import pandas as pd
import numpy as np
import joblib
import os
import sys

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from model.feature_extraction import extract_features
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler


def load_dataset(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"Dataset loaded    : {len(df)} samples")
    print(f"Columns           : {df.columns.tolist()}")
    print(f"Category counts   :\n{df['category'].value_counts()}")
    print(f"Score stats       :\n{df['quality_score'].describe()}")
    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    print("\nExtracting features...")
    feature_list = []

    for i, (_, row) in enumerate(df.iterrows()):
        features = extract_features(
            str(row["prompt"]),
            str(row["topic"]),
            str(row["category"])
        )
        feature_list.append(features)

        if (i + 1) % 1000 == 0:
            print(f"  Processed {i + 1} / {len(df)}")

    return pd.DataFrame(feature_list)


def train():
    os.makedirs("model", exist_ok=True)

    # ── Load dataset ──────────────────────────────────────────────────
    dataset_path = "dataset/final_dataset.csv"

    if not os.path.exists(dataset_path):
        dataset_path = "dataset/prompts.csv"
        print(f"final_dataset not found, using {dataset_path}")

    df = load_dataset(dataset_path)

    # ── Build features ────────────────────────────────────────────────
    X = build_features(df)
    y = df["quality_score"]

    print(f"\nFeatures shape : {X.shape}")
    print(f"Feature names  : {X.columns.tolist()}")

    # ── Split data ────────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size    = 0.2,
        random_state = 42
    )

    print(f"\nTraining samples : {len(X_train)}")
    print(f"Testing samples  : {len(X_test)}")

    # ── Scale features ────────────────────────────────────────────────
    scaler         = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    # ── Train model ───────────────────────────────────────────────────
    print("\nTraining model...")
    model = GradientBoostingRegressor(
        n_estimators      = 300,
        learning_rate     = 0.05,
        max_depth         = 5,
        min_samples_split = 10,
        subsample         = 0.8,
        random_state      = 42
    )

    model.fit(X_train_scaled, y_train)

    # ── Evaluate ──────────────────────────────────────────────────────
    y_pred = model.predict(X_test_scaled)
    mse    = mean_squared_error(y_test, y_pred)
    rmse   = np.sqrt(mse)
    r2     = r2_score(y_test, y_pred)

    print(f"\nModel Performance:")
    print(f"MSE  : {mse:.4f}")
    print(f"RMSE : {rmse:.4f}")
    print(f"R2   : {r2:.4f}")

    # ── Cross validation ──────────────────────────────────────────────
    print("\nRunning cross validation...")
    cv_scores = cross_val_score(
        GradientBoostingRegressor(
            n_estimators  = 100,
            random_state  = 42
        ),
        scaler.transform(X), y,
        cv      = 5,
        scoring = "r2"
    )
    print(f"CV R2 : {cv_scores.mean():.4f} "
          f"(+/- {cv_scores.std():.4f})")

    # ── Feature importance ────────────────────────────────────────────
    importance_df = pd.DataFrame({
        "feature":    X.columns,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False)

    print(f"\nTop 10 Features:")
    print(importance_df.head(10).to_string(index=False))

    # ── Save model ────────────────────────────────────────────────────
    model_path  = "model/prompt_scorer.pkl"
    scaler_path = "model/scaler.pkl"

    joblib.dump(model,  model_path)
    joblib.dump(scaler, scaler_path)

    print(f"\nModel saved  → {model_path}")
    print(f"Scaler saved → {scaler_path}")
    print("\nTraining complete ✅")


if __name__ == "__main__":
    train()