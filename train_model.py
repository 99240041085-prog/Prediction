import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
import os

# ─── Load Dataset ───────────────────────────────────────────────
DATASET_PATH = r"c:\Users\chund\Downloads\ai_impact_student_performance_dataset.csv"
print(f"Loading dataset from {DATASET_PATH}...")
df = pd.read_csv(DATASET_PATH)
print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns\n")

# ─── Feature Engineering ────────────────────────────────────────
# Input features the user will provide
input_features = [
    'ai_tools_used',
    'ai_usage_purpose',
    'ai_dependency_score',
    'ai_generated_content_percentage',
    'last_exam_score',
    'ai_usage_time_hours',  # NEW FEATURE
    'study_consistency_index',
    'sleep_hours'
]

# Target
target = 'final_score'

# ─── Encode Categorical Features ───────────────────────────────
le_tools = LabelEncoder()
le_purpose = LabelEncoder()

# Fill NaN with 'None' string before encoding so it becomes a valid class
df['ai_tools_used'] = df['ai_tools_used'].fillna('None').astype(str)
df['ai_usage_purpose'] = df['ai_usage_purpose'].fillna('None').astype(str)

df['ai_tools_used_encoded'] = le_tools.fit_transform(df['ai_tools_used'])
df['ai_usage_purpose_encoded'] = le_purpose.fit_transform(df['ai_usage_purpose'])

# Create new feature: ai_usage_time_hours
if 'ai_usage_time_minutes' in df.columns:
    df['ai_usage_time_hours'] = df['ai_usage_time_minutes'] / 60.0
else:
    # Fallback if column missing (though we verified it exists)
    print("Warning: 'ai_usage_time_minutes' not found. Creating dummy column.")
    df['ai_usage_time_hours'] = 0.0

# Build feature matrix with encoded categoricals
feature_cols = [
    'ai_tools_used_encoded',
    'ai_usage_purpose_encoded',
    'ai_dependency_score',
    'ai_generated_content_percentage',
    'last_exam_score',
    'ai_usage_time_hours',
    'study_consistency_index',
    'sleep_hours'
]

X = df[feature_cols].values

# ─── Train/Test Split ──────────────────────────────────────────
y_final = df[target].values

X_train, X_test, y_train, y_test = train_test_split(X, y_final, test_size=0.2, random_state=42)

# ─── Train Model ───────────────────────────────────────────────
print("Training Final Score model (RandomForestRegressor)...")
model_final = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
model_final.fit(X_train, y_train)
pred = model_final.predict(X_test)
print(f"  R² Score:  {r2_score(y_test, pred):.4f}")
print(f"  MAE:       {mean_absolute_error(y_test, pred):.4f}\n")

# ─── Save Model & Encoders ────────────────────────────────────
model_data = {
    'model_final': model_final,
    'le_tools': le_tools,
    'le_purpose': le_purpose,
    'feature_cols': feature_cols,
    'tools_classes': list(le_tools.classes_),
    'purpose_classes': list(le_purpose.classes_),
}

save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model.pkl')
joblib.dump(model_data, save_path)
print(f"[OK] Model and encoders saved to {save_path}")
print(f"\nTool classes:     {model_data['tools_classes']}")
print(f"Purpose classes:  {model_data['purpose_classes']}")
