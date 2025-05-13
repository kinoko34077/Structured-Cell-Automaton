# main.py

from Cell import Cell
from Syntax import Syntax

from Board import Board
from syntax_extractor import extract_syntax_from_cells

from quicksave import save_cells_to_jsonl, load_cells_from_jsonl
from quicksave import save_syntaxes_to_jsonl, load_syntaxes_from_jsonl

from scoring import evaluate_syntax
from clustering import cluster_syntaxes_by_tags

from output_zone import OutputZone

from evolver import evolve_generation
from scoring import evaluate_syntax

from linearizer import linearize_syntax

# セルの作成（意味タグ付き）
cell1 = Cell(id="c1", position=(0, 0), activation=0.7, meaning_tags=["名詞", "動物"])
cell2 = Cell(id="c2", position=(0, 1), activation=0.5, meaning_tags=["動詞", "移動"])
cell3 = Cell(id="c3", position=(0, 2), activation=0.3, meaning_tags=["助詞"])

# セルの情報を出力
print("▶ セル情報:")
print(cell1)
print(cell2)
print(cell3)

# 構文の生成（セル列として）
syntax = Syntax(
    sid="SYN001",
    cell_ids=["c1", "c2", "c3"],
    score=0.75,
    meaning_cluster="動物の動き",
    tags=["移動構文"]
)

print("\n▶ 構文情報:")
print(syntax)

# 構文の変異
mutated_syntax = syntax.mutate()
print("\n▶ 変異構文:")
print(mutated_syntax)

# Board作成とセル配置
board = Board(width=3, height=1)
for cell in [cell1, cell2, cell3]:
    board.place_cell(cell)

print("\n▶ 盤面状態:")
print(board)

# セル群から構文抽出
cell_list = [cell1, cell2, cell3]
extracted = extract_syntax_from_cells(cell_list)

print("\n▶ 抽出された構文群:")
for syn in extracted:
    print(syn)

# セルと構文を保存
save_cells_to_jsonl([cell1, cell2, cell3], 'cells.jsonl')
save_syntaxes_to_jsonl(extracted, 'syntaxes.jsonl')

# 読み込み
loaded_cells = load_cells_from_jsonl('cells.jsonl')
loaded_syntaxes = load_syntaxes_from_jsonl('syntaxes.jsonl')

print("\n▶ QuickSave読込結果（セル）:")
for c in loaded_cells:
    print(c)

print("\n▶ QuickSave読込結果（構文）:")
for s in loaded_syntaxes:
    print(s)

# IDからセルを引けるように辞書化
cell_dict = {c.id: c for c in [cell1, cell2, cell3]}

print("\n▶ スコア評価:")
for syn in extracted:
    score = evaluate_syntax(syn, cell_dict)
    print(f"{syn.sid[:8]} のスコア: {score:.3f}")

# 複数構文（仮に抽出結果と変異構文）で試す
syntaxes = extracted + [mutated_syntax]
cluster_result = cluster_syntaxes_by_tags(syntaxes, n_clusters=2)

print("\n▶ クラスタリング結果（SID → ClusterID）:")
for sid, cluster_id in cluster_result.items():
    print(f"{sid[:8]} → Cluster {cluster_id}")

# 出力ゾーンを生成
oz = OutputZone(capacity=5, activation_threshold=0.4)

# 構文を順に投入
for syn in extracted + [mutated_syntax]:
    oz.add_syntax(syn)

# 出力判定と発話
if oz.should_emit():
    print("\n▶ 出力ゾーン発話:")
    for out in oz.emit():
        print(f"→ {out.sid[:8]} (score={out.score:.3f}, tags={out.tags})")
else:
    print("\n▶ 出力ゾーン未発話（条件未満）")


# 初期群を評価
for syn in extracted + [mutated_syntax]:
    evaluate_syntax(syn, cell_dict)

# 出力ゾーン
oz = OutputZone(capacity=2, activation_threshold=0.6)

# 出力構文保持用
emitted_syntaxes = []
if not emitted_syntaxes and oz.should_emit():
    emitted_syntaxes = oz.emit()

# 世代ループ
generation = extracted + [mutated_syntax]
for gen in range(5):  # 世代数指定
    print(f"\n▶ 世代 {gen+1}")
    all_cell_ids = set()
    for syn in generation:
        all_cell_ids.update(syn.cell_ids)
    
    # 再構成された cell_dict（あくまで元のセルから拾えるもの）
    #cell_dict = {c.id: c for c in [cell1, cell2, cell3] if c.id in all_cell_ids}
    all_cells = [cell1, cell2, cell3]  # 今後はこれをグローバルに持っておく
    cell_dict = {c.id: c for c in all_cells}

    print(f"\n▶ 世代 {gen+1}")
    print("  cell_dict keys:", list(cell_dict.keys()))
    # 評価
    for syn in generation:
        evaluate_syntax(syn, cell_dict)
        oz.add_syntax(syn)
        print(f"  - {syn.sid[:8]} | score={syn.score:.3f} | len={len(syn.cell_ids)} | tags={syn.tags}")


    print("  OutputZoneバッファ:")
    for i, s in enumerate(oz.buffer):
        print(f"    {i+1}. {s.sid[:8]} | score={s.score:.3f} | tags={s.tags}")

    # 発話条件チェック
    if emitted_syntaxes:
        print("▶ 出力ゾーンが発話可能！")
        emitted_syntaxes = oz.emit()  # ← ここで一度だけemitし保存
        for out in emitted_syntaxes:
            print(f"→ {out.sid[:8]} (score={out.score:.3f}, tags={out.tags})")
        break

    # 進化
    generation = evolve_generation(generation)
else:
    print("▶ 5世代経ても発話条件未達")

# 出力ゾーンが発話可能なら、一度 emit して発話構文を保持
# ↓↓↓ emit構文をここで再整形
if emitted_syntaxes:
    print("\n▶ 発話構文の整形出力:")
    for syn in emitted_syntaxes:
        print(f"  raw: {syn}")
        linearized = linearize_syntax(syn, cell_dict)
        print(f"  line: {syn.sid[:8]} : {linearized}")
else:
    print("\n▶ 整形対象なし（発話構文なし）")