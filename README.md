# 🥗 AI-SmartNutriScan — AI-Powered Food Nutrition Analyzer

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0.3-black?style=flat-square&logo=flask)
![PyTorch](https://img.shields.io/badge/PyTorch-2.3.1-red?style=flat-square&logo=pytorch)
![CLIP](https://img.shields.io/badge/OpenAI-CLIP-412991?style=flat-square&logo=openai)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

> Upload a food photo and instantly get AI-powered nutrition analysis, health scoring, and personalized dietary advice — powered by OpenAI CLIP zero-shot classification.

---

## 📸 Demo

> Upload any food image → AI detects it → Get full nutrition breakdown in seconds.

![Demo Screenshot](static/demo.png)

---

## ✨ Features

- 🔍 **Zero-Shot Food Classification** — Uses OpenAI CLIP to identify 50+ foods without retraining
- 🛡️ **Smart Image Validation** — Rejects selfies (face detection via OpenCV Haar Cascade) and non-food images
- 📊 **Detailed Nutrition Data** — Calories, protein, carbs, fat, fiber, sugar per 100g
- 💯 **Health Score** — AI-calculated score out of 10 based on macro analysis
- 🏷️ **Dietary Tags** — Vegan, Keto, High Protein, Gluten-Free, and more
- 🛡️ **Disease Prevention Info** — Evidence-based health benefits per food
- 💡 **Personalized Advice** — Consumption tips tailored to each food
- 📷 **Camera Capture** — Analyze food directly from your webcam
- 🐳 **Dockerized** — Fully containerized for easy deployment

---

## 🧠 How It Works
```
User Uploads Image
        │
        ▼
 Face Detected? ──── YES ──→ ❌ Reject: Selfie
        │ NO
        ▼
 CLIP Zero-Shot Classification
        │
        ▼
 Confidence >= 18%? ─ NO ──→ ❌ Reject: Not identifiable
        │ YES
        ▼
 Non-Food Label? ──── YES ──→ ❌ Reject: Not food
        │ NO
        ▼
 Nutrition Lookup (JSON DB)
        │
        ▼
 Health Score Calculation
        │
        ▼
 ✅ Full Nutrition Report Returned
```

---

## 🗂️ Project Structure
```
AI-SmartNutriScan/
├── app.py                  # Flask API + routes
├── Dockerfile              # Container config
├── requirements.txt        # Dependencies
├── model/
│   ├── __init__.py
│   └── clip_model.py       # CLIP zero-shot classifier
├── utils/
│   ├── __init__.py
│   ├── validator.py        # Face + non-food detection
│   ├── nutrition.py        # Nutrition DB lookup
│   └── scorer.py           # Health score logic
├── data/
│   └── nutrition_db.json   # 30+ foods nutrition database
├── static/
│   ├── css/style.css       # Frontend styling
│   ├── js/main.js          # Frontend logic
│   └── uploads/            # Uploaded images
└── templates/
    └── index.html          # Frontend UI
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| AI Model | OpenAI CLIP (ViT-B/32) via HuggingFace |
| Image Validation | OpenCV Haar Cascade |
| Backend | Python, Flask |
| Deep Learning | PyTorch, HuggingFace Transformers |
| Nutrition Data | Custom JSON Database |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Containerization | Docker |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Docker (optional)
- Git

### Local Setup
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/AI-SmartNutriScan.git
cd AI-SmartNutriScan

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install torch==2.3.1+cpu torchvision==0.18.1+cpu \
  --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# Run the app
python app.py
```

Open `http://localhost:5000` in your browser.

---

### Docker Setup
```bash
# Build image
docker build -t ai-smartnutriscan .

# Run container
docker run -p 5000:5000 ai-smartnutriscan
```

---

## 📡 API Reference

### `POST /predict`

**Request:** `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| image | File | Food image (JPG, PNG, WEBP, max 10MB) |

**Success Response:**
```json
{
  "success": true,
  "food": "Grilled Chicken",
  "confidence": 87.3,
  "nutrition": {
    "per_100g": {
      "calories": 165,
      "protein": 31,
      "carbs": 0,
      "fat": 3.6,
      "fiber": 0,
      "sugar": 0
    },
    "vitamins": ["Vitamin B6", "Vitamin B12"],
    "minerals": ["Phosphorus", "Selenium"]
  },
  "dietary_tags": ["High Protein", "Low Fat", "Keto", "Gluten-Free"],
  "health_score": {
    "score": 8.5,
    "label": "Excellent",
    "out_of": 10
  },
  "disease_prevention": ["Supports muscle growth", "Boosts metabolism"],
  "advice": "One of the best lean protein sources. Ideal post-workout meal."
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Selfie or human face detected. Please upload a food image."
}
```

---

## 🍽️ Supported Foods (50+)

| Category | Foods |
|---|---|
| Fruits | Apple, Banana, Orange, Mango, Grapes, Strawberry, Watermelon, Pineapple, Avocado, Blueberry |
| Fast Food | Pizza, Burger, Sandwich, Hotdog, French Fries, Tacos, Burrito, Samosa |
| Proteins | Grilled Chicken, Fried Chicken, Steak, Salmon, Shrimp, Omelette |
| Grains | Rice, Pasta, Bread, Chapati, Pancakes, Waffles |
| Desserts | Chocolate Cake, Ice Cream, Donut, Cookie, Brownie, Cheesecake |
| South Asian | Biryani, Dal, Chapati, Samosa |
| Others | Salad, Sushi, Soup, Yogurt, Cheese |

---

## 👨‍💻 Author

**Hashir** — AI Engineer & Full Stack Developer
- 🎓 BS Artificial Intelligence — NUML Islamabad
- 💼 Ex-Intern @ Telenor Pakistan (AI/Voicebot) & Bytewise Limited (ML/DL)
- 🔗 [LinkedIn](https://linkedin.com/in/YOUR_PROFILE)
- 💻 [GitHub](https://github.com/YOUR_USERNAME)
- 🛒 [Fiverr](https://fiverr.com/YOUR_PROFILE)

---

## 📄 License

This project is licensed under the MIT License — for educational and portfolio use.

---

> ⭐ If you found this project useful, please give it a star on GitHub!