import json
import pandas as pd
import numpy as np
import os

# ── Step 1 — Read JSONL file ──────────────────────────────────────────────
def read_jsonl(path: str) -> list:
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    print(f"Total records loaded: {len(records)}")
    return records


def assign_quality_score(prompt: str) -> float:
    score      = 0.2
    word_count = len(str(prompt).split())

    # Length scoring — more generous
    if word_count > 50:   score += 0.35
    elif word_count > 30: score += 0.25
    elif word_count > 15: score += 0.15
    elif word_count > 8:  score += 0.10
    else:                 score += 0.03

    # Role keywords
    role_keywords = ["you are", "act as", "as an expert",
                     "as a senior", "as a specialist"]
    if any(k in str(prompt).lower() for k in role_keywords):
        score += 0.20

    # Quality keywords
    quality_keywords = ["comprehensive", "detailed", "thorough",
                        "specific", "actionable", "step-by-step",
                        "analyze", "evaluate", "explain",
                        "describe", "compare", "impact", "why"]
    score += min(
        sum(1 for k in quality_keywords
            if k in str(prompt).lower()) * 0.05,
        0.20
    )

    # Question words — good prompts ask specific questions
    question_keywords = ["what", "how", "why", "when",
                         "where", "which", "who", "would",
                         "could", "should"]
    q_count = sum(1 for k in question_keywords
                  if k in str(prompt).lower().split())
    score += min(q_count * 0.03, 0.10)

    return float(np.clip(score, 0.1, 0.98))
    score      = 0.3
    word_count = len(str(prompt).split())

    if word_count > 100:  score += 0.25
    elif word_count > 50: score += 0.15
    elif word_count > 20: score += 0.08
    else:                 score += 0.02

    role_keywords = ["you are", "act as", "as an expert",
                     "as a senior", "as a specialist",
                     "as a professional", "as a researcher"]
    if any(k in str(prompt).lower() for k in role_keywords):
        score += 0.20

    quality_keywords = ["comprehensive", "detailed", "thorough",
                        "specific", "actionable", "step-by-step",
                        "in-depth", "structured", "systematic",
                        "analyze", "evaluate", "explain", "describe"]
    score += min(
        sum(1 for k in quality_keywords
            if k in str(prompt).lower()) * 0.04,
        0.15
    )

    format_keywords = ["list", "table", "steps", "format",
                       "structured", "outline", "sections",
                       "bullet", "numbered"]
    if any(k in str(prompt).lower() for k in format_keywords):
        score += 0.05

    example_keywords = ["example", "for instance",
                        "such as", "e.g", "including"]
    if any(k in str(prompt).lower() for k in example_keywords):
        score += 0.05

    return float(np.clip(score, 0.1, 0.98))


# ── Step 3 — Detect category ──────────────────────────────────────────────
def detect_category(text: str) -> str:
    text = str(text).lower()

    if any(w in text for w in ["code", "programming", "python",
                                "algorithm", "software", "api",
                                "developer", "database", "function"]):
        return "Coding"
    elif any(w in text for w in ["science", "research", "physics",
                                  "biology", "chemistry", "experiment",
                                  "hypothesis", "scientific", "universe"]):
        return "Science"
    elif any(w in text for w in ["business", "strategy", "startup",
                                  "revenue", "customer", "market",
                                  "sales", "profit", "investment"]):
        return "Business"
    elif any(w in text for w in ["teach", "learn", "education",
                                  "student", "curriculum", "lesson",
                                  "school", "course", "study"]):
        return "Education"
    elif any(w in text for w in ["story", "write", "creative",
                                  "fiction", "narrative", "character",
                                  "plot", "novel", "poem", "imagine"]):
        return "Creative Writing"
    elif any(w in text for w in ["philosophy", "ethics", "moral",
                                  "consciousness", "existence",
                                  "truth", "justice", "meaning"]):
        return "Philosophy"
    elif any(w in text for w in ["marketing", "campaign", "brand",
                                  "advertise", "social media",
                                  "viral", "audience", "content"]):
        return "Marketing"
    else:
        return "General"


# ── Step 4 — Extract topic from prompt ───────────────────────────────────
def extract_topic(prompt: str) -> str:
    prompt = str(prompt).strip()

    # Remove quotes
    prompt = prompt.strip('"').strip("'")

    # Take first 50 characters as topic
    words = prompt.split()
    if len(words) <= 6:
        return prompt
    return " ".join(words[:6])


# ── Step 5 — Convert JSONL to CSV ─────────────────────────────────────────
def convert_and_process(
    jsonl_path:  str,
    output_path: str,
    max_samples: int = 10000    # limit to 10000 for faster training
):
    print(f"Reading: {jsonl_path}")
    records = read_jsonl(jsonl_path)

    print(f"Processing {min(len(records), max_samples)} records...")

    rows = []
    for record in records[:max_samples]:
        prompt = str(record.get("response", "")).strip()
        prompt = prompt.strip('"').strip("'")

        if len(prompt) < 10:
            continue
        if prompt.lower() in ["nan", "none", "null", ""]:
            continue

        topic         = extract_topic(prompt)
        category      = detect_category(prompt)
        quality_score = assign_quality_score(prompt)

        rows.append({
            "topic":         topic,
            "category":      category,
            "prompt":        prompt,
            "quality_score": quality_score,
            "source":        "ai_generated_prompts"
        })

    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset=["prompt"])
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"\n{'='*50}")
    print(f"Saved           → {output_path}")
    print(f"Total samples   : {len(df)}")
    print(f"\nCategory distribution:")
    print(df["category"].value_counts().to_string())
    print(f"\nScore statistics:")
    print(df["quality_score"].describe().round(3).to_string())
    print(f"{'='*50}")

    return df


# ── Step 6 — Merge with generated dataset ────────────────────────────────
def merge_with_generated(
    jsonl_csv_path: str,
    generated_path: str,
    output_path:    str
):
    jsonl_df     = pd.read_csv(jsonl_csv_path)
    generated_df = pd.read_csv(generated_path)

    merged = pd.concat(
        [jsonl_df, generated_df],
        ignore_index=True
    )
    merged = merged.drop_duplicates(subset=["prompt"])
    merged = merged.sample(
        frac=1, random_state=42
    ).reset_index(drop=True)

    merged.to_csv(output_path, index=False)

    print(f"\nFinal merged dataset:")
    print(f"JSONL samples     : {len(jsonl_df)}")
    print(f"Generated samples : {len(generated_df)}")
    print(f"Total samples     : {len(merged)}")
    print(f"Saved             → {output_path}")

    return merged


if __name__ == "__main__":

    jsonl_path = r"C:\Users\anshi\Downloads\archive (1)\data.jsonl"

    # Step 1 — Convert JSONL to CSV
    convert_and_process(
        jsonl_path  = jsonl_path,
        output_path = "dataset/jsonl_processed.csv",
        max_samples = 10000
    )

    # Step 2 — Generate base dataset
    print("\nGenerating base dataset...")
    os.system("python dataset/generate_dataset.py")

    # Step 3 — Merge both
    merge_with_generated(
        jsonl_csv_path = "dataset/jsonl_processed.csv",
        generated_path = "dataset/prompts.csv",
        output_path    = "dataset/final_dataset.csv"
    )