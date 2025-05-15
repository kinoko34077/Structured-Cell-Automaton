# ◆cluster_map.py（構文クラスタ） (旧visualizer.py)
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from core import Syntax
from engine.clustering import build_tag_vector
from sklearn.metrics.pairwise import cosine_similarity  # 🔧 追加

import matplotlib
matplotlib.rcParams['font.family'] = 'MS Gothic'  # または 'Yu Gothic' や 'Meiryo'

def visualize_syntax_clusters(syntaxes, tag_index: dict, use_streamlit: bool = False, figsize=(6, 4)):
    dim = len(tag_index)
    vectors = np.array([build_tag_vector(s, tag_index, dim) for s in syntaxes])

    G = nx.Graph()
    for s in syntaxes:
        G.add_node(s.sid[:8], label=s.sid[:8])

    for i in range(len(syntaxes)):
        for j in range(i+1, len(syntaxes)):
            v1 = vectors[i]
            v2 = vectors[j]
            sim = cosine_similarity([v1], [v2])[0][0]
            if sim > 0.2:  # 類似度しきい値
                G.add_edge(syntaxes[i].sid[:8], syntaxes[j].sid[:8], weight=sim)

    pos = nx.spring_layout(G, seed=42)
    fig = plt.figure(figsize=figsize)  # ← 明示的に fig を定義
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1000, font_size=10)
    plt.title("Semantic Cluster Map (構文意味ネットワーク)")

    if use_streamlit:
        import streamlit as st
        st.pyplot(fig)
    else:
        plt.show()
