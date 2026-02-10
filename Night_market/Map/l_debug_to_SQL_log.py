import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import traceback
import pymysql
import logging

# ======================================================
# ★ 設定錯誤 Log (全域只需設定一次)
# ======================================================
logging.basicConfig(
    filename="error_log.txt",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ======================================================
# ★ 統一錯誤處理函式（已大幅精簡終端機輸出）
# ======================================================
def handle_error(e):
    """
    - 終端機印出精簡錯誤
    - 完整 traceback 與錯誤內容寫入 error_log.txt
    """

    err_type = e.__class__.__name__

    # 終端機只顯示錯誤類型（避免印出 e 裡巨大內容）
    print(f"❌ 發生錯誤（{err_type}）")
    print("🔍 詳細錯誤請查看 error_log.txt")

    # 完整寫入 log
    logging.error("【%s】 %s", err_type, str(e))
    logging.error("Traceback:\n%s", traceback.format_exc())


# ======================================================
# ★ 讀取環境變數
# ======================================================
load_dotenv()
username = os.getenv("Local_username")
password = os.getenv("Local_password")
server   = "localhost"
port     = 3306
database = "Night_market"

# 建立資料庫連線
conn_str = f"mysql+pymysql://{username}:{password}@{server}:{port}/{database}?charset=utf8mb4"
engine = create_engine(conn_str)

# ======================================================
# ★ 自動檢查資料品質
# ======================================================
def check_data_quality(df):
    dupes = df[df.duplicated(subset=['nightmarket_id', 'nightmarket_weekday'], keep=False)]
    if not dupes.empty:
        print("❗ 重複主鍵資料（nightmarket_id + nightmarket_weekday）：")
        print(dupes[['nightmarket_id', 'nightmarket_weekday', 'nightmarket_name']])

    print("nightmarket_url max len:", df['nightmarket_url'].astype(str).str.len().max())
    print("nightmarket_name max len:", df['nightmarket_name'].astype(str).str.len().max())
    print("nightmarket_area_road max len:", df['nightmarket_area_road'].astype(str).str.len().max())
    print("nightmarket_zipcode_name max len:", df['nightmarket_zipcode_name'].astype(str).str.len().max())

    bad_open = df[~df['nightmarket_open'].astype(str).str.match(r'^\d{2}:\d{2}$', na=False)]
    bad_close = df[~df['nightmarket_close'].astype(str).str.match(r'^\d{2}:\d{2}$', na=False)]

    if not bad_open.empty:
        print("❗ nightmarket_open 格式異常：")
        print(bad_open[['nightmarket_id', 'nightmarket_weekday', 'nightmarket_open']])

    if not bad_close.empty:
        print("❗ nightmarket_close 格式異常：")
        print(bad_close[['nightmarket_id', 'nightmarket_weekday', 'nightmarket_close']])

    print("資料檢查完畢。")


# ======================================================
# ★ 讀取 CSV
# ======================================================
def load_csv():
    csv_path = r".\Data_clean\nightmarket_clean.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"找不到 CSV 檔案：{csv_path}")

    df = pd.read_csv(csv_path, encoding="utf-8-sig", dtype={
        'nightmarket_id': str,
        'nightmarket_weekday': str
    })

    df = df.dropna(how='all')
    df = df.dropna(subset=['nightmarket_id'])
    return df

# ======================================================
# ★ 建立 SQL Schema
# ======================================================
def create_schema():
    create_sql = """
    CREATE TABLE IF NOT EXISTS Night_market_separate (
        nightmarket_id              VARCHAR(20) NOT NULL,
        nightmarket_name            VARCHAR(30),
        nightmarket_latitude        DECIMAL(15,4),
        nightmarket_longitude       DECIMAL(15,4),
        nightmarket_area_road       VARCHAR(30),
        nightmarket_zipcode         VARCHAR(10),
        nightmarket_zipcode_name    VARCHAR(10),
        nightmarket_rating          FLOAT,
        nightmarket_region          VARCHAR(10),
        nightmarket_city            VARCHAR(10),
        nightmarket_open            TIME,
        nightmarket_close           TIME,
        nightmarket_weekday         VARCHAR(10) NOT NULL,
        nightmarket_url             VARCHAR(500),
        nightmarket_northeast_latitude   DECIMAL(15,4),
        nightmarket_northeast_longitude  DECIMAL(15,4),
        nightmarket_southwest_latitude   DECIMAL(15,4),
        nightmarket_southwest_longitude  DECIMAL(15,4)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    with engine.connect() as conn:
        conn.execute(text(create_sql))
        conn.commit()


# ======================================================
# ★ 主程式
# ======================================================
def main():
    try:
        df = load_csv()
        check_data_quality(df)
        create_schema()

        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE Night_market_separate"))
            conn.commit()

        numeric_cols = [
            'nightmarket_latitude', 'nightmarket_longitude',
            'nightmarket_northeast_latitude', 'nightmarket_northeast_longitude',
            'nightmarket_southwest_latitude', 'nightmarket_southwest_longitude',
            'nightmarket_rating'
        ]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df['nightmarket_open'] = pd.to_datetime(df['nightmarket_open'], format='%H:%M', errors='coerce').dt.time
        df['nightmarket_close'] = pd.to_datetime(df['nightmarket_close'], format='%H:%M', errors='coerce').dt.time

        columns_in_db = [
            'nightmarket_id', 'nightmarket_name', 'nightmarket_latitude', 'nightmarket_longitude',
            'nightmarket_area_road', 'nightmarket_zipcode', 'nightmarket_zipcode_name',
            'nightmarket_rating', 'nightmarket_region', 'nightmarket_city',
            'nightmarket_open', 'nightmarket_close', 'nightmarket_weekday', 'nightmarket_url',
            'nightmarket_northeast_latitude', 'nightmarket_northeast_longitude',
            'nightmarket_southwest_latitude', 'nightmarket_southwest_longitude'
        ]
        df = df[columns_in_db]

        df.to_sql(
            name="Night_market_separate",
            con=engine,
            if_exists="append",
            index=False,
            method='multi',
            chunksize=500
        )

        print("Night_market_separate 表格資料新增完成")

    except Exception as e:
        handle_error(e)   # ★ 使用統一錯誤處理


if __name__ == "__main__":
    main()


# 【 l_debug_to_SQL_log V1.1版 】

# / 程式功能

# 讀取清洗後的夜市資料 CSV
# 自動檢查資料品質（欄位長度、時間格式、重複主鍵等）
# 建立 MySQL 資料表 Schema（若不存在）
# 清空舊資料並寫入新的資料
# 統一處理例外錯誤並記錄到 log

# / 功能要點說明
# 1. 全域錯誤 Log 系統
# 設定 logging 寫入 error_log.txt
# 建立 handle_error() 用來：
# 終端機只顯示錯誤類型
# 完整錯誤＋traceback 寫入 log（方便除錯）
# 避免終端機大量輸出，錯誤紀錄集中管理