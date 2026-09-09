import math
import re
from collections import Counter

_WORD_RE = re.compile(r"[a-zA-Z]+")
def tokenize(text):
    return [w.lower() for w in _WORD_RE.findall(text)]

def frame_text(frame):
    return f"{frame.deliverable} {frame.results}"

def build_vectors(frames):
    docs = {f.frame_id: tokenize(frame_text(f)) for f in frames}
    n_docs = len(docs)
    doc_freq = Counter()
    for words in docs.values():
        doc_freq.update(set(words))
        
    vectors = {}
    for frame_id, words in docs.items():
        term_freq = Counter(words)
        vec = {}
        for word, tf in term_freq.items():
            idf = math.log((n_docs + 1) / (doc_freq[word] + 1)) + 1  # smoothed idf
            vec[word] = tf * idf
        vectors[frame_id] = vec
    return vectors

def cosine_similarity(vec_a, vec_b):
    shared_words = set(vec_a.keys()) & set(vec_b.keys())
    dot = sum(vec_a[w] * vec_b[w] for w in shared_words)
    norm_a = math.sqrt(sum(w * w for w in vec_a.values()))
    norm_b = math.sqrt(sum(w * w for w in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def similarity_search(frames):
    from itertools import combinations

    vectors = build_vectors(frames)
    results = {}
    for f1, f2 in combinations(frames, 2):
        sim = cosine_similarity(vectors[f1.frame_id], vectors[f2.frame_id])
        results[(f1.frame_id, f2.frame_id)] = sim
    return results

if __name__ == "__main__":
    from frame_data import ALL_FRAMES

    sims = similarity_search(ALL_FRAMES)
    top10 = sorted(sims.items(), key=lambda kv: kv[1], reverse=True)[:10]
    print("Top 10 most similar frame pairs (by TF-IDF cosine similarity):")
    for (i, j), sim in top10:
        print(f"  {i} <-> {j}: {sim:.3f}")
