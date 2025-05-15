import random
from core import Cell

def generate_diverse_cells(n=20):
    tag_pool = {
        "時間": ["朝", "夜", "未来", "昨日"],
        "空間": ["都市", "海", "森", "部屋"],
        "感情": ["喜", "怒", "哀", "楽"],
        "行為": ["見る", "歩く", "考える", "触れる"],
        "対象": ["人", "動物", "言葉", "機械"],
        "その他": ["静か", "速い", "青い", "危険"]
    }

    cells = []
    for i in range(n):
        category = random.choice(list(tag_pool.keys()))
        tags = random.sample(tag_pool[category], k=2)
        activation = round(random.uniform(0.3, 0.9), 2)
        cells.append(Cell(
            id=f"c{i:02}",
            position=(i // 5, i % 5),
            activation=activation,
            meaning_tags=tags
        ))

    return cells

def generate_balanced_cells(n=20):
    tag_pool = {
        "時間": ["朝", "夜", "未来", "昨日"],
        "空間": ["都市", "海", "森", "部屋"],
        "感情": ["喜", "怒", "哀", "楽"],
        "行為": ["見る", "歩く", "考える", "触れる"],
        "対象": ["人", "動物", "機械", "言葉"],
        "その他": ["速い", "静か", "青い", "危険"]
    }

    categories = list(tag_pool.keys())
    per_category = max(2, n // len(categories))
    cells = []
    idx = 0

    for category in categories:
        tags = tag_pool[category]
        for _ in range(per_category):
            selected = random.sample(tags, k=2)
            activation = round(random.uniform(0.3, 0.9), 2)
            cells.append(Cell(
                id=f"c{idx:02}",
                position=(idx // 5, idx % 5),
                activation=activation,
                meaning_tags=selected
            ))
            idx += 1

    return cells
