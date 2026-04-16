import re
import numpy as np
from typing import Dict

CATEGORY_MAP = {
    "General":          0,
    "Creative Writing": 1,
    "Coding":           2,
    "Business":         3,
    "Education":        4,
    "Marketing":        5,
    "Science":          6,
    "Philosophy":       7
}

ROLE_KEYWORDS = [
    "you are", "act as", "as an expert",
    "as a senior", "as a specialist",
    "as a professional", "as a researcher",
    "as a consultant", "as a professor"
]

QUALITY_KEYWORDS = [
    "comprehensive", "detailed", "thorough",
    "systematic", "specific", "actionable",
    "practical", "evidence-based", "step-by-step",
    "in-depth", "rigorous", "measurable",
    "structured", "analyze", "evaluate"
]

CONSTRAINT_KEYWORDS = [
    "must", "should", "avoid", "only",
    "always", "never", "ensure", "focus on",
    "make sure", "do not", "include", "exclude"
]

FORMAT_KEYWORDS = [
    "list", "table", "steps", "format",
    "json", "markdown", "bullet", "numbered",
    "structured", "section", "outline"
]

EXAMPLE_KEYWORDS = [
    "example", "for instance", "such as",
    "e.g", "including", "like", "specifically"
]

CONTEXT_KEYWORDS = [
    "context", "background", "given that",
    "considering", "taking into account",
    "assuming", "based on"
]


def extract_features(
    prompt: str,
    topic: str,
    category: str
) -> Dict[str, float]:

    prompt_lower = prompt.lower()
    words        = prompt.split()
    sentences    = re.split(r'[.!?]+', prompt)

    return {
        "length":
            len(prompt),
        "word_count":
            len(words),
        "sentence_count":
            len([s for s in sentences if s.strip()]),
        "avg_word_length":
            float(np.mean([len(w) for w in words]))
            if words else 0,
        "vocabulary_richness":
            len(set(prompt_lower.split()))
            / max(len(words), 1),

        "has_role":
            int(any(k in prompt_lower for k in ROLE_KEYWORDS)),
        "has_context":
            int(any(k in prompt_lower for k in CONTEXT_KEYWORDS)),
        "has_constraints":
            int(any(k in prompt_lower for k in CONSTRAINT_KEYWORDS)),
        "has_output_format":
            int(any(k in prompt_lower for k in FORMAT_KEYWORDS)),
        "has_examples":
            int(any(k in prompt_lower for k in EXAMPLE_KEYWORDS)),
        "quality_keyword_count":
            sum(1 for k in QUALITY_KEYWORDS if k in prompt_lower),

        "question_count":
            prompt.count("?"),
        "has_numbers":
            int(any(c.isdigit() for c in prompt)),
        "comma_count":
            prompt.count(","),
        "specificity_score":
            len(set(words)) / max(len(words), 1),

        "topic_word_count":
            len(str(topic).split()),
        "topic_in_prompt":
            int(str(topic).lower() in prompt_lower),
        "category_encoded":
            CATEGORY_MAP.get(category, 0),
        "category_topic_match":
            int(category.lower() in prompt_lower),
    }


def extract_features_list(
    prompt: str,
    topic: str,
    category: str
) -> list:
    return list(
        extract_features(prompt, topic, category).values()
    )