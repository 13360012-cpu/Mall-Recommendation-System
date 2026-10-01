import pandas as pd #讀取和處理 Excel/CSV 表格資料
import tkinter as tk #視窗（GUI）工具箱，用來畫按鈕、勾選框、輸入框
from tkinter import messagebox #彈出警告或提示小訊息視窗


# =========================================================
# 1. 讀取商品資料
# =========================================================

items = pd.read_csv("data/items.csv")


# =========================================================
# 2. 推薦演算法
# =========================================================

def recommend_items(items, user_preferences, top_n=5):

    PREFERENCE_WEIGHT = 0.5
    PRICE_WEIGHT = 0.3
    POPULARITY_WEIGHT = 0.2

    def calculate_score(row):

        category = row["category"]
        price = row["price"]

        if category not in user_preferences:
            return 0

        user_data = user_preferences[category]

        preference = user_data["preference"]
        min_price = user_data["min_price"]
        max_price = user_data["max_price"]

        # 喜好程度分數
        preference_score = preference / 3

        # 價格符合程度 [可再做調整]!
        if min_price <= price <= max_price:
            price_score = 1.0
        else:
            price_score = 0.0

        # 熱門程度
        popularity_score = row["popularity"]

        # 最終分數
        score = (
            preference_score * PREFERENCE_WEIGHT
            + price_score * PRICE_WEIGHT
            + popularity_score * POPULARITY_WEIGHT
        )

        return score

    result = items.copy()

    result["score"] = result.apply(
        calculate_score,
        axis=1
    )

    result = result[result["score"] > 0]

    recommendations = (
        result
        .sort_values(by="score", ascending=False)
        .head(top_n)
    )

    return recommendations


# =========================================================
# 3. 主視窗
# =========================================================

root = tk.Tk() #製造主視窗

root.title("個人化冷啟動推薦系統")

root.geometry("750x850") #解析度大小


# =========================================================
# 4. 標題
# =========================================================

title_label = tk.Label(
    root,
    text="✨ 找到適合你的商品 ✨",
    font=("Arial", 22, "bold")
)

title_label.pack(pady=(20, 5))


description_label = tk.Label(
    root,
    text="選擇類別後，設定你的喜好程度和可接受價格",
    font=("Arial", 12)
)

description_label.pack(pady=(0, 20))


# =========================================================
# 5. 類別設定
# =========================================================

categories = [
    "運動",
    "美妝",
    "服飾",
    "3C",
    "美食"
]

category_settings = {}


# =========================================================
# 6. 建立類別區塊
# =========================================================

for category in categories:

    # 外框
    frame = tk.LabelFrame(
        root,
        padx=10,
        pady=8
    )

    frame.pack(
        fill="x",
        padx=50,
        pady=6
    )

    # -----------------------------------------------------
    # 類別選擇
    # -----------------------------------------------------

    selected_var = tk.BooleanVar(value=False)

    category_settings[category] = {
        "selected": selected_var
    }

    checkbox = tk.Checkbutton(
        frame,
        text=category,
        variable=selected_var,
        font=("Arial", 13, "bold")
    )

    checkbox.grid(
        row=0,
        column=0,
        sticky="w"
    )

    # -----------------------------------------------------
    # 設定區域
    # -----------------------------------------------------

    settings_frame = tk.Frame(frame)

    settings_frame.grid(
        row=1,
        column=0,
        sticky="w",
        pady=(8, 0)
    )

    category_settings[category]["settings_frame"] = settings_frame

    # 初始隱藏
    settings_frame.grid_remove()

    # -----------------------------------------------------
    # 喜歡程度
    # -----------------------------------------------------

    tk.Label(
        settings_frame,
        text="喜歡程度：",
        font=("Arial", 10)
    ).grid(
        row=0,
        column=0,
        sticky="w",
        pady=5
    )

    preference_var = tk.IntVar(value=2)

    category_settings[category]["preference"] = preference_var

    tk.Radiobutton(
        settings_frame,
        text="普通",
        variable=preference_var,
        value=1
    ).grid(row=0, column=1)

    tk.Radiobutton(
        settings_frame,
        text="喜歡",
        variable=preference_var,
        value=2
    ).grid(row=0, column=2)

    tk.Radiobutton(
        settings_frame,
        text="非常喜歡",
        variable=preference_var,
        value=3
    ).grid(row=0, column=3)

    # -----------------------------------------------------
    # 可接受價格
    # -----------------------------------------------------

    tk.Label(
        settings_frame,
        text="可接受價格：",
        font=("Arial", 10)
    ).grid(
        row=1,
        column=0,
        sticky="w",
        pady=5
    )

    price_var = tk.StringVar(
        value="501-1000"
    )

    category_settings[category]["price"] = price_var

    price_options = [
        ("500以下", 0, 500),
        ("501～1000", 501, 1000),
        ("1001～2000", 1001, 2000),
        ("2001～5000", 2001, 5000),
        ("5000以上", 5001, 999999)
    ]

    for index, (text, min_price, max_price) in enumerate(price_options):

        tk.Radiobutton(
            settings_frame,
            text=text,
            variable=price_var,
            value=f"{min_price}-{max_price}"
        ).grid(
            row=1,
            column=index + 1
        )

    # -----------------------------------------------------
    # 點擊類別後展開／收起設定
    # -----------------------------------------------------

    def toggle_settings(
        current_category=category
    ):

        settings = category_settings[current_category]

        if settings["selected"].get():

            settings["settings_frame"].grid()

        else:

            settings["settings_frame"].grid_remove()

    checkbox.config(
        command=toggle_settings
    )


# =========================================================
# 7. 開始推薦
# =========================================================

def start_recommendation():

    user_preferences = {}

    for category in categories:

        settings = category_settings[category]

        if not settings["selected"].get():
            continue

        preference = settings["preference"].get()

        price_range = settings["price"].get()

        min_price, max_price = map(
            int,
            price_range.split("-")
        )

        user_preferences[category] = {
            "preference": preference,
            "min_price": min_price,
            "max_price": max_price
        }

    # 檢查是否有選擇
    if not user_preferences:

        messagebox.showwarning(
            "提醒",
            "請至少選擇一個類別！"
        )

        return

    # 執行推薦
    recommendations = recommend_items(
        items,
        user_preferences,
        top_n=5
    )

    if recommendations.empty:

        messagebox.showinfo(
            "推薦結果",
            "目前沒有符合條件的商品。"
        )

        return

    # =====================================================
    # 顯示結果
    # =====================================================

    result_window = tk.Toplevel(root)

    result_window.title("推薦結果")

    result_window.geometry("750x600")

    tk.Label(
        result_window,
        text="🎯 為您推薦的 Top 5 商品",
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
        result_window,
        text=preference_text,
        font=("Arial", 11),
        justify="left"
    ).pack(pady=10)

    # 顯示推薦商品

    for rank, (_, row) in enumerate(
        recommendations.iterrows(),
        start=1
    ):

        text = (
            f"#{rank}  {row['item_name']}\n"
            f"類別：{row['category']}   "
            f"價格：${row['price']}   "
            f"熱門度：{row['popularity']:.2f}\n"
            f"推薦分數：{row['score']:.3f}"
        )

        tk.Label(
            result_window,
            text=text,
            font=("Arial", 11),
            justify="left"
        ).pack(
            anchor="w",
            padx=70,
            pady=10
        )


# =========================================================
# 8. 下一步按鈕
# =========================================================

recommend_button = tk.Button(
    root,
    text="下一步：查看推薦 →",
    command=start_recommendation,
    font=("Arial", 14, "bold"),
    width=25,
    height=2
)

recommend_button.pack(pady=25)


# =========================================================
# 9. 啟動程式
# =========================================================

root.mainloop()