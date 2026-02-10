import os
import shutil
import pandas as pd
from e_crawler_market_coordinate import main as coordinate_main
from t_clean_market_time import process_market_time

# 檔案路徑設定
COORDINATE_OUTPUT_DIR = r".\Data_clean\Market_coordinates"
RAW_TIME_FILE = r".\Data_raw\Market_time.txt"
TIME_OUTPUT_DIR = r".\Data_clean\Market_time"
FINAL_OUTPUT_DIR = r".\Data_clean\Market_final"
ALL_FILE = os.path.join(FINAL_OUTPUT_DIR, "all_cities.csv")

def integrated_pipeline():
    clean_pycache()

    # 輸入縣市名稱
    city_name = input("請輸入縣市名稱（台或臺皆可）：").strip()
    city_name = city_name.replace("台", "臺")

    print(f"\n=== 步驟 1：查詢夜市座標（{city_name}） ===")
    coordinate_main(city_name)  # 會輸出 HTML

    print(f"\n=== 步驟 2：清理夜市營業時間（{city_name}） ===")
    process_market_time(RAW_TIME_FILE, TIME_OUTPUT_DIR, city_name)

    print("\n=== 步驟 3：合併並附加到總檔案 ===")
    append_to_all_csv(city_name)

    print("\n=== 步驟 4：刪除所有 HTML 檔並刪除 Market_coordinates 資料夾 ===")
    delete_html_and_folder()

    print("\n=== 清理中繼資料夾（保留最終檔案） ===")
    clean_intermediate_folders()

    print("\n✅ 整合流程完成！")
    print(f"總檔案位置：{ALL_FILE}")

# 刪除 __pycache__ 資料夾
def clean_pycache():
    project_root = r"C:\Data Engineer\Project\Traffic_accident_map_project"
    for root, dirs, files in os.walk(project_root):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                shutil.rmtree(os.path.join(root, dir_name))

# 刪除所有 HTML 檔並刪除 Market_coordinates 資料夾
def delete_html_and_folder():
    if os.path.exists(COORDINATE_OUTPUT_DIR):
        # 刪除 HTML 檔
        for f in os.listdir(COORDINATE_OUTPUT_DIR):
            if f.endswith(".html"):
                file_path = os.path.join(COORDINATE_OUTPUT_DIR, f)
                os.remove(file_path)
                print(f"✔ 已刪除 HTML 檔：{file_path}")
        # 刪除整個資料夾
        shutil.rmtree(COORDINATE_OUTPUT_DIR)
        print(f"✔ 已刪除資料夾：{COORDINATE_OUTPUT_DIR}")
    print("✔ HTML 檔與 Market_coordinates 資料夾已清理完成")

# 清理中繼資料夾
def clean_intermediate_folders():
    if os.path.exists(TIME_OUTPUT_DIR):
        shutil.rmtree(TIME_OUTPUT_DIR)
        print(f"✔ 已刪除資料夾：{TIME_OUTPUT_DIR}")
    print("✔ 中繼資料夾清理完成")

# 附加到總檔案
def append_to_all_csv(city_name):
    coord_files = [f for f in os.listdir(COORDINATE_OUTPUT_DIR) if f.endswith(".csv")]
    time_files = [f for f in os.listdir(TIME_OUTPUT_DIR) if f.endswith(".csv")]

    if not coord_files or not time_files:
        print("❌ 找不到輸出檔案，請確認前兩步是否成功執行")
        return

    coord_file = os.path.join(COORDINATE_OUTPUT_DIR, sorted(coord_files)[-1])
    time_file = os.path.join(TIME_OUTPUT_DIR, sorted(time_files)[-1])

    df_coord = pd.read_csv(coord_file)
    df_time = pd.read_csv(time_file)
    
    # 合併兩表，依 city + night_market 對應
    df_merged = pd.merge(df_time, df_coord, on=["city", "night_market"], how="left")

   # 重新編號 night_market_id
    df_merged["night_market_id"] = range(1, len(df_merged) + 1)

    # 固定欄位順序
    final_columns = [
        "night_market_id", "city", "night_market", "longitude", "latitude",
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "status"
    ]
    existing_cols = [col for col in final_columns if col in df_merged.columns]
    df_final = df_merged[existing_cols]

    os.makedirs(FINAL_OUTPUT_DIR, exist_ok=True)
    file_exists = os.path.isfile(ALL_FILE)
    existing_cities = set()
    if file_exists:
        existing_df = pd.read_csv(ALL_FILE)
        existing_cities = set(existing_df["city"].unique())

    if city_name in existing_cities:
        print(f"⚠ {city_name} 已存在於總檔案，跳過附加")
        return

    start_id = 1
    if file_exists:
        start_id = len(existing_df) + 1
    df_final["night_market_id"] = range(start_id, start_id + len(df_final))

    if not file_exists:
        df_final.to_csv(ALL_FILE, index=False, encoding="utf-8-sig")
    else:
        df_final.to_csv(ALL_FILE, mode="a", header=False, index=False, encoding="utf-8-sig")

    print(f"✅ 已附加 {len(df_final)} 筆資料到 {ALL_FILE}")

def main():
    integrated_pipeline()

if __name__ == "__main__":
    main()


# 【 t_clean_multiple_coordinate_time V1.1版 】

# / 程式要點

# 分批處理每個縣市的夜市資料（座標 + 營業時間）。
# 每次執行只處理一個縣市，並將結果附加到同一個總檔案 all_cities.csv。
# 避免重複寫入，確保資料整合完整。
# 支援：分批處理縣市，附加到同一個總檔案 all_cities.csv，並刪除所有 HTML 檔

# 核心流程
# 輸入縣市名稱
# 將「台」轉換成「臺」以保持一致性。
# 呼叫座標處理函式
# coordinate_main(city_name) → 來自 Seach_market_coordinate.py。
# 呼叫時間清理函式
# process_market_time(RAW_TIME_FILE, TIME_OUTPUT_DIR, city_name) → 來自 Pipeline_market_time.py。
# 合併兩個 CSV 並附加到總檔案
# 使用 pandas.merge()，依 city + night_market 對應。
# 固定欄位順序。
# 自動計算 night_market_id，根據現有筆數遞增。
# 檢查是否已存在該縣市，避免重複附加。
# 清理中繼資料
# 刪除 __pycache__。
# 刪除座標與時間的中繼檔案，保留總檔案。

# 附加模式設計
# 檢查 all_cities.csv 是否存在：
# 不存在 → 新增標題列。
# 存在 → 直接附加資料。
# 檢查是否已處理過該縣市 → 如果存在，跳過附加。
# 分批執行：適合大量縣市，避免一次跑完造成流程過長。
# 自動遞增 ID：根據現有筆數計算下一個 night_market_id。
# 避免重複寫入：檢查城市名稱是否已存在於總檔案。