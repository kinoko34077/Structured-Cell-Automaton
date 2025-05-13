from typing import List
from Syntax import Syntax
from memory_zone import MemoryZone
from evolver import evolve_generation
from scoring import evaluate_syntax
from output_zone import OutputZone

def simulate_thought_cycle(
    emitted: List[Syntax],
    cell_dict: dict,
    memory_zone: MemoryZone,
    output_zone: OutputZone,
    iterations: int = 20
):
    # 1. 意味タグ履歴収集
    recent_tags = list(set(tag for syn in emitted for tag in syn.tags))

    # 2. 近接タグ（簡易的に：同一語幹や派生語含むよう拡張）
    # 今はそのまま recent_tags を使う（将来的にWordNetや類語辞典ベースに拡張可能）

    # 3. 再活性構文を取得
    reactivated = memory_zone.reactivate_candidates(recent_tags, threshold=0.3)

    print(f"\n[Thought Loop] 再活性候補数: {len(reactivated)}")
    for s in reactivated:
        print(f"  ↳ {s.sid[:8]} | score={s.score:.3f} | tags={s.tags}")

    if not reactivated:
        sorted_mem = sorted(memory_zone.memory.values(), key=lambda e: -e['score'])
        if sorted_mem:
            syn = sorted_mem[0]['syntax']
            syn.score *= 0.9
            reactivated.append(syn)
            print(f"⚠️ 再活性構文が0件だったため {syn.sid[:8]} を強制追加")

    # 4. 進化サイクル
    generation = reactivated
    for i in range(iterations):
        if not generation:
            break

        for syn in generation:
            evaluate_syntax(syn, cell_dict)
            output_zone.add_syntax(syn)
            print(f"[内部] 再評価構文: {syn.sid[:8]} | score={syn.score:.3f} | tags={syn.tags}")

        if output_zone.should_emit():
            print("[内部] 出力ゾーンが満たされました → emit 実行")
            return output_zone.emit()

        generation = evolve_generation(generation)

    print("[内部] 発話に至らず思考ループ終了")
    return []
