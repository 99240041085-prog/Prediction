from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# ─── Load Model ────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model.pkl')

model_final = None
le_tools = None
le_purpose = None

if not os.path.exists(MODEL_PATH):
    print(f"\n[ERROR] Model file not found at: {MODEL_PATH}")
    print("Please run 'python train_model.py' to generate the model first.\n")
else:
    try:
        model_data = joblib.load(MODEL_PATH)
        # Handle both dictionary keys if they exist, or direct keys
        # The training script saves: 'model_final', 'le_tools', 'le_purpose'
        model_final = model_data.get('model_final')
        le_tools = model_data.get('le_tools')
        le_purpose = model_data.get('le_purpose')
        
        print("[OK] Model loaded successfully!")
        if le_tools:
            print(f"   Tool classes:     {list(le_tools.classes_)}")
        if le_purpose:
            print(f"   Purpose classes:  {list(le_purpose.classes_)}")
            
    except Exception as e:
        print(f"\n[ERROR] Failed to load model: {e}")
        print("The model file might be corrupted or incompatible. Try running 'python train_model.py' again.\n")


@app.route('/')
def index():
    """Serve the main prediction UI."""
    if le_tools is None or le_purpose is None:
        return render_template('error.html', 
                             message="Model not loaded. Please run train_model.py first."), 500

    return render_template('index.html',
                           tools=list(le_tools.classes_),
                           purposes=list(le_purpose.classes_))


@app.route('/predict', methods=['POST'])
def predict():
    """Accept JSON input and return predictions with/without AI."""
    # Ensure model is loaded
    if not model_final or not le_tools or not le_purpose:
         return jsonify({'success': False, 'error': 'Model not loaded. Please run train_model.py.'}), 500

    try:
        data = request.get_json()
        print(f"DEBUG: Received data: {data}")

        # Extract inputs
        try:
            ai_tool = data.get('ai_tools_used', 'None')
            ai_purpose = data.get('ai_usage_purpose', 'None')
            ai_dependency = float(data.get('ai_dependency_score', 5))
            ai_content_pct = float(data.get('ai_generated_content_percentage', 50))
            last_exam = float(data.get('last_exam_score', 50))
            # assignment_scores_avg REMOVED
            ai_usage_hours = float(data.get('ai_usage_hours', 1.0)) # NEW INPUT
            study_consistency = float(data.get('study_consistency_index', 5))
            sleep = float(data.get('sleep_hours', 7))
        except ValueError as e:
            print(f"DEBUG: Error parsing inputs: {e}")
            return jsonify({'success': False, 'error': f'Invalid input format: {e}'}), 400

        print(f"DEBUG: Parsed last_exam: {last_exam}")

        # Encode categoricals using the loaded encoders
        try:
            tool_encoded = le_tools.transform([ai_tool])[0]
        except ValueError:
             tool_encoded = le_tools.transform([le_tools.classes_[0]])[0]

        try:
            purpose_encoded = le_purpose.transform([ai_purpose])[0]
        except ValueError:
            purpose_encoded = le_purpose.transform([le_purpose.classes_[0]])[0]


        # ── Feature vector ──
        # Order must match training script:
        # ai_tools_used_encoded, ai_usage_purpose_encoded, ai_dependency_score, 
        # ai_generated_content_percentage, last_exam_score, ai_usage_time_hours, 
        # study_consistency_index, sleep_hours
        
        features = np.array([[
            tool_encoded,
            purpose_encoded,
            ai_dependency,
            ai_content_pct,
            last_exam,
            ai_usage_hours,
            study_consistency,
            sleep
        ]])

        # ── Predict ──
        raw_prediction = model_final.predict(features)[0]
        
        # CONSTRAINT: Score with AI must be > last_exam_score
        # We ensure it's at least last_exam + 1, or raw_prediction if that's higher
        final_score_with_ai = max(raw_prediction, last_exam + 1)
        
        # Calculate impact based on the (possibly adjusted) score vs last exam
        ai_impact = final_score_with_ai - last_exam

        response_payload = {
            'success': True,
            'predictions': {
                'final_score_with_ai': round(float(final_score_with_ai), 2),
                'last_exam_score': round(float(last_exam), 2), # Returning input reference
                'ai_impact': round(float(ai_impact), 2),
                'passed_with_ai': 'Yes' if final_score_with_ai >= 40 else 'No',
            }
        }
        print(f"DEBUG: Sending response: {response_payload}")
        return jsonify(response_payload)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)
