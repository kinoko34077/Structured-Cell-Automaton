# ◆score_heatmap.py 旧scoremap.py（スコア出力ヒートマップ）
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def draw_score_heatmap(emitted_syntaxes, all_tags, use_streamlit=False, figsize=(6, 4)):
    import matplotlib
    import matplotlib.pyplot as plt

    if not emitted_syntaxes or not all_tags:
        # 🎨 グレースケールでダミー表示
        fig, ax = plt.subplots(figsize=figsize)
        dummy_data = np.array([[0]])
        sns.heatmap(dummy_data, cmap="Greys", cbar=False,
                    xticklabels=["-"], yticklabels=["-"], ax=ax)

        ax.set_title("構文スコア出力ヒートマップ（データなし）")
        ax.set_xlabel("出力ステップ")
        ax.set_ylabel("意味タグ")

        if use_streamlit:
            import streamlit as st
            st.pyplot(fig)
        else:
            plt.show()
        return fig
    
    # ✅ SIDの重複を排除（最初に出現した構文のみ使用）
    seen_sids = set()
    unique_syntaxes = []
    for syn in emitted_syntaxes:
        if syn.sid not in seen_sids:
            seen_sids.add(syn.sid)
            unique_syntaxes.append(syn)

    # タグ順で行を定義
    tag_list = sorted(all_tags)
    num_steps = len(unique_syntaxes)

    # 行=タグ, 列=出力順（構文の出力位置）
    heatmap_data = np.zeros((len(tag_list), num_steps))

    for x, syn in enumerate(unique_syntaxes):
        for tag in syn.tags:
            if tag in tag_list:
                y = tag_list.index(tag)
                heatmap_data[y, x] = syn.score

     # サイズ制御：タグ数が多いと縦だけ大きくし、横は固定
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(heatmap_data, cmap='YlGnBu', xticklabels=True, yticklabels=tag_list, ax=ax)

    ax.set_title("構文スコア出力ヒートマップ")
    ax.set_xlabel("出力ステップ")
    ax.set_ylabel("意味タグ")

    if use_streamlit:
        import streamlit as st
        st.pyplot(fig)
    else:
        plt.show()
    return fig
