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

def expand_tags(tag_list: List[str]) -> List[str]:
    tag_synonyms = {
        "時間": ["朝", "夜", "未来", "昨日"],
        "空間": ["都市", "海", "森", "部屋"],
        "感情": ["喜", "怒", "哀", "楽"],
        "行為": ["見る", "歩く", "考える", "触れる"],
        "対象": ["人", "動物", "機械", "言葉"]
    }

    expanded = set(tag_list)
    for tag in tag_list:
        if tag in tag_synonyms:
            expanded.update(tag_synonyms[tag])
    return list(expanded)
