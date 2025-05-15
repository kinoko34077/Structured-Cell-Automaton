import json
from core import Cell, Syntax

def save_cells_to_jsonl(cells, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        for cell in cells:
            f.write(json.dumps(cell.__dict__, ensure_ascii=False) + '\n')

def load_cells_from_jsonl(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return [Cell(**json.loads(line)) for line in f]

def save_syntaxes_to_jsonl(syntaxes, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        for syntax in syntaxes:
            f.write(json.dumps(syntax.__dict__, ensure_ascii=False) + '\n')

def load_syntaxes_from_jsonl(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return [Syntax(**json.loads(line)) for line in f]

def save_metadata(filepath, meta_dict):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(meta_dict, f, ensure_ascii=False)

def load_metadata(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
