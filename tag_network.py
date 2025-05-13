# tag_network.py
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import networkx as nx
from collections import Counter
from itertools import combinations

def set_japanese_font():
    preferred_fonts = [
        'MS Gothic', 'Yu Gothic', 'Meiryo', 'Noto Sans CJK JP',
        'TakaoGothic', 'IPAGothic', 'AppleGothic'
    ]
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    for font in preferred_fonts:
        if font in available_fonts:
            plt.rcParams['font.family'] = font
            print(f"✅ 使用フォント: {font}")
            return fm.findfont(font)
    print("⚠ 日本語フォントが見つかりません。")
    return None

def draw_tag_cooccurrence_network(syntaxes, use_streamlit=False):
    # ⬛ フォントを明示的に取得
    font_path = set_japanese_font()
    font_prop = fm.FontProperties(fname=font_path) if font_path else None

    # ⬛ グラフ生成と共起カウント
    G = nx.Graph()
    cooccur_counter = Counter()
    for syn in syntaxes:
        tag_pairs = combinations(sorted(set(syn.tags)), 2)
        for pair in tag_pairs:
            cooccur_counter[pair] += 1
    for (tag1, tag2), weight in cooccur_counter.items():
        G.add_edge(tag1, tag2, weight=weight)

    # ⬛ 描画
    pos = nx.spring_layout(G, seed=42)
    edge_widths = [G[u][v]['weight'] for u, v in G.edges()]

    fig = plt.figure(figsize=(6, 5))
    nx.draw(
        G, pos,
        with_labels=True,
        width=edge_widths,
        node_color='lightblue',
        node_size=1200,
        font_size=10,
        font_family=font_prop.get_name() if font_prop else None
    )
    plt.title("意味タグ共起ネットワーク", fontproperties=font_prop)

    if use_streamlit:
        import streamlit as st
        st.pyplot(fig)
    else:
        plt.show()
