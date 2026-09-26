import json
import random

# 1. 讀取商品/櫃位圖資料
with open("mall_data.json", "r", encoding="utf-8") as f:
    mall_data = json.load(f)

nodes = mall_data["nodes"]
node_dict = {n["id"]: n for n in nodes}

# 4 種顧客客群
PERSONAS = [
    {
        "type": "beauty_food",
        "fav_categories": ["美妝香氛", "美妝保養", "專業彩妝", "餐飲甜點", "飲品咖啡"],
    },
    {
        "type": "fashion_dining",
        "fav_categories": [
            "流行服飾",
            "流行女裝",
            "少女服飾",
            "主題餐廳",
            "輕食鬆餅",
        ],
    },
    {
        "type": "family_sports",
        "fav_categories": [
            "運動旗艦",
            "休閒休旅鞋",
            "兒童玩具",
            "童裝童用品",
            "日式豬排專門",
        ],
    },
    {
        "type": "home_gourmet",
        "fav_categories": [
            "頂級家電",
            "按摩舒壓器材",
            "名品床墊",
            "個人燒肉名店",
            "頂級百匯吃到飽",
        ],
    },
]


# 2. 模擬顧客隨機遊走
def simulate_user_trajectory(user_id):
    persona = random.choice(PERSONAS)
    fav_cats = set(persona["fav_categories"])

    candidate_starts = [
        n["id"]
        for n in nodes
        if (n["category"] in fav_cats or n["floor"] in ["1F", "B1F"])
        and "ESC" not in n["id"]
    ]
    current = random.choice(candidate_starts)

    path = [current]
    max_hops = random.randint(5, 10)

    for _ in range(max_hops):
        curr_node = node_dict[current]
        available_next = []

        if "neighbors" in curr_node:
            available_next.extend(curr_node["neighbors"])
        if "floor_links" in curr_node:
            available_next.extend(curr_node["floor_links"])

        available_next = [nid for nid in available_next if nid in node_dict]
        if not available_next:
            break

        weights = []
        for nid in available_next:
            n_data = node_dict[nid]
            if n_data["category"] in fav_cats:
                weights.append(4.0)
            elif "ESC" in nid:
                weights.append(2.0)
            else:
                weights.append(1.0)

        next_hop = random.choices(available_next, weights=weights, k=1)[0]
        path.append(next_hop)
        current = next_hop

    return {
        "user_id": f"U{user_id:04d}",
        "persona": persona["type"],
        "raw_path": path,
    }


# 3. 資料清理
def clean_trajectory(raw_record):
    path = raw_record["raw_path"]

    # (1) 去除連續重複停留
    dedup_path = []
    for item in path:
        if not dedup_path or dedup_path[-1] != item:
            dedup_path.append(item)

    # (2) 過濾純動線設施（ESC）
    interacted_stores = [
        item for item in dedup_path if "ESC" not in node_dict[item]["id"]
    ]

    # (3) 剔除過短軌跡
    if len(interacted_stores) < 3:
        return None

    return {
        "user_id": raw_record["user_id"],
        "persona": raw_record["persona"],
        "history": interacted_stores[:-1],
        "target": interacted_stores[-1],
    }


# 產生 120 筆軌跡並清理
cleaned_data = []
for i in range(1, 121):
    raw = simulate_user_trajectory(i)
    cleaned = clean_trajectory(raw)
    if cleaned:
        cleaned_data.append(cleaned)

# 4. Train / Test 切分 (8:2)
random.seed(42)
random.shuffle(cleaned_data)

split_idx = int(len(cleaned_data) * 0.8)
train_set = cleaned_data[:split_idx]
test_set = cleaned_data[split_idx:]

with open("train_data.json", "w", encoding="utf-8") as f:
    json.dump(train_set, f, ensure_ascii=False, indent=2)

with open("test_data.json", "w", encoding="utf-8") as f:
    json.dump(test_set, f, ensure_ascii=False, indent=2)

print("=== 資料集產生完成！ ===")
print(f"有效資料總數: {len(cleaned_data)} 筆")
print(f"訓練集 (Train): {len(train_set)} 筆 -> train_data.json")
print(f"測試集 (Test):  {len(test_set)} 筆 -> test_data.json")