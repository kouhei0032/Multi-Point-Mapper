import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ページ設定
# st.set_page_config(page_title="dashboard", layout="wide")
st.title("📊 Multi-Point-Mapper dashboard")

LOG_FILE = "access_log.txt"

# ログファイルの存在確認
if not os.path.exists(LOG_FILE):
    st.warning("Log file not found. No login history yet.")
    if st.button("⬅️ Return to login screen"):
        st.switch_page("main.py")

else:
    try:
        # データの読み込み
        df = pd.read_csv(
            LOG_FILE,
            names=["datetime", "user_id", "action"],
            header=None
        )

        # データ型の変換と加工
        df["datetime"] = pd.to_datetime(df["datetime"])
        df["date"] = df["datetime"].dt.date
        df["user_id"] = df["user_id"].astype(str)

        # データの表示
        st.subheader("📝 Latest Login History List")
        st.dataframe(
            df.sort_values("datetime", ascending=False),
            use_container_width=True
        )
        st.divider()

        # --- 可視化セクション ---
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📅 Daily login trends")
            # 日ごとの件数を集計
            daily_counts = df.groupby("date").size()
            st.line_chart(daily_counts)

        with col2:
            st.subheader("👤 Login TOP10")
            # 社員番号ごとの件数を集計
            user_counts = df["user_id"].value_counts().head(10)
            st.bar_chart(user_counts)

        # ナビゲーションとダウンロード
        st.divider()
        col_btn1, col_btn2, _ = st.columns([1, 1, 2])

        with col_btn1:
            if st.button("⬅️ Return to login screen", use_container_width=True):
                st.switch_page("pages/login.py")

        with col_btn2:
            # Excelで開いても文字化けしないように utf_8_sig でエンコード
            csv_data = df.to_csv(index=False).encode('utf_8_sig')
            st.download_button(
                label="📥 Download logs as CSV",
                data=csv_data,
                file_name=f"access_log_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

    except Exception as e:
        st.error(f"An error occurred while analyzing the data.: {e}")
        st.info("The log file format may be corrupted.")
        if st.button("⬅️ Return to login screen"):
            st.switch_page("pages/login.py")

st.caption("admin page")