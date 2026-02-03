# rag.py
# Basic local RAG using:
# - Ollama for embeddings + generation
# - FAISS for vector search
#
# Install:
#   pip install -r requirements.txt
#
# Usage:
#   python rag.py build --data_dir ./data --index_dir ./rag_index
#   python rag.py ask --index_dir ./rag_index --model llama3.1 --top_k 5
#
# Put .txt/.md files in ./data before building.

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Tuple

import numpy as np
import faiss
import ollama


DEFAULT_EMBED_MODEL = "nomic-embed-text"
DEFAULT_CHAT_MODEL = "ministral-3:3b-cloud"


@dataclass
class Chunk:
    chunk_id: str
    source: str
    text: str


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def clean_text(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def chunk_text(text: str, max_chars: int = 1500, overlap: int = 200) -> List[str]:
    """
    Simple character-based chunking with overlap.
    For a basic class RAG, this is sufficient and easy to reason about.
    """
    text = clean_text(text)
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + max_chars, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        start = max(0, end - overlap)

    return chunks


def ollama_embed(texts: List[str], embed_model: str) -> np.ndarray:
    """
    Returns embeddings as float32 matrix of shape (len(texts), dim).
    Normalizes vectors for cosine similarity with inner product search.
    """
    vectors: List[np.ndarray] = []
    for t in texts:
        resp = ollama.embeddings(model=embed_model, prompt=t)
        vec = np.array(resp["embedding"], dtype=np.float32)
        vectors.append(vec)

    mat = np.vstack(vectors)
    faiss.normalize_L2(mat)
    return mat


def build_index(data_dir: str, index_dir: str, embed_model: str) -> None:
    data_path = Path(data_dir)
    out_path = Path(index_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    files: List[Path] = []
    for ext in ("*.txt", "*.md"):
        files.extend(sorted(data_path.rglob(ext)))

    if not files:
        raise SystemExit(f"No .txt or .md files found under: {data_path.resolve()}")

    all_chunks: List[Chunk] = []
    for fp in files:
        text = read_text_file(fp)
        parts = chunk_text(text)
        for i, p in enumerate(parts):
            chunk_id = f"{fp.name}::chunk_{i:04d}"
            all_chunks.append(Chunk(chunk_id=chunk_id, source=str(fp), text=p))

    texts = [c.text for c in all_chunks]
    emb = ollama_embed(texts, embed_model=embed_model)

    dim = emb.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(emb)

    faiss.write_index(index, str(out_path / "faiss.index"))

    meta = {
        "embed_model": embed_model,
        "dim": dim,
        "chunks": [asdict(c) for c in all_chunks],
    }
    (out_path / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"Built index with {len(all_chunks)} chunks from {len(files)} files.")
    print(f"Saved: {(out_path / 'faiss.index').resolve()}")
    print(f"Saved: {(out_path / 'meta.json').resolve()}")


def load_index(index_dir: str) -> Tuple[faiss.Index, dict]:
    p = Path(index_dir)
    idx_path = p / "faiss.index"
    meta_path = p / "meta.json"

    if not idx_path.exists() or not meta_path.exists():
        raise SystemExit("Index not found. Run: python rag.py build --data_dir ./data --index_dir ./rag_index")

    index = faiss.read_index(str(idx_path))
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    return index, meta


def retrieve(index: faiss.Index, meta: dict, query: str, top_k: int) -> List[Chunk]:
    q_emb = ollama_embed([query], embed_model=meta["embed_model"])
    scores, ids = index.search(q_emb, top_k)

    results: List[Chunk] = []
    for i in ids[0].tolist():
        if i < 0:
            continue
        c = meta["chunks"][i]
        results.append(Chunk(chunk_id=c["chunk_id"], source=c["source"], text=c["text"]))
    return results


def format_context(chunks: List[Chunk]) -> str:
    lines: List[str] = []
    for j, c in enumerate(chunks, start=1):
        lines.append(f"[S{j}] id: {c.chunk_id}\nsource: {c.source}\ntext:\n{c.text}\n")
    return "\n".join(lines).strip()


def answer_with_citations(query: str, chunks: List[Chunk], chat_model: str) -> str:
    context = format_context(chunks)

    system = (
        "You are a helpful assistant. Use ONLY the SOURCES to answer.\n"
        "If the answer is not supported by the SOURCES, say: I don't know.\n"
        "Cite sources in square brackets like [S1], [S2]."
    )

    user = (
        f"SOURCES:\n{context}\n\n"
        f"QUESTION:\n{query}\n\n"
        "Return:\n"
        "1) Answer\n"
        "2) Citations"
    )

    resp = ollama.chat(
        model=chat_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp["message"]["content"]


def cmd_ask(index_dir: str, model: str, top_k: int) -> None:
    index, meta = load_index(index_dir)
    print("RAG ready. Type a question. Ctrl+C to exit.\n")

    while True:
        try:
            q = input("Q: ").strip()
            if not q:
                continue

            chunks = retrieve(index, meta, q, top_k=top_k)
            if not chunks:
                print("A: I don't know.\n")
                continue

            out = answer_with_citations(q, chunks, chat_model=model)
            print(f"\nA:\n{out}\n")
        except KeyboardInterrupt:
            print("\nBye.")
            return


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_build = sub.add_parser("build")
    p_build.add_argument("--data_dir", default="./data")
    p_build.add_argument("--index_dir", default="./rag_index")
    p_build.add_argument("--embed_model", default=DEFAULT_EMBED_MODEL)

    p_ask = sub.add_parser("ask")
    p_ask.add_argument("--index_dir", default="./rag_index")
    p_ask.add_argument("--model", default=DEFAULT_CHAT_MODEL)
    p_ask.add_argument("--top_k", type=int, default=5)

    args = parser.parse_args()

    if args.cmd == "build":
        build_index(args.data_dir, args.index_dir, args.embed_model)
    elif args.cmd == "ask":
        cmd_ask(args.index_dir, args.model, args.top_k)


if __name__ == "__main__":
    main()
