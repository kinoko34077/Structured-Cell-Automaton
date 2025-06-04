# ◆sca_gui_extended.py

import streamlit as st
import os

from core import Cell, Syntax, OutputZone, linearize_syntax, MemoryZone
from engine import (
    extract_syntax_from_cells,
    evaluate_syntax,
    evolve_generation_with_tags,
    cluster_syntaxes_by_tags,
    simulate_thought_cycle,
    generate_balanced_cells
    )

from tagging import map_sentence_to_tags, expand_tags
from save import quicksave

from viz import cluster_map, genealogy_plot, cooccurrence_net, score_heatmap
import pandas as pd

if 'total_generations' not in st.session_state:
    st.session_state.total_generations = 0

st.set_page_config(page_title="SCA GUI+", layout="wide")
st.title("🧠 SCA 構文セル・オートマトン GUI+ (本格実験版)")

# =========================
# 📊 パラメータ選択 + 読込／保存UI統合
# =========================
st.sidebar.header("⚙️ 実験パラメータ")

num_cells = st.sidebar.slider("セル数", 10, 100, 20)
num_generations = st.sidebar.slider("進化世代数", 1, 50, 5)
top_k = st.sidebar.slider("交叉対象Top-K", 2, 10, 4)

# 後ほど使う変数を一旦初期化
initial_cells = generate_balanced_cells(n=num_cells)
syntax_pool = extract_syntax_from_cells(initial_cells)
emitted = []

# =========================
# 💾 保存・読込：サイドバー統合版
# =========================
st.sidebar.subheader("💾 セル・構文の保存・復元")

save_name = st.sidebar.text_input("保存ファイル名（例：save_001）", value="save_001")

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("📥 保存"):
        quicksave.save_cells_to_jsonl(initial_cells, f"save/{save_name}_cells.jsonl")
        quicksave.save_syntaxes_to_jsonl(syntax_pool + emitted, f"save/{save_name}_syntax.jsonl")
        quicksave.save_metadata(f"save/{save_name}_meta.json", {
            "total_generations": st.session_state.total_generations
        })
        st.sidebar.success(f"save/{save_name} に保存しました。")

with col2:
    if st.button("📤 読込"):
        cell_file = f"save/{save_name}_cells.jsonl"
        syntax_file = f"save/{save_name}_syntax.jsonl"
        meta_file = f"save/{save_name}_meta.json"

        if os.path.exists(cell_file) and os.path.exists(syntax_file):
            initial_cells = quicksave.load_cells_from_jsonl(cell_file)
            syntax_pool = quicksave.load_syntaxes_from_jsonl(syntax_file)

            if os.path.exists(meta_file):
                meta = quicksave.load_metadata(meta_file)
                st.session_state.total_generations = meta.get("total_generations", 0)
                st.success(f"✅ 読込成功 / 世代: {st.session_state.total_generations}")
            else:
                st.session_state.total_generations = 0

            cell_dict = {c.id: c for c in initial_cells}
            st.sidebar.success(f"save/{save_name} を読み込みました。")
            st.sidebar.info(f"🧮 累計進化世代数：{st.session_state.total_generations}")
        else:
            st.sidebar.error("❌ 指定ファイルが見つかりません。")
# =========================
# 📊 状態情報表示エリア
# =========================

# 🎯 cell_dict をこのタイミングで定義しておく（evaluate_syntaxで使用）
cell_dict = {c.id: c for c in initial_cells}
mz = MemoryZone()

# 🎲 構文スコア評価（初期）
for syn in syntax_pool:
    evaluate_syntax(syn, cell_dict, memory_pool=syntax_pool)

col_left, col_right = st.columns(2)


# 出力表示
with col_left:
    with st.expander("🧬 セル情報（クリックで展開）", expanded=False):
        df = pd.DataFrame([{
            "Cell ID": c.id,
            "位置": str(c.position),
            "活性度": round(c.activation, 3),
            "意味タグ": ", ".join(c.meaning_tags)
        } for c in initial_cells])
        st.dataframe(df, use_container_width=True)

if 'emitted' not in st.session_state:
    st.session_state.emitted = []

# 発話構文の保存先を更新
emitted = st.session_state.emitted

with col_right:
    with st.expander("🗣️ 発話構文", expanded=True):
        if emitted:
            # 表形式に整形
            data = []
            seen = set()
            for syn in emitted:
                if syn.sid in seen:
                    continue
                seen.add(syn.sid)
                data.append({
                    "SID": syn.sid[:8],
                    "スコア": round(syn.score, 3),
                    "構成": linearize_syntax(syn, cell_dict),
                    "タグ": ", ".join(syn.tags),
                })

            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)

        else:
            st.info("（まだ発話構文はありません）")



st.markdown(f"🧮 累計進化世代数：**{st.session_state.total_generations}**") # 📈 世代数表示

# =========================
# 🔁 進化操作＋出力
# =========================
ost = OutputZone(capacity=3, activation_threshold=0.5)

with st.expander("⚙️ 操作パネル（進化・思考・淘汰）", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶ 構文進化→評価→発話"):
            generation = syntax_pool.copy()
            for _ in range(num_generations):
                for syn in generation:
                    evaluate_syntax(syn, cell_dict)
                    ost.add_syntax(syn)
                    mz.store(syn, current_gen=st.session_state.total_generations)
                if st.session_state.total_generations > 1 and ost.should_emit():
                    new_output = ost.emit()
                    for syn in new_output:
                        mz.store(syn, current_gen=st.session_state.total_generations)
                    emitted += new_output
                    st.session_state.emitted += new_output  # セッションに記録
                    break
                generation = evolve_generation_with_tags(generation, cell_dict, top_k=top_k, current_gen=st.session_state.total_generations)
                st.session_state.total_generations += 1
                mz.auto_optimize(score_thresh=0.3, age_limit=60, similarity_thresh=0.9, current_gen=st.session_state.total_generations)

        if st.button("🔄 内的思考ループ"):
            trigger_tags = expand_tags([t for syn in emitted for t in syn.tags])
            st.markdown(f"🔍 **トリガータグ（展開後）**: {trigger_tags}")
            emitted = simulate_thought_cycle(emitted, cell_dict, mz, ost)
            if emitted:
                st.subheader("🧠 発話構文（思考ループ）")
                for syn in emitted:
                    st.markdown(f"→ {linearize_syntax(syn, cell_dict)}")
            else:
                st.warning("思考ループからの発話はありませんでした。")

    with col2:
        st.markdown("🧹 **構文淘汰ツール**")
        if st.button("スコア淘汰（<0.3）"):
            mz.prune_by_score(min_score=0.3)
            st.success("スコアによる構文淘汰を実行しました。")
        if st.button("世代淘汰（60世代前まで）"):
            mz.prune_by_generation(current_gen=st.session_state.total_generations, max_age=60)
            st.success("世代ベースで古い構文を淘汰しました。")
        if st.button("類似構文淘汰（閾値=0.9）"):
            mz.prune_by_similarity(threshold=0.9)
            st.success("類似タグを持つ冗長構文を圧縮しました。")
        if st.button("自動最適化（複合条件）"):
            mz.auto_optimize(
                score_thresh=0.3,
                age_limit=60,
                similarity_thresh=0.9,
                current_gen=st.session_state.total_generations
            )
            st.success("記憶圏の自動最適化を実行しました。")


# =========================
# 📊 各種可視化（2×2表示）
# =========================

# 🎯 可視化のための全タグ一覧（syntax_pool + emitted 両方）
all_tags = sorted(set(
    tag for syn in (syntax_pool + emitted) for tag in syn.tags
))

st.subheader("📊 可視化ビュー（構文クラスタ・系譜・共起・スコア）")
fig_size=(8, 3)

col1, col2 = st.columns(2)
with col1:
    #st.markdown(f"🧭 Semantic Cluster Map")
    from viz.cluster_map import visualize_syntax_clusters
    tag_index = {tag: i for i, tag in enumerate(sorted({tag for syn in syntax_pool for tag in syn.tags}))}
    visualize_syntax_clusters(syntax_pool, tag_index, use_streamlit=True, figsize=fig_size)

with col2:
    #st.markdown(f"🌱 構文進化系譜")
    from viz.genealogy_plot import draw_syntax_genealogy
    draw_syntax_genealogy(syntax_pool + emitted, use_streamlit=True, figsize=fig_size)

col3, col4 = st.columns(2)

with col3:
    #st.markdown(f"🕸️ 意味タグ共起ネットワーク")
    from viz.cooccurrence_net import draw_tag_cooccurrence_network
    draw_tag_cooccurrence_network(syntax_pool + emitted, use_streamlit=True, figsize=fig_size)

with col4:
    #st.markdown(f"📶 スコア出力ヒートマップ")
    from viz.score_heatmap import draw_score_heatmap
    draw_score_heatmap(emitted, all_tags, use_streamlit=True, figsize=fig_size)

#SCA GUI+ v0.3.1 by KiNoTch