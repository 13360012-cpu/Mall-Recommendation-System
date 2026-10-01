import tkinter as tk
from tkinter import messagebox

class ResultWindow:
    """負責呈現推薦結果的獨立視窗元件"""
    def __init__(self, parent, user_preferences: dict, recommendations: list):
        self.window = tk.Toplevel(parent)
        self.window.title("推薦結果")
        self.window.geometry("750x600")
        
        self._create_widgets(user_preferences, recommendations)

    def _create_widgets(self, user_preferences: dict, recommendations: list):
        tk.Label(
            self.window,
            text="為您推薦的 Top 5 商品",
            font=("Arial", 20, "bold")
        ).pack(pady=20)

        # 顯示使用者設定
        preference_text = "你的設定：\n"
        for category, data in user_preferences.items():
            if data["preference"] == 1:
                level = "普通"
            elif data["preference"] == 2:
                level = "喜歡"
            else:
                level = "非常喜歡"

            preference_text += (
                f"{category}｜"
                f"{level}｜"
                f"${data['min_price']}～${data['max_price']}\n"
            )

        tk.Label(
            self.window,
            text=preference_text,
            font=("Arial", 11),
            justify="left"
        ).pack(pady=10)

        # 顯示推薦商品 (使用一般 list 迴圈，不依賴 pandas)
        for rank, row in enumerate(recommendations, start=1):
            text = (
                f"#{rank}  {row['item_name']}\n"
                f"類別：{row['category']}   "
                f"價格：${row['price']}   "
                f"熱門度：{row['popularity']:.2f}\n"
                f"推薦分數：{row['score']:.3f}"
            )
            tk.Label(
                self.window,
                text=text,
                font=("Arial", 11),
                justify="left"
            ).pack(anchor="w", padx=70, pady=10)


class ColdStartApp:
    """負責主畫面佈局與使用者互動邏輯"""
    def __init__(self, root: tk.Tk, model):
        self.root = root
        self.model = model
        self.categories = ["運動", "美妝", "服飾", "3C", "美食"]
        self.category_settings = {}

        self._setup_main_window()
        self._create_widgets()

    def _setup_main_window(self):
        self.root.title("個人化冷啟動推薦系統")
        self.root.geometry("750x850")

    def _create_widgets(self):
        tk.Label(
            self.root,
            text=" 找到適合你的商品 ",
            font=("Arial", 22, "bold")
        ).pack(pady=(20, 5))

        tk.Label(
            self.root,
            text="選擇類別後，設定你的喜好程度和可接受價格",
            font=("Arial", 12)
        ).pack(pady=(0, 20))

        for category in self.categories:
            frame = tk.LabelFrame(self.root, padx=10, pady=8)
            frame.pack(fill="x", padx=50, pady=6)

            selected_var = tk.BooleanVar(value=False)
            self.category_settings[category] = {"selected": selected_var}

            checkbox = tk.Checkbutton(
                frame,
                text=category,
                variable=selected_var,
                font=("Arial", 13, "bold")
            )
            checkbox.grid(row=0, column=0, sticky="w")

            settings_frame = tk.Frame(frame)
            settings_frame.grid(row=1, column=0, sticky="w", pady=(8, 0))
            self.category_settings[category]["settings_frame"] = settings_frame
            settings_frame.grid_remove()

            # 喜歡程度選項
            tk.Label(settings_frame, text="喜歡程度：", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
            preference_var = tk.IntVar(value=2)
            self.category_settings[category]["preference"] = preference_var

            for idx, (text, val) in enumerate([("普通", 1), ("喜歡", 2), ("非常喜歡", 3)], start=1):
                tk.Radiobutton(settings_frame, text=text, variable=preference_var, value=val).grid(row=0, column=idx)

            # 可接受價格選項
            tk.Label(settings_frame, text="可接受價格：", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
            price_var = tk.StringVar(value="501-1000")
            self.category_settings[category]["price"] = price_var

            price_options = [
                ("500以下", 0, 500),
                ("501～1000", 501, 1000),
                ("1001～2000", 1001, 2000),
                ("2001～5000", 2001, 5000),
                ("5000以上", 5001, 999999)
            ]

            for index, (text, min_p, max_p) in enumerate(price_options):
                tk.Radiobutton(
                    settings_frame,
                    text=text,
                    variable=price_var,
                    value=f"{min_p}-{max_p}"
                ).grid(row=1, column=index + 1)

            def make_toggle(st=settings_frame, st_var=selected_var):
                def toggle():
                    if st_var.get():
                        st.grid()
                    else:
                        st.grid_remove()
                return toggle

            checkbox.config(command=make_toggle())

        recommend_button = tk.Button(
            self.root,
            text="下一步：查看推薦 →",
            command=self.start_recommendation,
            font=("Arial", 14, "bold"),
            width=25,
            height=2
        )
        recommend_button.pack(pady=25)

    def start_recommendation(self):
        user_preferences = {}

        for category in self.categories:
            settings = self.category_settings[category]
            if not settings["selected"].get():
                continue

            preference = settings["preference"].get()
            price_range = settings["price"].get()
            min_price, max_price = map(int, price_range.split("-"))

            user_preferences[category] = {
                "preference": preference,
                "min_price": min_price,
                "max_price": max_price
            }

        if not user_preferences:
            messagebox.showwarning("提醒", "請至少選擇一個類別！")
            return

        recommendations = self.model.recommend_items(user_preferences, top_n=5)

        if not recommendations:
            messagebox.showinfo("推薦結果", "目前沒有符合條件的商品。")
            return

        ResultWindow(self.root, user_preferences, recommendations)