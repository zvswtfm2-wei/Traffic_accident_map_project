
import os
import pandas as pd

# 資料來源位置 C:\Data Engineer\Project\Traffic_accident_map_project\Data_raw\Market_time.txt
# CSV輸出位置 C:\Data Engineer\Project\Traffic_accident_map_project\Data_clean\Market_time

def process_market_time(input_file, output_dir, user_input=None):
    # 縣市清單
    cities = ["基隆市","臺北市","新北市","桃園市","新竹市","新竹縣","宜蘭縣","苗栗縣","臺中市","彰化縣","南投縣","雲林縣","嘉義市","嘉義縣","臺南市","高雄市","屏東縣","花蓮縣","臺東縣","澎湖縣","金門縣","連江縣"]
    # 星期欄位
    week_days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

    # 如果 Pipeline 傳入 user_input，直接使用；否則互動輸入
    if user_input is None:
        user_input = input("請輸入縣市名稱（或輸入 '全部'）：").strip()
        user_input = user_input.replace("台", "臺")  # 將「台」轉換成「臺」

    # 建立輸出資料夾
    os.makedirs(output_dir, exist_ok=True)

    # 讀取檔案
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 動態設定輸出檔名
    if user_input == "全部":
        file_name = "Market_time_clean_全台.csv"
    else:
        file_name = f"Market_time_clean_{user_input}.csv"

    output_file = os.path.join(output_dir, file_name)

    # 初始化
    data = []
    pk = 1
    current_city = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 判斷是否為縣市
        if line in cities:
            current_city = line
            continue

        # 如果使用者有指定縣市，且不符合，則跳過
        if user_input != "全部" and current_city != user_input:
            continue

        # 處理夜市資料
        parts = line.split()
        name = parts[0]
        info_parts = parts[1:]  # 營業資訊拆分
        info_text = " ".join(info_parts)

        # 初始化欄位
        row = {
            "night_market_id": pk,
            "city": current_city,
            "night_market": name,
            "Monday": "",
            "Tuesday": "",
            "Wednesday": "",
            "Thursday": "",
            "Friday": "",
            "Saturday": "",
            "Sunday": "",
            "status": ""
        }

        # 檢查是否有「不定期」或「停止營業」
        if "不定期" in info_text or "停止營業" in info_text:
            row["status"] = info_text
        else:
            # 第一階段：處理「每週」規則
            for part in info_parts:
                if part.startswith("每週"):
                    for k, v in {"一":"Monday","二":"Tuesday","三":"Wednesday","四":"Thursday","五":"Friday","六":"Saturday","日":"Sunday","天":"Sunday"}.items():
                        if k in part:
                            time = info_parts[-1]
                            if row[v] == "":
                                row[v] = time

            # 第二階段：處理「每日」及時間
            if "每日" in info_text:
                split_parts = info_text.split()
                if "每日" in split_parts:
                    idx = split_parts.index("每日")
                    if idx + 1 < len(split_parts):
                        time = split_parts[idx + 1]
                        for day in week_days:
                            if row[day] == "":
                                row[day] = time

        data.append(row)
        pk += 1

    # 轉成 DataFrame 並輸出 CSV
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"✅ 清理完成，檔案已儲存至：{output_file}")

def main():
    input_file = r"C:\Data Engineer\Project\Traffic_accident_map_project\Data\Data_raw\Market_time.txt"
    output_dir = r"C:\Data Engineer\Project\Traffic_accident_map_project\Data\Data_clean\Market_time"

    # 如果單獨執行，互動輸入
    user_input = input("請輸入縣市名稱（或輸入 '全部'）：").strip()
    user_input = user_input.replace("台", "臺")

    process_market_time(input_file, output_dir, user_input)

if __name__ == "__main__":
    main()


# 【 t_clean_market_time V1.1版 】

# / 程式碼要點

# 檔案讀取與輸出設定
# 從 Market_time.txt 讀取原始資料。
# 輸出清理後的資料到 Market_time_clean.csv，並確保輸出資料夾存在。

# 縣市清單與星期欄位
# 預先定義台灣縣市清單，用來判斷每筆資料屬於哪個縣市。
# 定義星期欄位（Monday ~ Sunday）以存放營業時間。

# 使用者輸入篩選
# 使用 input() 讓使用者輸入縣市名稱或「全部」。
# 自動將「台」轉換成「臺」，確保輸入與縣市清單一致。
# 如果輸入「全部」，輸出所有資料；如果輸入縣市名稱，只輸出該縣市資料。

# 資料解析與清理
# 逐行讀取檔案，判斷是否為縣市名稱，並記錄當前縣市。
# 對夜市資料進行拆解，解析營業資訊。
# 初始化欄位：PK（流水號）、City、NightMarket、星期欄位、Status。

# 營業時間處理邏輯
# 如果營業資訊包含「不定期」或「停止營業」，將資訊放入 Status 欄位。
# 處理「每週」規則：依據中文數字對應星期，填入時間。
# 處理「每日」規則：將時間填入所有星期欄位。

# 輸出結果
# 將整理好的資料轉換成 DataFrame。
# 輸出成 CSV 檔案（UTF-8 BOM 格式），不在終端機印出資料，只顯示檔案路徑。