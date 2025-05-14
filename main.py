# 統合済み main.py：SCAプロトタイプ進化→発話→整形処理付き

from Cell import Cell
from Syntax import Syntax
from Board import Board
from syntax_extractor import extract_syntax_from_cells
from scoring import evaluate_syntax
from evolver import evolve_generation
from clustering import cluster_syntaxes_by_tags
from output_zone import OutputZone
from linearizer import linearize_syntax

# -------------------------------
# 初期セルと構文の定義
# -------------------------------

cell1 = Cell(id="c1", position=(0, 0), activation=0.7, meaning_tags=["名詞", "動物"])
cell2 = Cell(id="c2", position=(0, 1), activation=0.5, meaning_tags=["動詞", "移動"])
cell3 = Cell(id="c3", position=(0, 2), activation=0.3, meaning_tags=["助詞"])
initial_cells = [cell1, cell2, cell3]

# 盤面にセルを配置
board = Board(width=3, height=1)
for cell in initial_cells:
    board.place_cell(cell)

print("▶ セル情報:")
for c in initial_cells:
    print(c)

# 構文抽出
extracted = extract_syntax_from_cells(initial_cells)

print("\n▶ 抽出された構文群:")
for syn in extracted:
    print(syn)

# 変異構文（初期構文から派生）
mutated_syntax = extracted[0].mutate() if extracted else None
if mutated_syntax:
    print("\n▶ 変異構文:")
    print(mutated_syntax)

# QuickSave復元想定
cell_dict = {c.id: c for c in initial_cells}

# 初期構文にスコア付与・クラスタリング
for syn in extracted:
    evaluate_syntax(syn, cell_dict)
if mutated_syntax:
    evaluate_syntax(mutated_syntax, cell_dict)

syntax_pool = extracted + ([mutated_syntax] if mutated_syntax else [])
clusters = cluster_syntaxes_by_tags(syntax_pool)

print("\n▶ クラスタリング結果（SID → ClusterID）:")
for sid, cid in clusters.items():
    print(f"{sid[:8]} → Cluster {cid}")

# -------------------------------
# 世代ループ + 発話処理
# -------------------------------

oz = OutputZone(capacity=2, activation_threshold=0.6)
emitted_syntaxes = []  # 発話構文保持

generation = syntax_pool.copy()

for gen in range(5):
    print(f"\n▶ 世代 {gen+1}")
    print("  cell_dict keys:", list(cell_dict.keys()))

    for syn in generation:
        evaluate_syntax(syn, cell_dict)
        oz.add_syntax(syn)
        print(f"  - {syn.sid[:8]} | score={syn.score:.3f} | cells={syn.cell_ids}")

    print("  OutputZoneバッファ:")
    for i, s in enumerate(oz.buffer):
        print(f"    {i+1}. {s.sid[:8]} | score={s.score:.3f} | tags={s.tags}")

    if not emitted_syntaxes and oz.should_emit():
        emitted_syntaxes = oz.emit()
        print("\n▶ 出力ゾーンが発話可能！")
        for out in emitted_syntaxes:
            print(f"→ {out.sid[:8]} (score={out.score:.3f}, tags={out.tags})")
        break

    generation = evolve_generation(generation)

else:
    print("▶ 5世代経ても発話条件未達")

# -------------------------------
# 発話整形処理
# -------------------------------

if emitted_syntaxes:
    print("\n▶ 発話構文の整形出力:")
    for syn in emitted_syntaxes:
        print(f"  raw: {syn}")
        linearized = linearize_syntax(syn, cell_dict)
        print(f"  line: {syn.sid[:8]} : {linearized}")
else:
    print("\n▶ 整形対象なし（発話構文なし）")


# -------------------------------
# 再活性導入（発話後に再評価候補を追加）
# -------------------------------

from memory_zone import MemoryZone

# 発話構文を記憶に保存
mz = MemoryZone()

for syn in emitted_syntaxes:
    mz.store(syn)

# 次の世代開始前に再活性構文を取得
reactivated = mz.reactivate_candidates(current_tags=["動物", "移動", "助詞"])  # 仮：意味圏トリガー

print("\n▶ 再活性構文候補:")
for syn in reactivated:
    print(f"  {syn.sid[:8]} | 再スコア={syn.score:.3f} | tags={syn.tags}")

# 再活性構文を次世代プールに追加（例：次のgeneration += reactivated）

# -------------------------------
# 意味マップ描画
# -------------------------------

from viz.cluster_map import visualize_syntax_clusters

# 使用された構文すべてからタグインデックス生成
all_tags = sorted(set(tag for syn in syntax_pool for tag in syn.tags))
tag_index = {tag: i for i, tag in enumerate(all_tags)}

# 可視化（再活性構文などを含めた全構文マップ）
visualize_syntax_clusters(syntax_pool + emitted_syntaxes, tag_index)
