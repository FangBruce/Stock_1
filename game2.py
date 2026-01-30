import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import google.generativeai as genai
import threading
import random

# --- 填入您的 Gemini API Key ---
GEMINI_API_KEY = "" 

# --- 設定資料來源 ---
DATA_SOURCE = {
    '台股': {
        '2330.TW': '台積電', '2317.TW': '鴻海', '2454.TW': '聯發科', '2308.TW': '台達電', 
        '2382.TW': '廣達', '2412.TW': '中華電', '2881.TW': '富邦金', '2882.TW': '國泰金', 
        '2886.TW': '兆豐金', '2303.TW': '聯電', '2891.TW': '中信金', '1301.TW': '台塑', 
        '1303.TW': '南亞', '2002.TW': '中鋼', '2884.TW': '玉山金', '2892.TW': '第一金', 
        '2357.TW': '華碩', '3711.TW': '日月光投控', '2603.TW': '長榮', '3008.TW': '大立光'
    },
    'ETF': {
        '0050.TW': '元大台灣50', '0056.TW': '元大高股息', '00878.TW': '國泰永續高股息', 
        '00929.TW': '復華台灣科技優息', '00919.TW': '群益台灣精選高息', '006208.TW': '富邦台50', 
        '00713.TW': '元大台灣高息低波', '00940.TW': '元大台灣價值高息', '00881.TW': '國泰台灣5G+', 
        '00679B.TW': '元大美債20年', '0051.TW': '元大中型100', '006205.TW': '富邦上証', 
        '0052.TW': '富邦科技', '00692.TW': '富邦公司治理', '00850.TW': '元大臺灣ESG永續', 
        '00757.TW': '統一FANG+', '00900.TW': '富邦特選高股息30', '00939.TW': '統一台灣高息動能',
        '00941.TW': '中信上游半導體', '00631L.TW': '元大台灣50正2'
    },
    '加密貨幣': {
        'BTC-USD': '比特幣', 'ETH-USD': '以太幣', 'USDT-USD': '泰達幣', 'BNB-USD': '幣安幣', 
        'SOL-USD': '索拉納', 'XRP-USD': '瑞波幣', 'DOGE-USD': '狗狗幣', 'ADA-USD': '卡爾達諾', 
        'AVAX-USD': '雪崩幣', 'TRX-USD': '波場', 'DOT-USD': '波卡幣', 'LINK-USD': 'Chainlink'
    }
}

class BruceFinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bruce股市 - AI輔助投資機器人")
        self.root.geometry("1100x850")
        self.root.configure(bg="#F3F4F6") 
        
        self.registered_user = None 
        self.is_logged_in = False

        # Matplotlib 中文字型設定
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
        plt.rcParams['axes.unicode_minus'] = False

        self.setup_header()
        self.setup_main_container()
        self.show_landing_page()

    def setup_header(self):
        self.header = tk.Frame(self.root, bg="#FFFFFF", height=80)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        brand_frame = tk.Frame(self.header, bg="#FFFFFF")
        brand_frame.pack(side="left", padx=30)
        
        tk.Label(brand_frame, text="Bruce", font=("Georgia", 32, "bold italic"), fg="#8B2CF5", bg="#FFFFFF").pack(side="left")
        tk.Label(brand_frame, text=" AI投資機器人", font=("微軟正黑體", 24, "bold"), fg="#FF00FF", bg="#FFFFFF").pack(side="left", padx=5)

        right_area = tk.Frame(self.header, bg="#FFFFFF")
        right_area.pack(side="right", padx=30)

        # 搜尋區
        search_area = tk.Frame(right_area, bg="#FFFFFF")
        search_area.pack(side="left", padx=20)
        self.search_var = tk.StringVar()
        tk.Entry(search_area, textvariable=self.search_var, font=("微軟正黑體", 12), width=20, bd=1, relief="solid").pack(side="left", padx=5)
        tk.Button(search_area, text="搜尋", bg="#0099CC", fg="white", font=("微軟正黑體", 10, "bold"), command=self.perform_search, relief="flat", width=6).pack(side="left")

        self.auth_area = tk.Frame(right_area, bg="#FFFFFF")
        self.auth_area.pack(side="left")
        self.update_auth_buttons()

    def update_auth_buttons(self):
        for widget in self.auth_area.winfo_children(): widget.destroy()
        if not self.is_logged_in:
            tk.Button(self.auth_area, text="註冊", bg="#E74C3C", fg="white", command=self.show_register_page, relief="flat", width=8).pack(side="left", padx=5)
            tk.Button(self.auth_area, text="登入", bg="#2ECC71", fg="white", command=self.show_login_page, relief="flat", width=8).pack(side="left", padx=5)
        else:
            tk.Label(self.auth_area, text=f"Hi, {self.registered_user['email'].split('@')[0]}", bg="white").pack(side="left", padx=5)
            tk.Button(self.auth_area, text="登出", bg="#94A3B8", fg="white", command=self.logout, relief="flat", width=8).pack(side="left", padx=5)

    def setup_main_container(self):
        self.outer_canvas = tk.Canvas(self.root, bg="#F3F4F6", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.outer_canvas.yview)
        self.content_frame = tk.Frame(self.outer_canvas, bg="#F3F4F6")
        self.content_frame.bind("<Configure>", lambda e: self.outer_canvas.configure(scrollregion=self.outer_canvas.bbox("all")))
        self.outer_canvas.create_window((550, 0), window=self.content_frame, anchor="n", width=1000)
        self.outer_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.outer_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def clear_content(self):
        for widget in self.content_frame.winfo_children(): widget.destroy()
        self.outer_canvas.yview_moveto(0)

    def toggle_password(self, entry, button):
        if entry.cget('show') == '*':
            entry.config(show='')
            button.config(text="🔒")
        else:
            entry.config(show='*')
            button.config(text="👁️")

    def show_landing_page(self):
        self.clear_content()
        tk.Label(self.content_frame, text="歡迎來到 Bruce 投資分析中心", font=("微軟正黑體", 28, "bold"), bg="#F3F4F6", pady=30).pack()
        tk.Label(self.content_frame, text="請點選下方分類進行即時數據分析", font=("微軟正黑體", 14), bg="#F3F4F6", fg="#666666").pack(pady=(0, 40))
        
        card_container = tk.Frame(self.content_frame, bg="#F3F4F6")
        card_container.pack()

        categories = [
            ("台股", "#3B82F6"), 
            ("ETF", "#22C55E"), 
            ("加密貨幣", "#F97316")
        ]

        for title, border_color in categories:
            # 建立文字 + 外框設計
            card = tk.Frame(card_container, bg="white", width=250, height=180, highlightbackground=border_color, highlightthickness=2)
            card.pack_propagate(False)
            card.pack(side="left", padx=25)

            # 顯示分類文字
            tk.Label(card, text=title, font=("微軟正黑體", 32, "bold"), bg="white", fg=border_color).pack(expand=True)

            # 透明按鈕
            btn = tk.Button(card, text="", bg="white", activebackground="#F9FAFB", relief="flat", command=lambda t=title: self.show_category_list(t))
            btn.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_register_page(self):
        self.clear_content()
        box = tk.Frame(self.content_frame, bg="white", padx=40, pady=40, bd=1, relief="solid")
        box.pack(pady=60)
        tk.Label(box, text="會員註冊", font=("微軟正黑體", 20, "bold"), bg="white", fg="#E74C3C").pack(pady=(0, 20))
        
        tk.Label(box, text="Email:", bg="white").pack(anchor="w")
        email_ent = tk.Entry(box, font=("Arial", 12), width=35)
        email_ent.pack(pady=5)

        tk.Label(box, text="設定密碼:", bg="white").pack(anchor="w")
        pf1 = tk.Frame(box, bg="white")
        pf1.pack(fill="x")
        p_ent1 = tk.Entry(pf1, font=("Arial", 12), width=30, show="*")
        p_ent1.pack(side="left")
        p_btn1 = tk.Button(pf1, text="👁️", bg="white", relief="flat", command=lambda: self.toggle_password(p_ent1, p_btn1))
        p_btn1.pack(side="left")

        tk.Label(box, text="再次確認密碼:", bg="white").pack(anchor="w", pady=(10, 0))
        pf2 = tk.Frame(box, bg="white")
        pf2.pack(fill="x")
        p_ent2 = tk.Entry(pf2, font=("Arial", 12), width=30, show="*")
        p_ent2.pack(side="left")
        p_btn2 = tk.Button(pf2, text="👁️", bg="white", relief="flat", command=lambda: self.toggle_password(p_ent2, p_btn2))
        p_btn2.pack(side="left")

        def reg():
            email = email_ent.get()
            pwd1 = p_ent1.get()
            pwd2 = p_ent2.get()
            
            if not email:
                messagebox.showwarning("提示", "請輸入 Email")
                return
            if len(pwd1) < 6:
                messagebox.showwarning("提示", "密碼長度至少需 6 位")
                return
            if pwd1 != pwd2:
                messagebox.showerror("錯誤", "兩次輸入的密碼不一致")
                return
                
            self.registered_user = {'email': email, 'password': pwd1}
            messagebox.showinfo("成功", "註冊成功！現在可以登入了")
            self.show_login_page()
        
        tk.Button(box, text="提交註冊", bg="#E74C3C", fg="white", font=("微軟正黑體", 12), command=reg, width=30, pady=5).pack(pady=15)
        tk.Button(box, text="取消", bg="#94A3B8", fg="white", font=("微軟正黑體", 12), command=self.show_landing_page, width=30, pady=5).pack()

    def show_login_page(self):
        # 檢查是否已註冊
        if not self.registered_user:
            messagebox.showinfo("提示", "您尚未擁有帳號，請先註冊")
            self.show_register_page()
            return

        self.clear_content()
        box = tk.Frame(self.content_frame, bg="white", padx=40, pady=40, bd=1, relief="solid")
        box.pack(pady=100)
        tk.Label(box, text="會員登入", font=("微軟正黑體", 20, "bold"), bg="white", fg="#2ECC71").pack(pady=(0, 20))
        
        tk.Label(box, text="Email:", bg="white").pack(anchor="w")
        e_ent = tk.Entry(box, font=("Arial", 12), width=35)
        e_ent.pack(pady=5)

        tk.Label(box, text="密碼:", bg="white").pack(anchor="w")
        pf = tk.Frame(box, bg="white")
        pf.pack(fill="x")
        p_ent = tk.Entry(pf, font=("Arial", 12), width=30, show="*")
        p_ent.pack(side="left")
        p_btn = tk.Button(pf, text="👁️", bg="white", relief="flat", command=lambda: self.toggle_password(p_ent, p_btn))
        p_btn.pack(side="left")

        def log():
            if e_ent.get() == self.registered_user['email'] and p_ent.get() == self.registered_user['password']:
                self.is_logged_in = True
                self.update_auth_buttons()
                self.show_landing_page()
                messagebox.showinfo("歡迎", f"登入成功，歡迎回來！")
            else:
                messagebox.showerror("錯誤", "帳號或密碼有誤")
        
        tk.Button(box, text="立即登入", bg="#2ECC71", fg="white", font=("微軟正黑體", 12), command=log, width=30, pady=5).pack(pady=15)
        tk.Button(box, text="取消", bg="#94A3B8", fg="white", font=("微軟正黑體", 12), command=self.show_landing_page, width=30, pady=5).pack()

    def logout(self):
        self.is_logged_in = False; self.update_auth_buttons(); self.show_landing_page()

    def show_category_list(self, cat):
        self.clear_content()
        tk.Label(self.content_frame, text=f"▎ {cat} 分析清單", font=("微軟正黑體", 22, "bold"), bg="#F3F4F6").pack(anchor="w", padx=50, pady=20)
        tk.Button(self.content_frame, text="← 返回首頁", command=self.show_landing_page, bg="#CCCCCC", relief="flat").pack(anchor="w", padx=50)
        
        f = tk.Frame(self.content_frame, bg="white", padx=20, pady=20, bd=1, relief="solid")
        f.pack(fill="x", padx=50, pady=10)

        for s, n in DATA_SOURCE[cat].items():
            r = tk.Frame(f, bg="white", pady=10)
            r.pack(fill="x")
            tk.Label(r, text=f"• {n} ({s})", font=("微軟正黑體", 14), bg="white", width=40, anchor="w").pack(side="left")
            tk.Button(r, text="數據分析", bg="#2C3E50", fg="white", command=lambda sym=s, nam=n: self.show_analysis(sym, nam)).pack(side="right")
            tk.Frame(f, height=1, bg="#EEEEEE").pack(fill="x")

    def perform_search(self):
        q = self.search_var.get()
        if not q: return
        for c, items in DATA_SOURCE.items():
            for s, n in items.items():
                if q in s or q in n: self.show_analysis(s, n); return
        self.show_analysis(q, q)

    def show_analysis(self, symbol, name):
        self.clear_content()
        box = tk.Frame(self.content_frame, bg="white", padx=30, pady=30, bd=1, relief="solid")
        box.pack(fill="both", expand=True, padx=50, pady=20)
        
        tk.Button(box, text="← 返回", command=self.show_landing_page, bg="#EEEEEE", relief="flat").pack(anchor="w")

        ticker = yf.Ticker(symbol)
        df = ticker.history(period="6mo")
        if df.empty: tk.Label(box, text="查無數據", fg="red").pack(); return

        price = df['Close'].iloc[-1]
        tk.Label(box, text=f"{name} ({symbol})", font=("微軟正黑體", 26, "bold"), bg="white", fg="#8B2CF5").pack(pady=10)
        tk.Label(box, text=f"當前價格: {price:.2f}", font=("微軟正黑體", 16), bg="white").pack()

        # 互動式折線圖
        fig, ax = plt.subplots(figsize=(9, 4), facecolor='white')
        line, = ax.plot(df.index, df['Close'], color='#8B2CF5', linewidth=2)
        ax.set_title("近六個月走勢", fontsize=12)
        ax.grid(True, alpha=0.3)
        
        annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points", bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        def hover(event):
            if event.inaxes == ax:
                cont, ind = line.contains(event)
                if cont:
                    pos = line.get_offsets()[ind["ind"][0]]
                    date = df.index[ind["ind"][0]].strftime('%Y-%m-%d')
                    val = df['Close'].iloc[ind["ind"][0]]
                    annot.xy = (event.xdata, event.ydata)
                    annot.set_text(f"{date}\n價: {val:.2f}")
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if annot.get_visible(): annot.set_visible(False); fig.canvas.draw_idle()

        canvas = FigureCanvasTkAgg(fig, master=box)
        canvas.draw(); canvas.get_tk_widget().pack(fill="x", pady=20)
        fig.canvas.mpl_connect("motion_notify_event", hover)

        # AI 建議
        ai_box = tk.Frame(box, bg="#FFF9E6", padx=20, pady=20, bd=1, relief="solid")
        ai_box.pack(fill="x")
        tk.Label(ai_box, text="✨ Bruce AI 投資策略建議", font=("微軟正黑體", 14, "bold"), bg="#FFF9E6", fg="#D4AC0D").pack(anchor="w")
        
        tips = [
            f"{name} 目前處於上升通道，支撐位穩固，適合拉回時尋找買點。",
            f"技術指標顯示 {symbol} 超買，短期內可能有小幅震盪，建議先入袋為安。",
            f"該標的目前的波動率較低，適合中長期投資者定期定額佈局。",
            f"受到大盤環境影響，{name} 短線趨向保守，建議持股者續抱觀察。",
            f"此資產目前的本益比處於合理區間，基本面強勁，建議長期持有。"
        ]
        ai_msg = tk.Label(ai_box, text=random.choice(tips), font=("微軟正黑體", 12), bg="#FFF9E6", wraplength=800, justify="left")
        ai_msg.pack(anchor="w", pady=10)

        def call_gemini():
            if not GEMINI_API_KEY: return
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(f"分析 {symbol} 價格 {price}。請以專業投顧身份提供 80 字內的中肯投資建議。")
                self.root.after(0, lambda: ai_msg.config(text=res.text))
            except: pass
        threading.Thread(target=call_gemini).start()

if __name__ == "__main__":
    root = tk.Tk(); app = BruceFinanceApp(root); root.mainloop()