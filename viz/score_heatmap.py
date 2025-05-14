# ◆score_heatmap.py 旧scoremap.py（スコア出力ヒートマップ）
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def draw_score_heatmap(emitted_syntaxes, all_tags, use_streamlit=False):
    # タグ順で行を定義
    tag_list = sorted(all_tags)
    num_steps = len(emitted_syntaxes)

    # 行=タグ, 列=出力順（構文の出力位置）
    heatmap_data = np.zeros((len(tag_list), num_steps))

    for x, syn in enumerate(emitted_syntaxes):
        for tag in syn.tags:
            if tag in tag_list:
                y = tag_list.index(tag)
                heatmap_data[y, x] = syn.score

    fig, ax = plt.subplots(figsize=(num_steps, len(tag_list) * 0.5 + 1))
    sns.heatmap(heatmap_data, cmap='YlGnBu', xticklabels=True, yticklabels=tag_list, ax=ax)

    ax.set_title("構文スコア出力ヒートマップ")
    ax.set_xlabel("出力ステップ")
    ax.set_ylabel("意味タグ")

    if use_streamlit:
        import streamlit as st
        st.pyplot(fig)
    else:
        plt.show()
