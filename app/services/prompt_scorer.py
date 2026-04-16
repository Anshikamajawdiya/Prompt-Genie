import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import joblib
import numpy as np
import pandas as pd
import warnings
from model.feature_extraction import extract_features

class PromptScorer:

    def __init__(self):
        base_dir    = os.path.dirname(
            os.path.dirname(os.path.dirname(__file__))
        )
        model_path  = os.path.join(base_dir, "model", "prompt_scorer.pkl")
        scaler_path = os.path.join(base_dir, "model", "scaler.pkl")

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found: {model_path}\n"
                f"Run: python model/train_model.py"
            )

        self.model  = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)

    def score(self, prompt: str, topic: str, category: str) -> float:
        # ← Use DataFrame instead of list to keep column names
        features    = extract_features(prompt, topic, category)
        features_df = pd.DataFrame([features])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            scaled = self.scaler.transform(features_df)
            score  = self.model.predict(scaled)[0]

        return float(np.clip(score, 0.0, 1.0))

    def best_prompt(
        self,
        candidates: list,
        topic: str,
        category: str
    ) -> tuple:
        scored = [
            (c, self.score(c, topic, category))
            for c in candidates
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0]