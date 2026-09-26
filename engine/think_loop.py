from typing import List
from core import Syntax, MemoryZone, OutputZone
from .evolver import evolve_generation, evolve_generation_with_tags
from .scoring import evaluate_syntax
from tagging import expand_tags

def simulate_thought_cycle(
    emitted: List[Syntax],
    cell_dict: dict,
    memory_zone: MemoryZone,
    output_zone: OutputZone,
    iterations: int = 5,
    current_generation=0
):
    
    if not memory_zone.pool:
        print("[思考ループ] 記憶圏が空です")
        return []
    
    # 1. 発話構文のタグからトリガー抽出＋クラスタ拡張
    recent_tags = list(set(tag for syn in emitted for tag in syn.tags))
    trigger_tags = expand_tags(recent_tags)

    reactivated = memory_zone.reactivate_candidates(trigger_tags, threshold=0.3)

    # 2. 初期世代（再活性構文）を設定
    generation = reactivated
    result = []  # 🔸 ← 蓄積変数を忘れず初期化
    for i in range(iterations):
        if not generation:
            break

        for syn in generation:
            evaluate_syntax(syn, cell_dict)
            output_zone.add_syntax(syn)

        if output_zone.should_emit():
            emitted_syntaxes = output_zone.emit()
            result += emitted_syntaxes  # 🔹 ← 蓄積

            for syn in emitted_syntaxes:  # 🔹 ← ここが記憶圏保存箇所
                memory_zone.store(syn, current_gen=current_generation)
        
        generation = evolve_generation_with_tags(generation, cell_dict) # 本来は「前回の generation を進化」すべき

    return result  # 🔸 ← 返り値を result に修正
