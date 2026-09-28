# ◆sca_gui_extended.py

import streamlit as st
from pathlib import Path

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

SAVE_ROOT = Path(__file__).resolve().parent / "save"

from project.ui_helpers import get_cached_figure, syntax_signature
from viz.cluster_map import visualize_syntax_clusters
from viz.genealogy_plot import draw_syntax_genealogy
from viz.cooccurrence_net import draw_tag_cooccurrence_network
from viz.score_heatmap import draw_score_heatmap
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
def _ensure_session_state(cell_count):
    """Initialize the extended experiment once per Streamlit session."""
    if "sca_initial_cells" not in st.session_state:
        st.session_state.sca_initial_cells = generate_balanced_cells(n=cell_count)
        st.session_state.sca_cell_count = cell_count
    if "sca_cell_count" not in st.session_state:
        st.session_state.sca_cell_count = len(st.session_state.sca_initial_cells)
    if cell_count != st.session_state.sca_cell_count:
        st.session_state.sca_pending_cell_count = cell_count
    else:
        st.session_state.pop("sca_pending_cell_count", None)
    if "sca_syntax_pool" not in st.session_state:
        st.session_state.sca_syntax_pool = extract_syntax_from_cells(
            st.session_state.sca_initial_cells
        )
    if "sca_emitted" not in st.session_state:
        st.session_state.sca_emitted = []
    if "sca_memory_zone" not in st.session_state:
        st.session_state.sca_memory_zone = MemoryZone()
    if "sca_output_zone" not in st.session_state:
        st.session_state.sca_output_zone = OutputZone(capacity=3, activation_threshold=0.5)
    if "sca_visualization_cache" not in st.session_state:
        st.session_state.sca_visualization_cache = {}


_ensure_session_state(num_cells)
initial_cells = st.session_state.sca_initial_cells
syntax_pool = st.session_state.sca_syntax_pool
emitted = st.session_state.sca_emitted

pending_cell_count = st.session_state.get("sca_pending_cell_count")
if pending_cell_count is not None:
    st.sidebar.warning(
        f"セル数 {pending_cell_count} が選択されています。適用するまで現在の実験は維持されます。"
    )
    if st.sidebar.button("セル数を適用"):
        st.session_state.sca_initial_cells = generate_balanced_cells(n=pending_cell_count)
        st.session_state.sca_syntax_pool = extract_syntax_from_cells(
            st.session_state.sca_initial_cells
        )
        st.session_state.sca_cell_count = pending_cell_count
        del st.session_state.sca_pending_cell_count
        st.session_state.sca_emitted = []
        st.session_state.sca_memory_zone = MemoryZone()
        st.session_state.sca_output_zone = OutputZone(
            capacity=3, activation_threshold=0.5
        )
        st.session_state.sca_visualization_cache = {}

# =========================
# 💾 保存・読込：サイドバー統合版
# =========================
st.sidebar.subheader("💾 セル・構文の保存・復元")

save_name = st.sidebar.text_input("保存ファイル名（例：save_001）", value="save_001")

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("📥 保存"):
        try:
            quicksave.save_snapshot(
                SAVE_ROOT,
                save_name,
                initial_cells,
                syntax_pool + emitted,
                {"total_generations": st.session_state.total_generations},
            )
        except (quicksave.QuicksaveError, OSError) as exc:
            st.sidebar.error(f"❌ 保存できません: {exc}")
        else:
            st.sidebar.success(f"save/{save_name} に保存しました。")

with col2:
    if st.button("📤 読込"):
        try:
            loaded_cells, loaded_syntaxes, meta = quicksave.load_snapshot(
                SAVE_ROOT, save_name
            )
        except (quicksave.QuicksaveError, OSError) as exc:
            st.sidebar.error(f"❌ 読込できません: {exc}")
        else:
            st.session_state.sca_initial_cells = loaded_cells
            st.session_state.sca_syntax_pool = loaded_syntaxes
            st.session_state.sca_cell_count = len(loaded_cells)
            st.session_state.pop("sca_pending_cell_count", None)
            st.session_state.sca_emitted = []
            st.session_state.sca_memory_zone = MemoryZone()
            st.session_state.sca_output_zone = OutputZone(
                capacity=3, activation_threshold=0.5
            )
            st.session_state.sca_visualization_cache = {}
            st.session_state.total_generations = meta.get("total_generations", 0)
            initial_cells = loaded_cells
            syntax_pool = loaded_syntaxes
            st.success(f"✅ 読込成功 / 世代: {st.session_state.total_generations}")
            st.sidebar.success(f"save/{save_name} を読み込みました。")
            st.sidebar.info(f"🧮 累計進化世代数：{st.session_state.total_generations}")
# =========================
# 📊 状態情報表示エリア
# =========================

# 🎯 cell_dict をこのタイミングで定義しておく（evaluate_syntaxで使用）
initial_cells = st.session_state.sca_initial_cells
syntax_pool = st.session_state.sca_syntax_pool
emitted = st.session_state.sca_emitted
cell_dict = {c.id: c for c in initial_cells}
mz = st.session_state.sca_memory_zone

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

# 発話構文の保存先を更新
emitted = st.session_state.sca_emitted

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
ost = st.session_state.sca_output_zone

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
                    existing_sids = {syn.sid for syn in st.session_state.sca_emitted}
                    for syn in new_output:
                        if syn.sid not in existing_sids:
                            st.session_state.sca_emitted.append(syn)
                            existing_sids.add(syn.sid)
                    emitted = st.session_state.sca_emitted
                    break
                generation = evolve_generation_with_tags(generation, cell_dict, top_k=top_k, current_gen=st.session_state.total_generations)
                st.session_state.total_generations += 1
                mz.auto_optimize(score_thresh=0.3, age_limit=60, similarity_thresh=0.9, current_gen=st.session_state.total_generations)

        if st.button("🔄 内的思考ループ"):
            trigger_tags = expand_tags([t for syn in emitted for t in syn.tags])
            st.markdown(f"🔍 **トリガータグ（展開後）**: {trigger_tags}")
            new_output = simulate_thought_cycle(emitted, cell_dict, mz, ost)
            existing_sids = {syn.sid for syn in st.session_state.sca_emitted}
            for syn in new_output:
                if syn.sid not in existing_sids:
                    st.session_state.sca_emitted.append(syn)
                    existing_sids.add(syn.sid)
            emitted = st.session_state.sca_emitted
            if new_output:
                st.subheader("🧠 発話構文（思考ループ）")
                for syn in new_output:
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
    tag_index = {tag: i for i, tag in enumerate(sorted({tag for syn in syntax_pool for tag in syn.tags}))}
    cluster_signature = (
        syntax_signature(syntax_pool, include_score=False),
        tuple(sorted(tag_index.items())),
    )
    cluster_figure = get_cached_figure(
        st.session_state.sca_visualization_cache,
        "cluster",
        cluster_signature,
        lambda: visualize_syntax_clusters(
            syntax_pool, tag_index, use_streamlit=False, show=False, figsize=fig_size
        ),
    )
    st.pyplot(cluster_figure)

with col2:
    #st.markdown(f"🌱 構文進化系譜")
    genealogy_input = syntax_pool + emitted
    genealogy_figure = get_cached_figure(
        st.session_state.sca_visualization_cache,
        "genealogy",
        syntax_signature(genealogy_input, include_score=False),
        lambda: draw_syntax_genealogy(
            genealogy_input, use_streamlit=False, show=False, figsize=fig_size
        ),
    )
    st.pyplot(genealogy_figure)

col3, col4 = st.columns(2)

with col3:
    #st.markdown(f"🕸️ 意味タグ共起ネットワーク")
    cooccurrence_figure = get_cached_figure(
        st.session_state.sca_visualization_cache,
        "cooccurrence",
        syntax_signature(genealogy_input, include_score=False),
        lambda: draw_tag_cooccurrence_network(
            genealogy_input, use_streamlit=False, show=False, figsize=fig_size
        ),
    )
    st.pyplot(cooccurrence_figure)

with col4:
    #st.markdown(f"📶 スコア出力ヒートマップ")
    heatmap_figure = get_cached_figure(
        st.session_state.sca_visualization_cache,
        "heatmap",
        (syntax_signature(emitted, include_score=True), tuple(all_tags)),
        lambda: draw_score_heatmap(
            emitted, all_tags, use_streamlit=False, show=False, figsize=fig_size
        ),
    )
    st.pyplot(heatmap_figure)

#SCA GUI+ v0.3.1 by KiNoTch
