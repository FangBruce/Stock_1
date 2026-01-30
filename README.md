Bruce股市 - AI 輔助投資機器人

這是一個基於 Python 開發的桌面應用程式，旨在結合實時金融數據與 Google Gemini AI 技術，為投資者提供直觀、即時的市場分析與決策建議。

🌟 核心特色

多樣化資產追蹤：涵蓋台股熱門個股、主要 ETF 以及全球主流加密貨幣（BTC, ETH等）。

AI 智能投顧：串接 Google Gemini API，根據當前股價提供專業級的文字分析建議。

動態視覺化圖表：使用 Matplotlib 繪製近六個月的價格走勢，支援滑鼠懸停顯示詳細數值。

會員管理系統：具備完整的註冊與登入流程，包含密碼二次確認機制與安全提示。

精美現代化 UI：簡約的文字方框設計，支援響應式佈局與捲軸控制。

🛠️ 技術架構

開發語言：Python

UI 框架：Tkinter / ttk

數據抓取：yfinance (Yahoo Finance API)

資料分析：pandas

圖表繪製：matplotlib

生成式 AI：google-generativeai (Gemini 1.5 Flash)

非同步處理：threading (確保 AI 請求不卡頓 UI)

🚀 快速開始

1. 環境準備

請確保您的電腦已安裝 Python 3.8 或以上版本。

2. 安裝依賴庫

打開終端機並運行以下指令：

pip install yfinance matplotlib pandas google-generativeai


3. 設定 API Key

前往 Google AI Studio 取得您的 Gemini API Key。

在 bruce_finance_pro_v4.py 程式碼中找到以下變數並填入：

GEMINI_API_KEY = "您的_API_KEY_HERE"


4. 執行程式

python bruce_finance_pro_v4.py


📖 使用說明

註冊帳號：首次使用請點擊右上角「註冊」，輸入 Email 並設定密碼（需兩次確認）。

登入系統：若未註冊直接點擊登入，系統將引導您先完成註冊。

選擇分類：在首頁點選「台股」、「ETF」或「加密貨幣」。

查看分析：點擊列表中的「數據分析」按鈕，即可查看即時價格、走勢圖與 Bruce AI 的投資建議。

搜尋功能：可在右上角搜尋欄直接輸入代號（如：2330.TW）或名稱進行快速查詢。

⚠️ 免責聲明

本軟體所提供之所有數據與 AI 建議僅供學術與研究參考，不構成任何形式的投資操作建議。投資有風險，使用者在進行金融交易前應自行承擔責任並諮詢專業理財顧問。

Developed by Bruce - 打造更聰明的投資體驗
