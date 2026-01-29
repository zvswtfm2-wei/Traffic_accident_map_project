import requests
import json
import folium
import csv
import os
import time
import difflib
from shapely.geometry import Point, Polygon

# Seach_market_coordinate V1.1版
# CSV輸出位置   C:\Data Engineer\Project\Traffic_accident_map_project\Data_clean\Market_coordinates
# Html輸出位置  C:\Data Engineer\Project\Traffic_accident_map_project\Data_clean\Market_coordinates

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NightMarketBot/1.0; +https://example.com)"
}

# 快取字典
osm_cache = {}
nominatim_cache = {}

# 夜市名單
night_markets_by_city = {
 # 北部
    "基隆市": ["廟口夜市", "八斗子夜市", "七堵夜市"],
    "臺北市": ["士林夜市", "華西街夜市", "艋舺夜市", "饒河街觀光夜市", "公館夜市", "南機場觀光夜市", "師大夜市", "臨江街觀光夜市", "寧夏夜市", "大龍街夜市", "延三夜市", "景美夜市", "雙城街夜市", "遼寧街夜市", "石牌夜市", "林口街夜市", "737夜市", "社子夜市"],
    "新北市": ["四腳亭吉安宮夜市", "樂華夜市", "湳雅夜市", "裕民夜市", "三和夜市", "中和興南夜市", "樹林興仁花園夜市", "樹林夜市", "新莊廟街夜市", "西盛夜市", "蘆洲廟口夜市", "淡水英專夜市", "淡水沙崙夜市", "集應廟夜市", "三芝夜市", "鶯歌夜市", "鶯歌龍鳳夜市", "林口夜市", "八里廖添丁廟夜市", "西雲路夜市", "御史路夜市", "金山夜市", "深坑慈聖夜市", "五股工業區夜市", "汐止觀光夜市", "汐止弘道街夜市", "汐止樟樹夜市", "長興街福德祠夜市", "貢寮澳底夜市"],
    "桃園市": ["南崁五福夜市", "大竹夜市", "桃園觀光夜市", "中壢觀光夜市", "中原夜市", "興仁花園夜市", "楊梅觀光夜市", "埔心後站夜市", "富岡夜市", "菓林夜市", "大園夜市", "大溪夜市", "新屋夜市", "草漯夜市", "新坡夜市", "觀音夜市", "復興夜市", "山腳夜市"],
    "新竹市": ["城隍廟夜市", "清大夜市", "樹林頭夜市", "後站夜市", "青草湖夜市", "內湖夜市", "中正台夜市"],
    "新竹縣": ["竹北夜市", "竹東沿河街夜市", "竹東二重埔夜市", "湖口夜市", "關西夜市", "新庄子夜市", "新豐夜市", "新埔夜市", "北埔夜市", "竹中夜市"],
    "宜蘭縣": ["羅東夜市", "東門觀光夜市", "員山夜市", "冬山夜市", "清溝夜市", "南方澳夜市", "頭城夜市", "南澳夜市", "三星夜市", "蘇澳夜市", "馬賽夜市", "礁溪溫泉夜市"],

    # 中部
    "苗栗縣": ["國泰夜市", "中港夜市", "建國路龍鳳夜市", "頭份建國夜市", "頭份尚順夜市", "苗栗英才觀光夜市", "公館夜市", "後龍夜市", "苑裡夜市", "苑裡29夜市", "大湖夜市", "銅鑼夜市", "三義夜市", "卓蘭夜市", "通霄夜市"],
    "臺中市": ["逢甲夜市", "一中商圈", "中華路夜市", "忠孝路夜市", "東海別墅夜市", "霧峰樹仁商圈", "豐原廟東夜市", "太平臺中小鎮夜市", "四張犁夜市", "捷運總站夜市", "潭子勝利夜市", "潭子頭家夜市", "大雅夜市", "葫蘆墩觀光夜市", "SOGO停車場夜市", "八方國際觀光夜市", "神岡夜市", "后里夜市", "外埔夜市", "東勢夜市", "旱溪夜市", "太平東平夜市", "大慶觀光夜市", "大里勝利大夜市", "大里塗城夜市", "大里文化街夜市", "亞洲大學夜市", "霧峰四德路夜市", "霧峰德泰街夜市", "大肚夜市", "大肚山龍井自強夜市", "龍井茄投夜市", "龍井龍津夜市", "福順宮夜市", "靜宜夜市", "梧棲夜市", "梧棲中港觀光夜市", "清水五權夜市", "沙鹿鹿峰夜市", "大甲夜市", "大甲蔣公路夜市"],
    "彰化縣": ["彰化中央陸橋夜市", "彰化精誠夜市", "彰化冠天夜市", "和美東發夜市", "和美美寮路夜市", "和美仁愛夜市", "鹿港鹿和夜市", "鹿港頂番夜市", "鹿港草港夜市", "福興夜市", "線西夜市", "伸港水尾夜市", "伸港福安宮夜市", "秀水夜市", "芬園社口夜市", "員林龍燈夜市", "員林大圓林觀光夜市", "員林林厝夜市", "社頭芭樂市場夜市", "永靖觀光夜市", "大村夜市", "花壇夜市", "田中夜市", "田中鐵支路觀光夜市", "田中高鐵夜市", "二水夜市", "田尾夜市", "田尾海豐崙夜市", "埤頭夜市", "埤頭星期四.六夜市", "北斗觀光夜市", "溪州夜市", "二林王子夜市", "二林金仔角觀光夜市", "埔鹽夜市", "埔鹽新水夜市", "埔鹽天盛夜市", "溪湖夜市", "溪湖忠溪夜市", "溪湖大公路夜市", "芳苑草湖夜市", "芳苑王功夜市", "竹塘夜市", "大城夜市", "埤頭星期三夜市"],
    "南投縣": ["草鞋墩人文觀光夜市", "國姓夜市", "南投市家樂福夜市", "南崗夜市", "中興新村內轆夜市", "南投祖祠路夜市", "中寮夜市", "松柏嶺夜市", "名間夜市", "鹿谷夜市", "竹山夜市", "集集夜市", "水裡夜市", "魚池夜市", "埔里城觀光夜市", "埔里樹人夜市"],
    "雲林縣": ["斗六觀光夜市", "斗六成功夜市", "斗六石榴班夜市", "大崙夜市", "虎尾夜市", "土庫夜市", "馬光夜市", "同仁夜市", "東南夜市", "吳厝夜市", "斗南夜市", "石龜夜市", "林內夜市", "古坑夜市", "大埤夜市", "莿桐夜市", "崙背夜市", "二崙夜市", "麥寮泰安宮夜市", "麥寮鎮南宮夜市", "褒忠夜市", "下崙夜市", "台西夜市", "崙豐夜市", "東勢夜市", "四湖夜市", "元長夜市"],

    # 南部
    "嘉義市": ["文化路夜市", "嘉樂福觀光夜市", "彌陀夜市", "湖美夜市"],
    "嘉義縣": ["新塭夜市", "布袋夜市", "大布袋夜市", "過溝夜市", "東石夜市", "蒜頭夜市", "義竹夜市", "鹿草夜市", "朴子夜市", "七主宮夜市", "後潭夜市", "新埤夜市", "麻魚寮夜市", "水牛厝夜市", "新港夜市", "民雄夜市", "頭橋夜市", "溪口夜市", "大林夜市", "大埔美夜市", "竹崎夜市", "梅山夜市", "水上夜市", "中庄夜市", "汴頭夜市", "同仁夜市", "番路夜市"],
    "臺南市": ["花園夜市", "大東夜市", "武聖夜市", "小北觀光夜市", "小北成功夜市", "仁和夜市", "灣裡夜市", "新永華夜市", "十二佃夜市", "本淵寮夜市", "中州寮夜市", "土城聖母廟夜市", "國宅夜市", "樺谷夜市", "新同安夜市", "永大夜市", "南工小夜市", "鹽行夜市", "中興里夜市", "復華夜市", "聖龍夜市", "大灣夜市", "鍾厝夜市", "德南夜市", "太子廟夜市", "大潭夜市", "歸仁星期三夜市", "歸仁星期四夜市", "關廟夜市", "新市夜市", "善化夜市", "新化夜市", "民生夜市", "隆田夜市", "六甲夜市", "下營夜市", "中營夜市", "麻豆夜市", "西港夜市", "安定夜市", "海寮夜市", "佳里夜市", "安西夜市", "仁愛夜市", "玉井夜市", "山上夜市", "大內夜市", "漚汪夜市", "學甲夜市", "蚵寮夜市", "北門夜市", "三寮灣夜市", "新營中華路夜市", "新進夜市", "鹽水夜市", "長安夜市", "白河夜市", "白河中正夜市", "柳營夜市", "小腳腿夜市", "果毅後夜市", "東山夜市", "龍山夜市", "南化夜市", "楠西夜市"],
    "高雄市": ["六合觀光夜市", "南華夜市", "瑞豐夜市", "前鎮夜市", "佛公夜市", "光華夜市", "德昌夜市", "崗山南夜市", "漢民夜市", "二苓夜市", "桂林夜市", "鋼平夜市", "高松夜市", "苓雅夜市", "忠孝夜市", "興中夜市", "三民街夜市", "吉林夜市", "喜峰街夜市", "駁二夜市", "內惟夜市", "鳳山中山路夜市", "中華街夜市", "牛潮埔夜市", "鳳山青年夜市", "五甲夜市", "海洋夜市", "大明夜市", "開漳聖王廟夜市", "南光街夜市", "國光路夜市", "南江街夜市", "會社88夜市", "翁公園迷你小夜市", "林園夜市", "鳥松夜市", "仁武夜市", "仁雄夜市", "後勁夜市", "楠都夜市", "土庫夜市", "大社夜市", "旗山夜市", "美濃夜市", "橋頭星期一夜市", "橋頭星期六夜市", "橋頭菁埔廣場夜市", "五里林夜市", "九甲圍夜市", "蚵仔寮海邊夜市", "智蚵夜市", "燕巢夜市", "岡山中山夜市", "岡山後紅夜市", "路竹夜市", "湖內大廟夜市", "湖內大湖夜市", "永安夜市", "阿蓮夜市", "茄萣夜市", "大樹夜市", "九曲堂週二夜市", "九曲堂週六夜市"],
    "屏東縣": ["屏東民族路夜市", "墾丁大街", "恆春夜市", "潮州夜市", "愛國夜市", "萬丹夜市", "社皮夜市", "新庄夜市", "新園夜市", "新東夜市", "烏龍夜市", "高樹夜市", "東港夜市", "繁華夜市", "林邊夜市", "南州夜市", "水底寮夜市", "里港夜市", "石光見夜市", "鹽埔夜市", "新圍夜市", "長治夜市", "九如夜市", "西勢夜市", "水門夜市", "隘寮夜市", "龍泉夜市", "老埤夜市", "楓港夜市", "佳佐夜市", "餉潭夜市", "七佳夜市", "望嘉夜市"],

    # 東部
    "花蓮縣": ["花蓮東大門國際觀光夜市", "崇德夜市", "太魯閣夜市", "新城夜市", "北埔廟口夜市", "北埔夜市", "美崙夜市", "太昌夜市", "南埔夜市", "志學夜市", "壽豐夜市", "林榮夜市", "鳳林夜市", "光復夜市", "富源夜市", "瑞穗夜市", "玉里夜市", "富里夜市"],
    "臺東縣": ["臺東觀光夜市", "知本夜市", "四維夜市", "太平夜市", "太麻里觀光夜市", "金崙夜市", "大武夜市", "池上夜市", "關山夜市", "長濱夜市", "桃源夜市", "新港夜市", "東清夜市"],

    # 離島
    "澎湖縣": ["西文祖師廟夜市", "北甲宮夜市", "馬公夜市"],
    "金門縣": ["金門體育館夜市", "金門救國團夜市"],
    "連江縣": ["南竿馬港觀光夜市"]
}

# 將「台」轉換成「臺」並去除空白
def normalize_city_name(city_name):
    return city_name.strip().replace("台", "臺")

# 模糊比對夜市名稱
def find_closest_name(target_name, all_names):
    matches = difflib.get_close_matches(target_name, all_names, n=1, cutoff=0.6)
    return matches[0] if matches else None

# 抓取該縣市所有 OSM 夜市名稱（快取）
def get_osm_names_by_city(city_name):
    if city_name in osm_cache:
        return osm_cache[city_name]
    query = f"""
    [out:json][timeout:60];
    (
      node["name"~"夜市"]["addr:city"~"{city_name}"];
      way["name"~"夜市"]["addr:city"~"{city_name}"];
      relation["name"~"夜市"]["addr:city"~"{city_name}"];
    );
    out tags;
    """
    url = "https://overpass.kumi.systems/api/interpreter"
    try:
        response = requests.post(url, data={'data': query}, headers=HEADERS, timeout=60)
        response.raise_for_status()
        data = response.json()
        names = [el['tags']['name'] for el in data.get('elements', []) if 'tags' in el and 'name' in el['tags']]
        osm_cache[city_name] = names
        return names
    except:
        return []

# 查詢夜市座標（OSM，快取）
def fetch_night_market_by_name(night_market_name):
    if night_market_name in osm_cache:
        return osm_cache[night_market_name]
    query = f"""
    [out:json][timeout:60];
    (
      node["name"="{night_market_name}"];
      way["name"="{night_market_name}"];
      relation["name"="{night_market_name}"];
    );
    out geom;
    """
    url = "https://overpass.kumi.systems/api/interpreter"
    try:
        response = requests.post(url, data={'data': query}, headers=HEADERS, timeout=60)
        if response.status_code != 200:
            return None
        data = response.json()
        if not data.get('elements'):
            return None
        coords = []
        for element in data['elements']:
            if 'geometry' in element:
                coords = [(point['lon'], point['lat']) for point in element['geometry']]
                break
        osm_cache[night_market_name] = coords
        return coords
    except:
        return None

# Nominatim API 查詢座標（快取）
def fetch_coords_from_nominatim(night_market_name, city_name):
    key = f"{city_name}_{night_market_name}"
    if key in nominatim_cache:
        return nominatim_cache[key]
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{night_market_name} {city_name}",
        "format": "json",
        "addressdetails": 1,
        "limit": 1
    }
    try:
        response = requests.get(url, params=params, headers={"User-Agent": "NightMarketBot"})
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            coords = [(lon, lat)]
            nominatim_cache[key] = coords
            return coords
        else:
            return None
    except:
        return None

# 修正：座標不足時直接使用單一定位點
def generate_grid_in_polygon(coords, spacing=100):
    if len(coords) < 4:
        print("⚠ 座標不足，將使用單一定位點")
        return coords
    polygon = Polygon(coords)
    min_lon = min(lon for lon, lat in coords)
    max_lon = max(lon for lon, lat in coords)
    min_lat = min(lat for lon, lat in coords)
    max_lat = max(lat for lon, lat in coords)
    lon_step = spacing / 111000
    lat_step = spacing / 111000
    grid_points = []
    lat = min_lat
    while lat <= max_lat:
        lon = min_lon
        while lon <= max_lon:
            point = Point(lon, lat)
            if polygon.contains(point):
                grid_points.append((lon, lat))
            lon += lon_step
        lat += lat_step
    if not grid_points:
        centroid = polygon.centroid
        grid_points.append((centroid.x, centroid.y))
    return grid_points

# 顯示地圖
def show_map(coords, grid_points, night_market_name):
    center_lat = sum(lat for _, lat in coords) / len(coords)
    center_lon = sum(lon for lon, _ in coords) / len(coords)
    m = folium.Map(location=[center_lat, center_lon], zoom_start=17)
    if len(coords) >= 4:
        folium.Polygon(locations=[(lat, lon) for lon, lat in coords],
                       color="red", fill=True, fill_opacity=0.4,
                       popup=night_market_name).add_to(m)
    else:
        folium.Marker(location=[coords[0][1], coords[0][0]],
                      popup=f"{night_market_name} (單一定位點)",
                      icon=folium.Icon(color="blue", icon="info-sign")).add_to(m)
    for lon, lat in grid_points:
        folium.CircleMarker(location=[lat, lon], radius=2, color="blue").add_to(m)

    html_output_dir = r"C:\Data Engineer\Project\Traffic_accident_map_project\Data_clean\Market_coordinates"
    os.makedirs(html_output_dir, exist_ok=True)
    m.save(os.path.join(html_output_dir, f"{night_market_name}_map.html"))

# 修改後的 main()：支援傳入 city_name
def main(city_name=None):
    if city_name is None:
        city_name = input("請輸入縣市名稱（台或臺皆可）：")
    city_name = normalize_city_name(city_name)

    if city_name in night_markets_by_city:
        night_markets = night_markets_by_city[city_name]
        print(f"開始查詢 {city_name} 共 {len(night_markets)} 個夜市...")
        osm_names = get_osm_names_by_city(city_name)
        night_market_coords = {}
        for night_market in night_markets:
            coords = fetch_night_market_by_name(night_market)
            if not coords:
                print(f"⚠ 找不到 {night_market}，嘗試模糊比對...")
                closest_name = find_closest_name(night_market, osm_names)
                if closest_name:
                    print(f"✔ 最接近的名稱：{closest_name}，重新查詢...")
                    coords = fetch_night_market_by_name(closest_name)
            if not coords:
                print(f"⚠ OSM 無資料，改用 Nominatim 查詢 {night_market}...")
                coords = fetch_coords_from_nominatim(night_market, city_name)
                if coords:
                    print(f"✔ Nominatim 找到座標：{coords}")
                else:
                    print(f"❌ Nominatim 也找不到 {night_market}")
            if coords:
                print(f"{night_market} 座標共 {len(coords)} 點")
                grid_points = generate_grid_in_polygon(coords)
                lons = [str(lon) for lon, lat in grid_points]
                lats = [str(lat) for lon, lat in grid_points]
                night_market_coords[night_market] = {
                    "city": city_name,
                    "longitude": ",".join(lons),
                    "latitude": ",".join(lats)
                }
                show_map(coords, grid_points, night_market)

        #  輸出 CSV：新增 night_market_id
        output_dir = r"C:\Data Engineer\Project\Traffic_accident_map_project\Data_clean\Market_coordinates"
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"all_{city_name}.csv")
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["night_market_id", "city", "night_market", "longitude", "latitude"])
            for idx, (night_market, data) in enumerate(night_market_coords.items(), start=1):
                writer.writerow([idx, data["city"], night_market, data["longitude"], data["latitude"]])
        print(f"✅ 已輸出 {len(night_market_coords)} 筆夜市座標到 {filename}")
    else:
        print("⚠ 找不到該縣市資料，請確認輸入是否正確")

if __name__ == "__main__":
    main()


# 程式要點

# 主要功能
# 根據使用者輸入的縣市名稱，查詢該縣市所有夜市。
# 透過 Overpass API 取得夜市的座標範圍。
# 在夜市範圍內生成每隔 100 公尺的網格點。
# 保證至少一個座標：如果網格為空 → 加入 Polygon 中心點。
# 將網格點輸出成 CSV 檔，並用 Folium 生成地圖 HTML。
# 輸出 CSV：每個夜市一列，經緯度分開欄位，且多個座標用逗號分隔
# 新增一個縣市總檔案：將同縣市所有夜市的網格點合併，並在 CSV 中加上夜市名稱欄位。
# 新增快取機制： OSM 查詢結果快取, Nominatim 查詢結果快取
# 快取儲存在記憶體

# 核心模組
# requests：呼叫 Overpass API。
# json：解析 API 回傳資料。
# folium：生成互動地圖。
# csv：輸出座標檔案。
# shapely：判斷點是否在多邊形內。

# 主要流程
# 輸入縣市 → 正規化名稱 → 查詢夜市清單 → 逐一處理夜市
# 模糊比對夜市名稱：使用 difflib.get_close_matches，找最接近的名稱。
# 如果找到相似名稱 → 顯示「最接近的名稱」並查詢座標。
# 如果完全找不到 → 顯示「OSM 無此夜市」。
# Nominatim 補座標（免費）
# 自動補救 Polygon 錯誤（座標不足時建立虛擬矩形）
# 呼叫 API 取得座標。
# 生成網格點。
# 輸出 CSV。
# 生成地圖 HTML。

# 錯誤處理
# API 呼叫失敗或非 JSON 回應 → 重試機制。
# 找不到夜市 → 顯示警告訊息。
# 網路錯誤 → 捕捉例外並重試。

# 易錯點與注意事項
# 座標順序
# Overpass API 回傳 (lon, lat)，Folium 需要 (lat, lon)，程式中有轉換，但要小心一致性。
# 多邊形判斷
# Polygon(coords) 使用的是 (lon, lat)，若順序錯誤會導致判斷失敗。
# 網格間距換算
# spacing / 111000 是近似值，適用於台灣，但在高緯度地區誤差會變大。

# API 限制
# Overpass API 容易超時或回傳空資料，需確保重試機制有效。
# 檔案路徑
# os.makedirs(os.path.dirname(filename), exist_ok=True) 若 filename 沒有資料夾層，可能出錯。
# 大量夜市處理
# 單執行緒逐一處理，若夜市數量多，執行時間會很長，可考慮多執行緒或非同步。
# 地圖檔案命名
# night_market_name 若含特殊字元，可能導致檔案命名錯誤。
# 城市名稱正規化
# 僅處理「台」→「臺」，其他錯字或簡繁體未處理，可能導致查詢失敗。