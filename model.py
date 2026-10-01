import csv

class RecommendationModel:
    """使用 Python 內建 csv 模組，不需依賴 pandas 即可運作的推薦模型"""
    def __init__(self, csv_path: str):
        self.items = []
        # 使用 Python 內建的 open 與 csv.DictReader 讀取檔案
        with open(csv_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # 將數值欄位轉成對應的型態 (int 或 float)
                self.items.append({
                    "item_id": row["item_id"],
                    "item_name": row["item_name"],
                    "category": row["category"],
                    "price": int(row["price"]),
                    "popularity": float(row["popularity"])
                })

    def recommend_items(self, user_preferences: dict, top_n: int = 5) -> list:
        PREFERENCE_WEIGHT = 0.5
        PRICE_WEIGHT = 0.3
        POPULARITY_WEIGHT = 0.2

        scored_items = []

        for row in self.items:
            category = row["category"]
            price = row["price"]

            if category not in user_preferences:
                continue

            user_data = user_preferences[category]
            preference = user_data["preference"]
            min_price = user_data["min_price"]
            max_price = user_data["max_price"]

            preference_score = preference / 3
            price_score = 1.0 if min_price <= price <= max_price else 0.0
            popularity_score = row["popularity"]

            score = (
                preference_score * PREFERENCE_WEIGHT
                + price_score * PRICE_WEIGHT
                + popularity_score * POPULARITY_WEIGHT
            )

            if score > 0:
                # 複製一份資料並加入 score
                item_copy = row.copy()
                item_copy["score"] = score
                scored_items.append(item_copy)

        # 依照分數由高到低排序並取前 N 名
        scored_items.sort(key=lambda x: x["score"], reverse=True)
        return scored_items[:top_n]