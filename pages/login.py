import streamlit as st
import time
from datetime import datetime

# ページの設定
# st.set_page_config(page_title="Multi-Point-Mapper", layout="centered")

st.title("Multi-Point-Mapper")

st.write("Please enter your ID to launch the system.")

# 入力欄
user_id = st.text_input("UserID", placeholder="Ex: 1XXXXX")

if st.button("Login"):
    # 1. 未入力チェック
    if not user_id:
        st.error("Please enter your UserID.")

    # 2. 管理者ログイン
    elif "ADMIN_PASSWORD" in st.secrets and user_id == st.secrets["ADMIN_PASSWORD"]:
        st.success("Logging in as Administrator...")
        time.sleep(1.2)
        st.switch_page("pages/dashboard.py")

    # 3. ID形式チェック（1から始まる6桁）
    elif not (user_id.startswith("1") and len(user_id) == 6 and user_id.isdigit()):
        st.warning("Invalid ID. Please enter a 6-digit number starting with '1'.")

    # 4. 認証成功
    else:
        # ログを記録
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("./access_log.txt", "a", encoding="utf-8") as f:
                f.write(f"{now},{user_id},login\n")
        except Exception as e:
            st.error(f"ログの書き込みに失敗しました: {e}")

        st.session_state.user_id = user_id
        st.success("Authenticated! Launching the map system...")
        time.sleep(1.2)
        st.switch_page("pages/map_app.py")

st.markdown("---")
st.caption("Developed by Kohei Takahashi")
