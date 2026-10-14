import json
import os
import random
from collections import defaultdict

# 1. 自動辨識並讀取商場資料庫
json_file = "mall_data_v2.json" if os.path.exists("mall_data_v2.json") else "mall_data.json"
print(f"正在讀取商場資料庫：{json_file}")

with open(json_file, "r", encoding="utf-8") as f:
    mall_data = json.load(f)

# 解析節點結構
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

# 建立專櫃字典與鄰接圖
node_dict = {n["id"]: n for n in nodes if isinstance(n, dict) and "id" in n}
adj_list = defaultdict(list)

for n in nodes:
    if not isinstance(n, dict) or "id" not in n:
        continue
    curr_id = n["id"]
    
    # 平面走道鄰近專櫃
    for nbr in n.get("neighbors", []):
        adj_list[curr_id].append(nbr)
        adj_list[nbr].append(curr_id)
        
    # 跨樓層手扶梯連通
    for fl_link in n.get("floor_links", []):
        adj_list[curr_id].append(fl_link)
        adj_list[fl_link].append(curr_id)

# 排除設施，分類專櫃 ID
all_store_ids = [n["id"] for n in nodes if n.get("category") != "動線設施"]
sports_store_ids = [n["id"] for n in nodes if n.get("category") == "運動休閒"]

# 2. 客群輪廓偏好設定
PERSONA_PREFERENCES = {
    "beauty_food": {
        "fav_categories": ["美妝香氛", "美食餐飲"],
        "price_pref": [3, 4, 5]
    },
    "fashion_dining": {
        "fav_categories": ["流行服飾", "美食餐飲"],
        "price_pref": [2, 3, 4]
    },
    "family_sports": {
        "fav_categories": ["運動休閒", "美食餐飲", "居家名品"],
        "price_pref": [2, 3, 4]
    },
    "luxury_buffet": {
        "fav_categories": ["美食餐飲", "居家名品"],
        "price_pref": [4, 5]
    }
}

# 3. 隨機漫步動線生成
def generate_trajectories(num_sessions=600, min_len=3, max_len=7):
    dataset = []
    # 客群權重：稍微提升 family_sports 抽中率，確保運動休閒有充分動線
    persona_pool = ["beauty_food", "fashion_dining", "family_sports", "family_sports", "luxury_buffet"]
    
    for i in range(num_sessions):
        p_name = random.choice(persona_pool)
        pref = PERSONA_PREFERENCES[p_name]
        
        # 起點策略：若為運動客群，有 50% 機率直接從運動專櫃或 7F 開始逛
        if p_name == "family_sports" and sports_store_ids and random.random() < 0.5:
            current_node = random.choice(sports_store_ids)
        else:
            current_node = random.choice(all_store_ids)
            
        history = [current_node]
        seq_len = random.randint(min_len, max_len)
        
        for _ in range(seq_len):
            neighbors = adj_list.get(current_node, all_store_ids)
            if not neighbors:
                neighbors = all_store_ids
            
            weights = []
            for nbr in neighbors:
                nbr_info = node_dict.get(nbr, {})
                cat = nbr_info.get("category", "")
                
                weight = 1.0
                # 客群喜好類別 5 倍強力加權
                if cat in pref["fav_categories"]:
                    weight *= 5.0
                # 手扶梯維持高連通，促使跨樓層探索
                if "ESC" in nbr or cat == "動線設施":
                    weight *= 3.0
                
                weights.append(weight)
            
            # 依權重抽取下一站
            next_node = random.choices(neighbors, weights=weights, k=1)[0]
            current_node = next_node
            
            # 設施不記入主要足跡
            if node_dict.get(current_node, {}).get("category") != "動線設施":
                history.append(current_node)
        
        # 去除相鄰連續重複專櫃
        filtered = []
        for h in history:
            if not filtered or filtered[-1] != h:
                filtered.append(h)
        
        if len(filtered) >= 2:
            dataset.append({
                "user_id": f"U{i+1:04d}",
                "persona": p_name,
                "history": filtered[:-1],
                "target": filtered[-1]
            })
            
    return dataset

# 4. 生成並輸出資料集
data = generate_trajectories(num_sessions=600)
split_idx = int(len(data) * 0.8)

train_data = data[:split_idx]
test_data = data[split_idx:]

with open("train_data.json", "w", encoding="utf-8") as f:
    json.dump(train_data, f, ensure_ascii=False, indent=2)

with open("test_data.json", "w", encoding="utf-8") as f:
    json.dump(test_data, f, ensure_ascii=False, indent=2)

print(f"訓練集 (train_data.json)：{len(train_data)} 筆")
print(f"測試集 (test_data.json)：{len(test_data)} 筆")
