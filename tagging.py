# tagging.py
from typing import List

def map_sentence_to_tags(sentence: str) -> list:
    word_tag_map = {
        "朝": "時間", "夜": "時間", "昨日": "時間", "未来": "時間",
        "都市": "空間", "海": "空間", "森": "空間", "部屋": "空間",
        "喜ぶ": "感情", "怒る": "感情", "悲しむ": "感情", "楽しむ": "感情",
        "見る": "行為", "歩く": "行為", "考える": "行為", "触る": "行為",
        "人": "対象", "動物": "対象", "機械": "対象", "言葉": "対象"
    }

    tags = set()
    for word, tag in word_tag_map.items():
        if word in sentence:
            tags.add(tag)

    return list(tags)

# 意味カテゴリマップ：上位概念 → 下位具体語
tag_cluster_map = {
    "時間": ["朝", "夜", "昨日", "未来"],
    "空間": ["都市", "海", "森", "部屋"],
    "感情": ["喜", "怒", "哀", "楽"],
    "行為": ["見る", "歩く", "考える", "触れる"],
    "対象": ["人", "動物", "言葉", "機械"]
}

def expand_tags(tags: list[str]) -> list[str]:
    """上位タグを与えると、下位タグ群に展開（逆展開も対応可能）"""
    expanded = set(tags)
    for tag in tags:
        if tag in tag_cluster_map:
            expanded.update(tag_cluster_map[tag])
        for parent, children in tag_cluster_map.items():
            if tag in children:
                expanded.add(parent)
    return list(expanded)