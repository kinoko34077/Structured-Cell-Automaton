from typing import List, Dict
from Syntax import Syntax
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering

def build_tag_vector(syntax: Syntax, tag_index: Dict[str, int], dim: int) -> np.ndarray:
    vec = np.zeros(dim)
    for tag in syntax.tags:
        if tag in tag_index:
            vec[tag_index[tag]] += 1
    return vec

def cluster_syntaxes_by_tags(syntaxes: List[Syntax], n_clusters=2) -> Dict[str, int]:
    # 全タグ辞書作成
    all_tags = sorted(set(tag for syn in syntaxes for tag in syn.tags))
    tag_index = {tag: i for i, tag in enumerate(all_tags)}
    dim = len(tag_index)

    # ベクトル化
    vectors = np.array([build_tag_vector(syn, tag_index, dim) for syn in syntaxes])
    
    # クラスタリング（階層型クラスタ）
    # clustering = AgglomerativeClustering(n_clusters=n_clusters, affinity='cosine', linkage='average') # ❌ 旧形式（古いバージョンではOK）
    clustering = AgglomerativeClustering(n_clusters=n_clusters, metric='cosine', linkage='average') # ✅ 修正後（新バージョン対応）
    labels = clustering.fit_predict(vectors)

    # SID → クラスタ番号 の辞書
    return {syn.sid: label for syn, label in zip(syntaxes, labels)}
