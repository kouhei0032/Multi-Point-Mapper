import streamlit as st

# 1. ページの定義（ファイル名が正確に一致しているか確認してください）
login_page = st.Page("pages/login.py", title="login")
map_page = st.Page("pages/map_app.py", title="map_app")
admin_page = st.Page("pages/dashboard.py", title="dashboard")

# 2. ナビゲーションの設定（サイドバーを隠す）
pg = st.navigation([login_page, map_page,admin_page], position="hidden")

# 3. 実行
pg.run()