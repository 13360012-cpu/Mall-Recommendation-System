import json
import os
from collections import Counter, defaultdict

# 1. 讀取資料集檔案
with open("train_data.json", "r", encoding="utf-8") as f:
    train_data = json.load(f)

json_file = "mall_data_v2.json" if os.path.exists("mall_data_v2.json") else "mall_data.json"
with open(json_file, "r", encoding="utf-8") as f:
    mall_data = json.load(f)

# 2. 建立專櫃資訊查找表
nodes = []
if isinstance(mall_data, dict):
    if "graph_data" in mall_data and isinstance(mall_data["graph_data"], dict):
        nodes = mall_data["graph_data"].get("nodes", [])
    elif "nodes" in mall_data:
        nodes = mall_data.get("nodes", [])
    elif "stores" in mall_data:
        nodes = mall_data.get("stores", [])
elif isinstance(mall_data, list):
    nodes = mall_data

store_map = {}
for n in nodes:
    if isinstance(n, dict) and "id" in n:
        store_map[n["id"]] = {
            "name": n.get("name", n["id"]),
            "category": n.get("category", "未分類"),
            "floor": n.get("floor", "")
        }

# 3. 核心統計：計算成交人氣 (target)
purchase_counter = Counter()
for session in train_data:
    if "target" in session:
        purchase_counter[session["target"]] += 1

# 4. 輸出【全商場】熱門人氣推薦 Top 3 (與分類別統一風格)
print("==========================================")
print("🏆 全商場熱門人氣推薦 Top 3")
print("==========================================")
for rank, (store_id, count) in enumerate(purchase_counter.most_common(3), 1):
    info = store_map.get(store_id, {"name": store_id, "floor": ""})
    print(f"  Top {rank}：{info['name']} [{info['floor']}]")

# 5. 分類別整理
category_purchase = defaultdict(Counter)
for store_id, count in purchase_counter.items():
    cat = store_map.get(store_id, {}).get("category", "其他")
    if cat not in ["動線設施", "設施", "其他"]:
        category_purchase[cat][store_id] = count

# 6. 按 5 大標準類別輸出人氣推薦 Top 3 (給顧客的乾淨視角)
print("\n==========================================")
print("📊 分類別熱門推薦 Top 3")
print("==========================================")
standard_order = ["美妝香氛", "流行服飾", "運動休閒", "美食餐飲", "居家名品"]

for cat in standard_order:
    print(f"\n【{cat}】")
    counter = category_purchase.get(cat, Counter())
    if not counter:
        print("  暫無推薦店家")
        continue
    for rank, (store_id, count) in enumerate(counter.most_common(3), 1):
        info = store_map.get(store_id, {"name": store_id, "floor": ""})
        print(f"  Top {rank}：{info['name']} [{info['floor']}]")

# 7. 匯出成果 (提供給 C 組前端 UI 使用時，排版乾淨俐落)
export_result = {
    "overall_top3": [
        {
            "rank": rank,
            "store_id": s_id,
            "name": store_map.get(s_id, {}).get("name", s_id),
            "floor": store_map.get(s_id, {}).get("floor", ""),
            "category": store_map.get(s_id, {}).get("category", "")
        }
        for rank, (s_id, _) in enumerate(purchase_counter.most_common(3), 1)
    ],
    "category_rankings": {
        cat: [
            {
                "rank": rank,
                "store_id": s_id,
                "name": store_map.get(s_id, {}).get("name", s_id),
                "floor": store_map.get(s_id, {}).get("floor", "")
            }
            for rank, (s_id, _) in enumerate(counter.most_common(3), 1)
        ]
        for cat, counter in category_purchase.items()
    }
}

