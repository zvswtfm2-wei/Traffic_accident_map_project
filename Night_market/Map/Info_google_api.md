/ 功能 1  - Google API

【 夜市地圖所需欄位 】
(1) 夜市名 (2) 星等 (3) 地址 (4)營業時間 (5)地址 (6) 夜市連結 (7) 夜市Wiki

說明 :
抓取台灣夜市資料的計費方式，並不是按欄位（名稱、星等、地址、營業時間）逐項收費，而是按「次」請求計費。不過，單次請求的「單價」會根據你索取的資料欄位屬於哪種 SKU（定價層級） 而有所不同。

1. 計費邏輯：看你用了哪些「欄位」
當你呼叫 Place Details（地點詳情）API 時，收費取決於你請求的欄位組合。系統會根據最高階的那個欄位來決定這整次請求的價格： 
基本資訊 (Basic)： 包含 名稱、地址。
專業資訊 (Pro)： 包含 星等 (Rating)、評價總數、商家目前狀態。
企業資訊 (Enterprise)： 包含 營業時間 (Opening Hours)、價格等級。 
結論： 如果你一次抓「名稱、地址、星等、營業時間」，這算 1 次請求，但會以較貴的 Enterprise（企業服務） 級別計費。 

2. 預估費用（每 1,000 次請求）
只抓名稱 + 地址 (Essentials/Basic)：約 $0 (2025年新制下，每月前 10,000 次免費)。
抓名稱 + 地址 + 星等 (Pro)：約 $5.10 (每月前 5,000 次免費)。
全抓（含營業時間）(Enterprise)：約 $17.00 - $25.00。 

3. 如何省錢？
欄位遮罩 (Field Mask)：在程式碼中明確指定 fields: ['displayName', 'formattedAddress', 'rating', 'regularOpeningHours']。如果你不指定，Google 會預設傳回「所有資料」並按最高價格收費。
快取 (Caching)：對於像地址或夜市名稱這類不太會變動的資料，Google 許可短暫快取（通常建議 30 天內），避免重複抓取同一家夜市而產生多次費用。
善用免費額度：從 2025 年 3 月起，不同等級的 SKU 都有各自的免費上限（例如 Pro 等級每月前 5,000 次免費），這對小規模抓取非常有利。

/* Google Maps Platform 新制計費
從 2025 年 3 月 1 日起，Google Maps Platform 已正式全面施行「新制計費」，最大的改變就是取消了過去「每月統一贈送 200 美元抵免額」的作法。 
現在的計費方式改為「依據功能等級，贈送固定的免費次數」。以下為 2026 年適用的新制核心邏輯： 取消 $200 抵免額，改為「分級免費次數」
以前不論你用什麼 API，通通從 200 美元扣；現在是把 API 分成 Essentials（基礎）、Pro（專業）、Enterprise（企業） 三大類，每一類獨立計算免費額度： 

類別 (SKU Tier) 	每月免費次數 (Free Tier)	常見功能 (以 Places API 為例)
Essentials	        10,000 次	               地點名稱、地點 ID、地址
Pro	                5,000 次	               星等 (Rating)、評論總數、營業狀態
Enterprise	        1,000 次	               詳細營業時間、評論內容、價格等級

/* 計費邏輯
1. 預估夜市數量與請求次數
全台夜市估計：目前登記在案與知名的夜市約為 300 至 500 個。
請求次數：若您已有清單，僅需抓取詳細資訊（Details），則為 500 次請求。若需先搜尋（Search）再抓詳情，則約為 1,000 次請求。
2. 資料欄位與收費等級 (SKU)
您需要的欄位跨越了三個等級，系統會按 最高等級 計費： 
夜市名、地址：屬於 Essentials 等級（基礎）。
星等 (Rating)：屬於 Pro 等級（專業）。
營業時間：屬於 Enterprise 等級（企業）。
結論：因為包含「營業時間」，這整筆請求會被歸類為 Enterprise SKU。 
3. 2025 新制下的預估錢數
從 2025 年 3 月 1 日起，Google 取消了統一的 $200 美元抵免額，改為針對不同 SKU 提供免費使用上限： 費用項目 	價格 (每 1,000 次)	每月免費額度 (新制)	500 個夜市的預估費用 Enterprise SKU	約 $25.00	前 1,000 次免費	$0 元
4. 連續查詢
Google Maps API 沒有「重複查詢不計費」的機制。即便你在一秒鐘內連續查詢兩次同一個夜市，Google 依然會將其視為兩次獨立的 API 呼叫並重複扣款。 

/* Google Places API 回傳格式
1. 回傳格式：JSON
當你透過程式（如 Python, Node.js 或 cURL）呼叫 API 時，Google 會傳回一個結構化的 JSON 字串。
字串 (String)：在傳輸過程中，資料是以「JSON 字串」的形式回傳到你的程式中。
物件 (Object)：你的程式接收到後，通常會將其解析（Parse）成「物件」或「字典」，以便提取裡面的名稱、星等和營業時間。 
2. 範例：回傳的樣子
如果你抓取一個夜市，回傳的 JSON 結構大約如下：
json
{
  "displayName": { "text": "士林夜市" },
  "formattedAddress": "111台北市士林區基河路101號",
  "rating": 4.1,
  "regularOpeningHours": {
    "weekdayDescriptions": [
      "星期一: 16:00 – 00:00",
      "星期二: 16:00 – 00:00",
      ...
    ]
  }
}

/ 功能 2 - Google評論
/* 【 夜市評論 】
可用關鍵字 :
1. 交通 方便
2. 塞車
3. 停車
4. 動線
5. 行人

/* 計費邏輯
基本資訊 (Basic)： 包含 名稱、地址、經緯度
專業資訊 (Pro)： 包含 星等 (Rating)、評價總數、商家目前狀態。
企業資訊 (Enterprise)： 包含 營業時間 (Opening Hours)、價格等級。 
Google 評論 (Reviews) 的計費邏輯與「營業時間」相同，都屬於 Places API 中最進階的等級。

/* 抓取規則
單次 API 請求最多只能抓到 5 則評論。
Google API 不提供 抓取該地點「所有歷史評論」的功能。
如果你需要該夜市成千上萬條的評論，透過官方 API 是辦不到的（這通常需要使用額外的 Google Business Profile API 且僅限管理自己擁有的店家，或是使用第三方爬蟲工具）。

/* 附註 常用欄位名稱對照表
對應的官方欄位名稱如下：
想要抓的資料	API 欄位名稱 (Field Mask)	費用等級 (SKU)
1. 夜市名稱	 displayName	              Essentials (基礎)
2. 地址	     formattedAddress           Essentials (基礎)
3. 地點 ID	 id	                        Essentials (基礎)
4. 星等	     rating	                    Pro (專業)
5. 總評論數	 userRatingCount	          Pro (專業)
6. 營業時間	 regularOpeningHours       	Enterprise (企業)
7. 5 則評論內容	reviews               	Enterprise (企業)
