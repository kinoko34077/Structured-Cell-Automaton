# sca_gui.py
import streamlit as st
from core import Cell, Syntax, MemoryZone, OutputZone
from core.memory_zone import DEFAULT_MAX_AGE_GENERATIONS, prune_memory_by_generation
from engine.syntax_extractor import extract_syntax_from_cells

from engine.scoring import evaluate_syntax
from engine.evolver import evolve_generation, crossover_tags
from core.linearizer import linearize_syntax
from engine.clustering import cluster_syntaxes_by_tags
from viz.cluster_map import visualize_syntax_clusters

from engine.think_loop import simulate_thought_cycle

from engine.sca_data import generate_diverse_cells, generate_balanced_cells

from tagging import map_sentence_to_tags, expand_tags


st.set_page_config(page_title="SCA GUI", layout="wide")

st.title("🧠 SCA 構文セル・オートマトン GUI")
# --------------
# セル管理
# --------------

# 初期セル
# cell1 = Cell(id="c1", position=(0, 0), activation=0.7, meaning_tags=["名詞", "動物"])
# cell2 = Cell(id="c2", position=(0, 1), activation=0.5, meaning_tags=["動詞", "移動"])
# cell3 = Cell(id="c3", position=(0, 2), activation=0.3, meaning_tags=["助詞"])
# initial_cells = [cell1, cell2, cell3]

# セル生成（20個例）
if "sca_initial_cells" not in st.session_state:
    initial_cells = generate_balanced_cells()
    cell_dict = {c.id: c for c in initial_cells}

    extracted = extract_syntax_from_cells(initial_cells)
    if extracted:
        mutated = extracted[0].mutate()
        syntax_pool = extracted + [mutated]
    else:
        syntax_pool = []

    for syn in syntax_pool:
        evaluate_syntax(syn, cell_dict, memory_pool=syntax_pool)

    st.session_state.sca_initial_cells = initial_cells
    st.session_state.sca_cell_dict = cell_dict
    st.session_state.sca_syntax_pool = syntax_pool

initial_cells = st.session_state.sca_initial_cells
cell_dict = st.session_state.sca_cell_dict
syntax_pool = st.session_state.sca_syntax_pool

# セル表示
st.subheader("セル情報")
for c in initial_cells:
    st.write(c)

# 評価・クラスタ
clusters = cluster_syntaxes_by_tags(syntax_pool)

# --------------
# 構文管理
# --------------

# 構文表示
st.subheader("構文一覧")
for syn in syntax_pool:
    st.markdown(f"- {syn.sid[:8]} | score={syn.score:.3f} | tags={syn.tags}")

# 発話ゾーン
if "sca_output_zone" not in st.session_state:
    st.session_state.sca_output_zone = OutputZone(capacity=1, activation_threshold=0.6)
if "sca_memory_zone" not in st.session_state:
    st.session_state.sca_memory_zone = MemoryZone()
if "sca_emitted" not in st.session_state:
    st.session_state.sca_emitted = []
if "sca_generation" not in st.session_state:
    st.session_state.sca_generation = 0
if "sca_last_analysis" not in st.session_state:
    st.session_state.sca_last_analysis = None

oz = st.session_state.sca_output_zone
mz = st.session_state.sca_memory_zone
emitted = st.session_state.sca_emitted

def advance_current_generation(steps=1):
    st.session_state.sca_generation += steps
    return st.session_state.sca_generation

# ------------
# 改良版進化ループ（tag-based crossover）
def evolve_generation_with_tags(syntaxes, cell_dict, top_k=4):
    sorted_s = sorted(syntaxes, key=lambda s: -s.score)
    new_generation = []
    for i in range(min(top_k - 1, len(sorted_s) - 1)):
        s1, s2 = sorted_s[i], sorted_s[i+1]
        child = crossover_tags(s1, s2, cell_dict)
        new_generation.append(child)
    return new_generation

# --------------

# 世代操作
if st.button("進化 → 評価 → 発話チェック"):
    advance_current_generation()
    generation = syntax_pool.copy()
    for gen in range(5):
        for syn in generation:
            evaluate_syntax(syn, cell_dict)
            oz.add_syntax(syn)
            
        if oz.should_emit():
            emitted = oz.emit()
            st.session_state.sca_emitted = emitted
            break
        generation = evolve_generation_with_tags(generation, cell_dict)  # ← 意味タグベース交叉

# 出力表示
if emitted:
    st.subheader("発話構文")
    for syn in emitted:
        line = linearize_syntax(syn, cell_dict)
        st.markdown(f"**{syn.sid[:8]}** → {line}")

# ------------------------
# 描画処理
# ------------------------

# クラスタ図表示
st.subheader("意味クラスタ可視化")
all_tags = sorted(set(tag for syn in syntax_pool for tag in syn.tags))
tag_index = {tag: i for i, tag in enumerate(all_tags)}

visualize_syntax_clusters(syntax_pool, tag_index, use_streamlit=True)   # 可視化（streamlit=Trueを明示）

# -------
# デバッグ出力関数を追加
def debug_reactivation(memory_zone, current_tags):
    print("\n[DEBUG] Reactivation trigger tags:", current_tags)
    for sid, syntax in memory_zone.pool.items():
        overlap = set(syntax.tags).intersection(current_tags)
        print(f"- {sid[:8]} | tags={syntax.tags} | overlap={list(overlap)}")

# -------
# MemoryZone + 内的思考ボタン

# GUIボタン操作群
st.subheader("操作パネル")
if st.button("初回進化・発話"):
    current_generation = advance_current_generation()
    for syn in syntax_pool:
        mz.store(syn, current_gen=current_generation)
    generation = syntax_pool.copy()
    for gen in range(5):
        for syn in generation:
            evaluate_syntax(syn, cell_dict)
            oz.add_syntax(syn)
        if oz.should_emit():
            emitted = oz.emit()
            st.session_state.sca_emitted = emitted
            break
        generation = evolve_generation_with_tags(generation, cell_dict)  # ← 意味タグベース交叉

# 内的思考ループボタン処理
if st.button("内的思考ループ実行"):
    current_generation = advance_current_generation()
    debug_reactivation(mz, [t for syn in emitted for t in syn.tags])
    emitted = simulate_thought_cycle(emitted, cell_dict, mz, oz, current_generation=current_generation)
    st.session_state.sca_emitted = emitted

    if emitted:
        st.subheader("発話構文（内的思考ループ）:")
        for syn in emitted:
            line = linearize_syntax(syn, cell_dict)
            st.markdown(f"→ {line}")
    else:
        st.warning("思考ループからは構文が発話されませんでした（条件未達）")

# ------
# Streamlit に入力欄＋連携追加（GUI）

st.subheader("自然言語からの入力")

user_input = st.text_input("文章を入力してください（例：昨日、都市を歩いた）")

if st.button("意味タグに変換"):
    inferred_tags = map_sentence_to_tags(user_input)
    expanded_tags = expand_tags(inferred_tags)

    # MemoryZoneに対してタグをトリガーとして再活性化処理
    reactivated = mz.reactivate_candidates(expanded_tags)
    st.session_state.sca_last_analysis = {
        "input": user_input,
        "inferred_tags": list(inferred_tags),
        "expanded_tags": list(expanded_tags),
        "reactivated_lines": [linearize_syntax(syn, cell_dict) for syn in reactivated],
    }

last_analysis = st.session_state.sca_last_analysis
if last_analysis:
    inferred_label = ", ".join(last_analysis["inferred_tags"]) or "（なし）"
    expanded_label = ", ".join(last_analysis["expanded_tags"]) or "（なし）"
    st.markdown(f"**前回の分析対象:** {last_analysis['input']}")
    st.markdown(f"**抽出された意味タグ:** {inferred_label}")
    st.markdown(f"**拡張されたトリガータグ:** {expanded_label}")

    if last_analysis["reactivated_lines"]:
        st.subheader("意味タグに基づく再活性構文:")
        for line in last_analysis["reactivated_lines"]:
            st.markdown(f"→ {line}")
    else:
        st.warning("対応する再活性構文は見つかりませんでした。")
# -----

# SID構文ツリー可視化（networkx + matplotlib）
from viz.genealogy_plot import draw_syntax_genealogy

st.subheader("構文進化系譜")
draw_syntax_genealogy(syntax_pool + emitted, use_streamlit=True)

# 共起ネットワーク描画モジュール
from viz.cooccurrence_net import draw_tag_cooccurrence_network

st.subheader("意味タグ共起ネットワーク")
draw_tag_cooccurrence_network(syntax_pool + emitted, use_streamlit=True)


# 出力スコアヒートマップ
from viz.score_heatmap import draw_score_heatmap

if emitted:
    st.subheader("スコア出力ヒートマップ")
    all_tags = sorted(set(tag for syn in syntax_pool + emitted for tag in syn.tags))
    draw_score_heatmap(emitted, all_tags, use_streamlit=True)

# 構文淘汰ツール
st.subheader("構文淘汰ツール")

if st.button("スコア淘汰（<0.3）"):
    mz.prune_by_score(min_score=0.3)
    st.success("スコアによる構文淘汰を実行しました。")

if st.button(f"世代淘汰（{DEFAULT_MAX_AGE_GENERATIONS}世代超）"):
    prune_memory_by_generation(mz, current_generation=st.session_state.sca_generation)
    st.success("世代差に基づいて古い構文を淘汰しました。")

if st.button("類似構文淘汰（閾値=0.9）"):
    mz.prune_by_similarity(threshold=0.9)
    st.success("類似タグを持つ冗長構文を圧縮しました。")