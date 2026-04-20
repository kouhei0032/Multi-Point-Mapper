# ライブラリインポート ----------------------------------------
# 1. 標準ライブラリ（基本機能）
import time
import urllib.parse
import math
import traceback

# 2. 外部ライブラリ（通信・汎用）
import requests

# 3. Streamlit & 地図関連（アプリの核となる部分）
import streamlit as st
import folium
from streamlit_folium import st_folium

# ブラウザのタブ名、ファビコン等の情報設定
st.set_page_config(
    page_title="Multi-Point-Mapper",  # ここがブラウザのタブ名になります
    page_icon="📍", #ページアイコン
    layout="wide",
    initial_sidebar_state="expanded",  # 常に開いた状態で開始,
)

# memo -----------------------------------------------------
# lat:緯度
# lon:経度

# 国土地理院ベースのジオコーディング関数 ---------------------------
def get_lat_lon_geolonia(address):
    # 住所をURL用にエンコード UTF-8（スペースや漢字対策）
    encoded_address = urllib.parse.quote(address)
    url = f"https://msearch.gsi.go.jp/address-search/AddressSearch?q={encoded_address}"

    try:
        response = requests.get(url, timeout=10)  # サーバーが応答しない
        response.raise_for_status()  # ステータスコードが200以外なら例外を出す / URLが間違っている（404エラーなど）
        data = response.json()  # Pythonで扱えるデータ形式へ変更

        if data:
            # 座標を取得 (APIは [経度, 緯度] の順 → returnの時に 緯度,経度の順に修正)
            lon, lat = data[0]["geometry"]["coordinates"]
            return lat, lon
    except Exception as e:
        print(f"debug error: {e}")
        return None
    return None


# -----

# 経路取得関数 -----------------------------------------------
def get_osrm_route(points):
    if len(points) < 2:
        return None, 0, 0

    coords = ";".join([f"{p[1]},{p[0]}" for p in points])
    url = f"http://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson"

    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        if "routes" in data:
            route = data["routes"][0]
            geometry = route["geometry"]["coordinates"]
            distance = route["distance"]
            duration = route["duration"]

            path = [[p[1], p[0]] for p in geometry]
            return path, distance, duration
    except Exception as e:
        # サイドバーに分かりやすいメッセージを表示
        st.sidebar.error("Failed to retrieve data.")

        # 詳細なエラー内容は「詳細」として折りたたんで表示（親切設計）
        with st.sidebar.expander("Check error details"):
            st.code(traceback.format_exc())
            st.code(e)

    return None, 0, 0


# -----

# 訪問順序の最適化関数　近い順に次を訪問する（貪欲法） --------------
def optimize_route(locations):
    """
    1番目の地点をスタートとし、残りを『現在地から一番近い順』に並び替える（貪欲法）
    """
    if len(locations) <= 2:
        return locations

    unvisited = locations[:]  # コピーを作成
    optimized = [unvisited.pop(0)]  # 1番目をスタートとして固定

    while unvisited:
        # 現在地（optimizedの最後）
        current = optimized[-1]

        # 残りの中で最も近い地点を探す
        next_loc = min(
            unvisited,
            key=lambda x: math.sqrt((x['lat'] - current['lat']) ** 2 + (x['lon'] - current['lon']) ** 2)
        )

        optimized.append(next_loc)
        unvisited.remove(next_loc)

    return optimized


# -----


# CSSの指定 Streamlitではある程度スタイルが固定されているのでCSSで強制的にレイアウトを変えている
st.markdown("""
    <style>
    /* 1. アプリ全体・メインコンテナの余白を完全にゼロにする */
    .stApp, .main, .block-container {
        margin: 0 !important;
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* 2. メインコンテナを上に突き合わせる (ネガティブマージン) */
    .main .block-container {
        margin-top: -3.5rem !important; /* ツールバーとヘッダーの隙間を相殺 */
    }

    /* 3. ヘッダーとツールバーを完全に非表示（高さをゼロに） */
    [data-testid="stHeader"], 
    [data-testid="stAppToolbar"] {
        display: none !important;
        height: 0 !important;
    }

    /* 4. 要素間の隙間(gap)と各divのパディングを排除 */
    [data-testid="stVerticalBlock"],
    [data-testid="stVerticalBlock"] > div {
        gap: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* 5. 地図(iframe)を画面いっぱいに広げ、下部の隙間を消す */
    iframe {
        width: 100% !important;
        height: 100vh !important;
        display: block !important;
        border: none !important;
    }

    /* 6. フッターを非表示 */
    footer {
        visibility: hidden;
        height: 0;
    }

    /* 7. サイドバーを閉じるボタン（<<）を完全に非表示にする */
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }

    /* 8. ついでに、サイドバー上部の余計なパディングを詰めたい場合 */
    [data-testid="stSidebarNav"] {
        padding-top: 0rem !important;
    }


    /* サイドバーの幅を指定（例：400px） */
    [data-testid="stSidebar"] {
        width: 400px !important;
    }

    /* サイドバーを広げた分、メイン画面が重ならないように調整 */
    [data-testid="stSidebarContent"] {
        width: 400px !important;
    }

    /* サイドバーにあるテキストエリアの「入力文字」を調整 */
    [data-testid="stSidebar"] [data-testid="stTextArea"] textarea {
        font-size: 13px !important;  /* ここでサイズを自由に調整 */
        line-height: 1.4 !important; /* 行間を少し広げると読みやすくなります */
        color: #1f2937 !important;   /* 文字色を濃くして視認性をアップ */
        font-family: sans-serif !important; 
    }

    /* サイドバー上部のDIVを削除 */
    .st-emotion-cache-10p9htt.e9ic3ti4 {
        display: none !important;
    }

</style>
    """, unsafe_allow_html=True)

# 右メイン画面側のタイトル 不要なのでコメント化
# st.title("訪問ユーザマッピングシステム beta1.0")

# --- セッション状態の初期化 ---
# 検索した地点情報を保存する場所 /　初回実行時にセッションを作成する
if "locations" not in st.session_state:
    st.session_state.locations = []

if "selected_names" not in st.session_state:
    st.session_state.selected_names = []

if "p_names" not in st.session_state:
    st.session_state.p_names = ""

if "p_data" not in st.session_state:
    st.session_state.p_data = ""


# --- 2. クリアボタンの判定を先に持ってくる ---
# ウィジェットが表示される前に値を書き換えるのがStreamlitのルール
def clear_text():
    st.session_state.p_names = ""
    st.session_state.p_data = ""
    st.session_state.locations = []
    st.session_state.selected_names = []
    st.session_state.selected_office = "none"


# サイドバー
with st.sidebar:
    # --- サイドバー ---
    st.markdown("# <b>Multi-Point-Mapper</b><br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- 3. その後にテキストエリアを配置する ---
    paste_names = st.text_area(
        "User",
        height=150,
        placeholder="User...",
        key="p_names"  # セッション状態と連動
    )

    st.markdown("<br>", unsafe_allow_html=True)

    paste_data = st.text_area(
        "Address",
        height=150,
        placeholder="Address...",
        key="p_data"  # セッション状態と連動
    )

    # st.sidebar.write("*緯度経度の算出には国土地理院のAPIを利用")
    st.caption("*Latitude and longitude calculation: Using the Geospatial Information Authority of Japan's API.*")

    st.markdown("<br>", unsafe_allow_html=True)

    # サイドバーのどこか（住所入力欄の上など）に追加
    offices = {
        "none": "",
        "Sapporo": "北海道札幌市北区北6条西4丁目",
        "Sendai": "宮城県仙台市青葉区中央1丁目1-1",
        "Tokyo": "東京都千代田区丸の内1丁目9-1",
        "Osaka": "大阪府大阪市北区梅田3丁目1-1",
        "Kyushu": "福岡県福岡市博多区博多駅中央街1-1",
    }

    selected_office_name = st.selectbox("🏠 Select the starting point of the route.",
                                        list(offices.keys()),
                                        key="selected_office"
                                        )
    st.caption("*Do not output the route when picking up destinations.*")
    st.markdown("&nbsp;<br>", unsafe_allow_html=True)

    # 1. サイドバー内に2つのカラムを作成
    col1, col2 = st.columns([1, 2])
    # 2. それぞれのカラムにボタンを配置
    with col1:
        st.button("🗑️Clear", on_click=clear_text, use_container_width=True, type="secondary")

    with col2:
        run_button = st.button("📍plot", use_container_width=True)

    # --- ここに追加：プログレスバーとステータステキストの表示位置を固定 ---
    spacer_placeholder = st.empty()  # 実行時のみ空白を入れる枠
    progress_placeholder = st.empty()  # プログレスバー用の場所
    status_placeholder = st.empty()  # テキスト（処理中...）用の場所

    # ---　訪問先ピックアップ　---
    st.markdown("---")
    st.markdown("### 📋 Visited destination pick-up")
    selected = st.session_state.get("selected_names", [])

    if selected:
        # 1. 最初にクリックしたものがリストの先頭([0])にあり、
        #    enumerateはそれを No.1 として表示します。
        for i, name in enumerate(selected, start=1):
            st.write(f"No.{i} : {name}")

        st.sidebar.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️Clear list only", key="clear_list"):
            st.session_state.selected_names = []
            st.rerun()
    else:
        st.caption("Clicking on a marker on the map will display it here.")

    st.sidebar.markdown("---")
    st.markdown("### 📝 Recommended visit order")

    # 1. そもそも「経路出力しない」が選ばれている場合
    if selected_office_name == "none":
        st.caption("oute output is turned off.")

    # 2. 経路出力する設定だが、まだ地点がプロットされていない場合
    elif not st.session_state.locations:
        st.caption("When you plot the locations, the order will be displayed here.")

# --- ジオコーディング処理 ---
if run_button and paste_data:

    spacer_placeholder.markdown("&nbsp;<br>", unsafe_allow_html=True)

    # 事業所が選択されている場合のみ経路出力
    if selected_office_name != "none":
        office_address = offices[selected_office_name]
        addresses = [office_address] + [addr.strip() for addr in paste_data.split('\n') if addr.strip()]
        names = [selected_office_name] + [name.strip() for name in paste_names.split('\n') if name.strip()]
    else:
        addresses = [addr.strip() for addr in paste_data.split('\n') if addr.strip()]
        names = [name.strip() for name in paste_names.split('\n') if name.strip()]

    # デバッグ用のコード
    # st.write(paste_data.split('\n'))

    new_results = []

    # progress_bar = st.sidebar.progress(0) 新しく作ると下にできちゃうから削除
    # status_text = st.sidebar.empty() 新しく作ると下にできちゃうから削除

    for i, address in enumerate(addresses):

        # --- 住所のみでも処理できるように処理
        if i < len(names) and names[i] != "":
            user_name = names[i]
        else:
            user_name = f"No.{i + 1}: {address[:10]}..."
        # ------------------------------

        # user_name = names[i]

        status_placeholder.markdown(f"<br>{i + 1}/{len(addresses)} 件目を処理中... \n >{address}",
                                    unsafe_allow_html=True)
        # status_text.text(f"処理中: {address}")

        try:
            # 1回目：国土地理院API
            res = get_lat_lon_geolonia(address)
            lat, lon = None, None

            if res:
                lat, lon = res  # タプルを展開

            else:
                # 2回目：失敗した場合、「丁目」以降を削って再試行
                target = "丁目"
                if target in address:
                    idx = address.find(target)
                    short_addr = address[:idx + len(target)]
                    # status_text.text(f"再試行(丁目まで): {short_addr}")
                    status_placeholder.markdown(
                        f"<br>{i + 1}/{len(addresses)} 件目を \"再試行\" 処理中... \n >{address}",
                        unsafe_allow_html=True)
                    # 短い住所で再試行
                    time.sleep(1.1)
                    nom_res = get_lat_lon_geolonia(short_addr)
                    if nom_res:
                        lat, lon = nom_res

            if lat and lon:
                new_results.append({
                    "lat": lat,
                    "lon": lon,
                    "address": address,
                    "user_name": user_name
                })
            else:
                st.sidebar.warning(f"Search failed: {address}")

            time.sleep(0.6)  # 規約遵守
            progress_placeholder.progress((i + 1) / len(addresses))

        except Exception as e:
            st.sidebar.error(f"error: {address}")

    # 検索結果をセッションに保存
    st.session_state.locations = new_results

    # st.write("セッションの確認コード　----------------")
    # st.write(new_results)
    # time.sleep(5)

    # ここで並び替えを実行！
    if new_results:
        st.session_state.locations = optimize_route(new_results)
        st.sidebar.success(f"{len(st.session_state.locations)}Plotting complete! (Route optimized)")
    else:
        st.session_state.locations = []
        st.sidebar.warning("No plottable locations were found.")

    st.sidebar.markdown("&nbsp;<br>", unsafe_allow_html=True)
    time.sleep(1.5)

    # 強制再描画
    st.rerun()

# --- 地図の組み立て ---
# セッションにデータがあれば最初の地点、なければ札幌をセンターにする
if st.session_state.locations:
    # プロットした場合の緯度・経度を直接指定
    center_lat = st.session_state.locations[0]["lat"]
    center_lon = st.session_state.locations[0]["lon"]
    zoom_val = 10
else:
    # 初期状態での地図表示位置
    center_lat, center_lon = 35.681236, 139.767125
    zoom_val = 12

# デフォルト表示
# m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_val)

# デフォルト表示
m = folium.Map(location=[center_lat, center_lon],
               zoom_start=zoom_val,
               tiles='OpenStreetMap')

m.get_root().header.add_child(folium.Element("""
    <style>
        .leaflet-control-attribution {
            margin-bottom: 5px !important; /* ここで直接持ち上げる */
            background-color: rgba(255, 255, 255, 0.8) !important;
        }
    </style>
"""))

# ルートを青線で構築する -----------------------------------------------------------------------------
if selected_office_name != "none" and len(st.session_state.locations) >= 2:
    points = [[loc["lat"], loc["lon"]] for loc in st.session_state.locations]

    # ルート、距離(m)、時間(秒)を取得
    route_path, dist_m, duration_sec = get_osrm_route(points)

    if route_path:
        folium.PolyLine(route_path, color="#2A52BE", weight=6, opacity=0.8).add_to(m)

        # --- 時間予測のスクリプト ---
        # 秒を分に、メートルをキロに変換
        # duration_min = round(duration_sec * 1.3 / 60)  # 1.3は信号や渋滞を考慮
        # dist_km = round(dist_m / 1000, 1)

        # サイドバーに情報を表示
        with st.sidebar:

            # # 予測ボックス（既存）
            # st.markdown(f"""
            #             <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-top: 10px;">
            #                 <p style="margin:0; font-size:14px; color:#555;">📊 <b>ルート予測</b></p>
            #                 <p style="margin:0; font-size:20px; color:#1f2937;">
            #                     ⏱️ 約 <b>{duration_min}</b> 分
            #                     <span style="font-size:14px; margin-left:10px;">({dist_km} km)</span>
            #                 </p>
            #             </div>
            #         """, unsafe_allow_html=True)

            route_lines = []
            import re

            for i, loc in enumerate(st.session_state.locations):
                # 既存の番号を消して純粋な名前を取得
                clean_name = re.sub(r'^\d+\.\s*', '', loc['user_name'])

                if i == 0:
                    # 0番目（営業所）は旗のみ、数字なし
                    route_lines.append(f"🏠 {clean_name}")
                else:
                    # 1番目以降の顧客に「1.」「2.」と番号を振る
                    route_lines.append(f"{i}. {clean_name}")

            # リストを表示
            route_text = "  \n".join(route_lines)
            st.info(route_text)

# -------------------------------------------------------------------------------------------
st.sidebar.markdown("### 🔄 Route adjustment")

# 1. 「経路出力しない」が選ばれている場合
if selected_office_name == "none":
    st.sidebar.caption("Route output is turned off.")

# 2. 経路出力する設定だが、まだ地点がプロットされていない場合
elif not st.session_state.locations:
    st.sidebar.caption("You can edit the location once you've plotted it.")

# 3. 地点が存在し、かつ経路出力が有効な場合
else:
    # リストの全要素をループ
    for i in range(len(st.session_state.locations)):
        cols = st.sidebar.columns([0.6, 0.2, 0.2])
        loc = st.session_state.locations[i]

        # 名前を表示
        cols[0].write(f"{i}. {loc['user_name'][:10]}")

        # 「上へ」ボタン
        if i > 0:
            if cols[1].button("↑", key=f"up_{i}"):
                st.session_state.locations[i], st.session_state.locations[i - 1] = \
                    st.session_state.locations[i - 1], st.session_state.locations[i]
                st.rerun()

        # 「下へ」ボタン
        if i < len(st.session_state.locations) - 1:
            if cols[2].button("↓", key=f"down_{i}"):
                st.session_state.locations[i], st.session_state.locations[i + 1] = \
                    st.session_state.locations[i + 1], st.session_state.locations[i]
                st.rerun()
# -------------------------------------------------------------------------------------------

if len(st.session_state.locations) >= 2:
    # 住所をURL用に変換
    def format_addr(loc):
        # 緯度経度だと確実ですが、住所文字列でもGoogle側で再計算してくれます
        return f"{loc['lat']},{loc['lon']}"


    base_url = "https://www.google.com/maps/dir/?api=1"

    # 出発地 (0番目)
    origin = format_addr(st.session_state.locations[0])
    # 目的地 (最後)
    destination = format_addr(st.session_state.locations[-1])

    # 経由地 (1番目 〜 最後から2番目まで)
    if len(st.session_state.locations) > 2:
        waypoints = "|".join([format_addr(l) for l in st.session_state.locations[1:-1]])
        nav_url = f"{base_url}&origin={origin}&destination={destination}&waypoints={waypoints}&travelmode=driving"
    else:
        nav_url = f"{base_url}&origin={origin}&destination={destination}&travelmode=driving"

    st.sidebar.markdown(f"""
        <a href="{nav_url}" target="_blank" style="text-decoration: none;">
            <div style="
                background-color: #4285F4;
                color: white;
                padding: 12px;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                margin-top: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                📱 GoogleMapへ経路データ連携
            </div>
        </a>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------------------------------------

# セッションに保存されているすべての地点をプロット
for i, loc in enumerate(st.session_state.locations):
    popup = folium.Popup(loc["address"], max_width=300, min_width=150)

    # --- 色分けのロジック ---
    if selected_office_name != "経路出力しない" and i == 0:
        marker_color = "red"
        icon_type = "home"  # スタートは家マーク
    else:
        marker_color = "blue"
        icon_type = "map-marker"  # 標準

    folium.Marker(
        [loc["lat"], loc["lon"]],
        popup=popup,
        tooltip="社名: "+loc["user_name"]+"　<br>住所: "+loc["address"],
        # アイコン設定を追加。ここで変数を反映させます
        icon=folium.Icon(color=marker_color, icon=icon_type)
    ).add_to(m)

# --- 地図の表示 ---
# keyを動的に変えることで、データ更新時に強制的に描画を更新させる
st_data = st_folium(
    m,
    use_container_width=True,
    height=800,
    #key=f"map_{len(st.session_state.locations)}"
    key="main_map",  # 固定の文字列にする
    returned_objects=["last_object_clicked_tooltip"]  # クリック検知に必要なデータだけ受け取る
)

# クリック検知
# st_dataの中にクリックされたオブジェクトの情報（tooltipに設定した名前）が入ってくる
if st_data and st_data.get("last_object_clicked_tooltip"):
    clicked_name = st_data["last_object_clicked_tooltip"]

    # 重複して追加されないようにチェックしてリストに追加
    if clicked_name not in st.session_state.selected_names:
        st.session_state.selected_names.append(clicked_name)
        # リストが更新されたので再描画
        st.rerun()

# サイドバーの最後に出典情報を設定
with st.sidebar:
    st.markdown("---")  # 区切り線
    st.write("🔧App information")
    st.markdown(
        """
        This service utilizes map data from © <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors and 
        <a href="https://maps.gsi.go.jp/development/ichiran.html" target="_blank">Geospatial Information Authority of Japan</a>'s geocoding functionality.
        """,
        unsafe_allow_html=True
    )


