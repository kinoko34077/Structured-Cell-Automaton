from Syntax import Syntax
from typing import List
import uuid
import random
import time

def crossover(s1: Syntax, s2: Syntax) -> Syntax:
    # 交叉：半分ずつ交互に取る（簡易）
    l1 = s1.cell_ids[:len(s1.cell_ids)//2]
    l2 = s2.cell_ids[len(s2.cell_ids)//2:]
    new_cells = l1 + l2
    new_sid = str(uuid.uuid4())
    tags = list(set(s1.tags + s2.tags))
    return Syntax(sid=new_sid, cell_ids=new_cells, parent_sid=f"{s1.sid}&{s2.sid}", tags=tags)

def mutate(syn: Syntax) -> Syntax:
    # 簡易変異：セル列を逆順
    new_cell_ids = list(reversed(syn.cell_ids))
    new_sid = str(uuid.uuid4())
    return Syntax(sid=new_sid, cell_ids=new_cell_ids, parent_sid=syn.sid, tags=syn.tags)

def evolve_generation(syntaxes: List[Syntax], top_k=2, mutation_rate=0.3) -> List[Syntax]:
    # スコア上位から交叉
    sorted_s = sorted(syntaxes, key=lambda s: -s.score)
    new_generation = []

    # 交叉
    for i in range(min(top_k, len(sorted_s) - 1)):
        s1, s2 = sorted_s[i], sorted_s[i+1]
        child = crossover(s1, s2)
        new_generation.append(child)

    # 変異（一定確率）
    for s in sorted_s[:top_k]:
        if random.random() < mutation_rate:
            mutated = mutate(s)
            new_generation.append(mutated)

    return new_generation

def crossover_tags(s1: Syntax, s2: Syntax, cell_dict: dict) -> Syntax:
    from random import sample

    # タグの交差
    combined_tags = list(set(s1.tags + s2.tags))
    selected_tags = sample(combined_tags, min(4, len(combined_tags)))

    # タグに近いセルを選出
    matching_cells = [
        c for c in cell_dict.values()
        if any(tag in c.meaning_tags for tag in selected_tags)
    ]

    selected_cells = sample(matching_cells, min(3, len(matching_cells)))
    sid = str(uuid.uuid4())

    return Syntax(
        sid=sid,
        cell_ids=[c.id for c in selected_cells],
        tags=selected_tags,
        parent_sid=f"{s1.sid}&{s2.sid}"
    )