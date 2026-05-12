import sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))

import pandas as pd
from datetime import datetime
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.config import Config
from src.rag.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

QA_PAIRS = [
    {"question": "What was the ECB deposit facility rate in December 2024?", "ground_truth": "3.00%"},
    {"question": "By how many basis points did ECB cut rates in 2024?", "ground_truth": "100 basis points"},
    {"question": "What was headline inflation in the euro area in December 2024?", "ground_truth": "2.4%"},
    {"question": "What was core inflation at its peak in 2023?", "ground_truth": "7.6% in March 2023"},
    {"question": "What is the ECB inflation target?", "ground_truth": "2%"},
    {"question": "What percentage of ECB total assets were monetary policy securities?", "ground_truth": "59%"},
    {"question": "What was the total value of euro banknotes in circulation end of 2024?", "ground_truth": "1588.3 billion euros"},
    {"question": "What share of euro banknotes is allocated to the ECB?", "ground_truth": "8%"},
    {"question": "What is the PEPP program?", "ground_truth": "Pandemic emergency purchase programme"},
    {"question": "What is the TPI?", "ground_truth": "Transmission protection instrument approved July 2022"},
    {"question": "How many significant institutions are directly supervised by ECB?", "ground_truth": "22"},
    {"question": "What is FINREP?", "ground_truth": "Financial reporting framework for credit institutions"},
    {"question": "What is the SMP program?", "ground_truth": "Securities Markets Programme"},
    {"question": "What is the ABSPP?", "ground_truth": "Asset-backed securities purchase programme"},
    {"question": "What did ECB say about housing investment in 2024?", "ground_truth": "fell 4.0 percent largest decline since 2009"},
    {"question": "What are the three main financial stability risks in November 2025?", "ground_truth": "asset valuations sovereign debt credit risk tariffs"},
    {"question": "What did BaFin focus on in AML audits in 2023?", "ground_truth": "risk analysis due diligence IT monitoring"},
    {"question": "What is MaRisk?", "ground_truth": "Minimum Requirements for Risk Management for Banks"},
    {"question": "What is global trade growth in 2024?", "ground_truth": "4.4%"},
    {"question": "What is the ECB APP?", "ground_truth": "Asset purchase programme"},
]

def run_rag(question, embeddings, chroma_dir, llm):
    db = Chroma(persist_directory=chroma_dir, embedding_function=embeddings)
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})
    docs = retriever.invoke(question)
    context = "\n\n".join([
        f"[Source: {d.metadata.get('source','?')}, Page {d.metadata.get('page','?')}]\n{d.page_content}"
        for d in docs
    ])
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", USER_PROMPT_TEMPLATE)
    ])
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})
    return {"answer": answer, "contexts": [d.page_content for d in docs]}

def simple_score(answer, ground_truth):
    gt_words = set(ground_truth.lower().split())
    ans_words = set(answer.lower().split())
    if not gt_words:
        return 0.0
    return round(len(gt_words & ans_words) / len(gt_words), 3)

config = Config()
llm = ChatOllama(model="mistral", base_url="http://localhost:11434", temperature=0.1)

MODELS = {
    "baseline": {
        "label": "Baseline (all-MiniLM-L6-v2)",
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "chroma_dir": "data/processed/chroma_minilm",
    },
    "improved": {
        "label": "Improved (Jina-DE v2)",
        "model_name": "jinaai/jina-embeddings-v2-base-de",
        "chroma_dir": "data/processed/chroma",
    },
}

all_results = {}

for model_key, model_cfg in MODELS.items():
    print(f"\n{'='*60}")
    print(f"Running: {model_cfg['label']}")
    print(f"{'='*60}")
    embeddings = HuggingFaceEmbeddings(
        model_name=model_cfg["model_name"],
        encode_kwargs={"normalize_embeddings": True},
    )
    scores, latencies = [], []
    for i, qa in enumerate(QA_PAIRS):
        print(f"  Q{i+1:02d}: {qa['question'][:55]}...")
        t0 = datetime.now()
        try:
            result = run_rag(qa["question"], embeddings, model_cfg["chroma_dir"], llm)
            latency = (datetime.now() - t0).total_seconds()
            score = simple_score(result["answer"], qa["ground_truth"])
            scores.append(score)
            latencies.append(latency)
            print(f"       Score: {score:.3f} | {latency:.1f}s")
        except Exception as e:
            print(f"       ERROR: {e}")
            scores.append(0.0)
            latencies.append(0.0)
    all_results[model_key] = {
        "label": model_cfg["label"],
        "avg_score": sum(scores)/len(scores),
        "p50": sorted(latencies)[len(latencies)//2],
        "p95": sorted(latencies)[int(len(latencies)*0.95)],
        "scores": scores,
        "latencies": latencies,
    }

print(f"\n{'='*65}")
print("EVAL RESULTS — BASELINE vs IMPROVED")
print(f"{'='*65}")
print(f"{'Model':<32} {'Avg Score':>10} {'p50 (s)':>9} {'p95 (s)':>9}")
print(f"{'-'*65}")
for k, r in all_results.items():
    print(f"{r['label']:<32} {r['avg_score']:>10.3f} {r['p50']:>9.1f} {r['p95']:>9.1f}")
print(f"{'='*65}")

rows = []
for k, r in all_results.items():
    for i, qa in enumerate(QA_PAIRS):
        rows.append({
            "model": r["label"],
            "question": qa["question"],
            "ground_truth": qa["ground_truth"],
            "score": r["scores"][i],
            "latency_s": r["latencies"][i],
        })
pd.DataFrame(rows).to_csv("evals/ragas_results.csv", index=False)
print("\nSaved: evals/ragas_results.csv")