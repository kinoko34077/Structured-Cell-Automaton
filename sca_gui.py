import streamlit as st
from Cell import Cell
from Syntax import Syntax
from syntax_extractor import extract_syntax_from_cells
from scoring import evaluate_syntax
from evolver import evolve_generation
from output_zone import OutputZone
from linearizer import linearize_syntax
from memory_zone import MemoryZone
from clustering import cluster_syntaxes_by_tags
from visualizer import visualize_syntax_clusters

st.set_page_config(page_title="SCA GUI", layout="wide")

st.title("🧠 SCA 構文セル・オートマトン GUI")

# 初期セル
cell1 = Cell(id="c1", position=(0, 0), activation=0.7, meaning_tags=["名詞", "動物"])
cell2 = Cell(id="c2", position=(0, 1), activation=0.5, meaning_tags=["動詞", "移動"])
cell3 = Cell(id="c3", position=(0, 2), activation=0.3, meaning_tags=["助詞"])
initial_cells = [cell1, cell2, cell3]
cell_dict = {c.id: c for c in initial_cells}

# セル表示
st.subheader("セル情報")
for c in initial_cells:
    st.write(c)

# 抽出構文
extracted = extract_syntax_from_cells(initial_cells)
if extracted:
    mutated = extracted[0].mutate()
    syntax_pool = extracted + [mutated]
else:
    syntax_pool = []

# 評価・クラスタ
for syn in syntax_pool:
    evaluate_syntax(syn, cell_dict)
clusters = cluster_syntaxes_by_tags(syntax_pool)

# 構文表示
st.subheader("構文一覧")
for syn in syntax_pool:
    st.markdown(f"- {syn.sid[:8]} | score={syn.score:.3f} | tags={syn.tags}")

# 発話ゾーン
oz = OutputZone(capacity=2, activation_threshold=0.6)
emitted = []

# 世代操作
if st.button("進化 → 評価 → 発話チェック"):
    generation = syntax_pool.copy()
    for gen in range(5):
        for syn in generation:
            evaluate_syntax(syn, cell_dict)
            oz.add_syntax(syn)
        if oz.should_emit():
            emitted = oz.emit()
            break
        generation = evolve_generation(generation)

# 出力表示
if emitted:
    st.subheader("発話構文")
    for syn in emitted:
        line = linearize_syntax(syn, cell_dict)
        st.markdown(f"**{syn.sid[:8]}** → {line}")

# クラスタ図表示
st.subheader("意味クラスタ可視化")
all_tags = sorted(set(tag for syn in syntax_pool for tag in syn.tags))
tag_index = {tag: i for i, tag in enumerate(all_tags)}

visualize_syntax_clusters(syntax_pool, tag_index, use_streamlit=True)   # 可視化（streamlit=Trueを明示）
