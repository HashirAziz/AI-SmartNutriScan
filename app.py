import os
import uuid
from flask import Flask, request, jsonify, render_template
from PIL import Image

from model.clip_model import predict_food
from utils.validator import validate_image
from utils.nutrition import get_nutrition
from utils.scorer import calculate_health_score

app = Flask(__name__)

# Config
UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


# ─── Helpers ──────────────────────────────────────────────

def allowed_file(filename: str) -> bool:
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def save_uploaded_file(file) -> tuple[str, str]:
    """Save uploaded file with unique name. Returns (filepath, filename)."""
    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    file.save(filepath)
    return filepath, unique_name


# ─── Routes ───────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():

    # ── 1. File presence check ──
    if "image" not in request.files:
        return jsonify({
            "success": False,
            "error": "No image file provided."
        }), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({
            "success": False,
            "error": "No file selected."
        }), 400

    # ── 2. Extension check ──
    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "error": "Invalid file type. Allowed: PNG, JPG, JPEG, WEBP."
        }), 400

    # ── 3. Save file ──
    try:
        filepath, filename = save_uploaded_file(file)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to save image: {str(e)}"
        }), 500

    # ── 4. Load as PIL Image ──
    try:
        image = Image.open(filepath).convert("RGB")
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to process image: {str(e)}"
        }), 500

    # ── 5. CLIP Prediction ──
    try:
        prediction = predict_food(image)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Model prediction failed: {str(e)}"
        }), 500

    # ── 6. Confidence threshold check ──
    if not prediction["success"]:
        return jsonify({
            "success": False,
            "error": "Could not identify any food in this image. Please upload a clearer food photo.",
            "top3": prediction.get("predictions", [])
        }), 200

    predicted_label = prediction["food"]
    confidence      = prediction["confidence"]
    top3            = prediction["top3"]

    # ── 7. Image validation (face + non-food) ──
    validation = validate_image(image, predicted_label)

    if not validation["is_valid"]:
        return jsonify({
            "success": False,
            "error": validation["reason"]
        }), 200

    # ── 8. Nutrition lookup ──
    nutrition = get_nutrition(predicted_label)

    if not nutrition["found"]:
        return jsonify({
            "success": False,
            "error": f"'{predicted_label}' was detected but nutrition data is unavailable.",
            "food": predicted_label,
            "confidence": confidence
        }), 200

    # ── 9. Health score ──
    health = calculate_health_score(nutrition)

    # ── 10. Build final response ──
    response = {
        "success":    True,
        "food":       predicted_label.title(),
        "confidence": round(confidence * 100, 2),
        "image_url":  f"/static/uploads/{filename}",
        "top3":       [
            {
                "label":      item["label"].title(),
                "confidence": round(item["confidence"] * 100, 2)
            }
            for item in top3
        ],
        "nutrition": {
            "per_100g":    nutrition["per_100g"],
            "vitamins":    nutrition["vitamins"],
            "minerals":    nutrition["minerals"]
        },
        "dietary_tags":       nutrition["dietary_tags"],
        "disease_prevention": nutrition["disease_prevention"],
        "advice":             nutrition["advice"],
        "health_score": {
            "score":     health["score"],
            "label":     health["label"],
            "out_of":    10,
            "breakdown": health["breakdown"]
        }
    }

    return jsonify(response), 200


# ─── Error Handlers ───────────────────────────────────────

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        "success": False,
        "error": "Image too large. Maximum size is 10MB."
    }), 413


@app.errorhandler(500)
def server_error(e):
    return jsonify({
        "success": False,
        "error": "Internal server error."
    }), 500


# ─── Run ──────────────────────────────────────────────────

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)