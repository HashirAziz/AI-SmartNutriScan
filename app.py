import os
import uuid
import streamlit as st
from PIL import Image

from model.clip_model import predict_food
from utils.validator import validate_image
from utils.nutrition import get_nutrition
from utils.scorer import calculate_health_score

# ── Page Config ───────────────────────────────────────────

st.set_page_config(
    page_title="AI-SmartNutriScan",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

.main { background: #f0fdf4; }

.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    color: #1a1a2e;
    line-height: 1.2;
    margin-bottom: 8px;
}

.hero-title span { color: #22c55e; }

.hero-sub {
    color: #6b7280;
    font-size: 1rem;
    margin-bottom: 32px;
}

.result-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.food-title {
    font-size: 2rem;
    font-weight: 800;
    color: #16a34a;
    margin: 0;
}

.confidence-text {
    color: #6b7280;
    font-size: 0.85rem;
    font-weight: 500;
}

.score-excellent { color: #22c55e; font-size: 2rem; font-weight: 800; }
.score-good      { color: #3b82f6; font-size: 2rem; font-weight: 800; }
.score-moderate  { color: #f97316; font-size: 2rem; font-weight: 800; }
.score-poor      { color: #ef4444; font-size: 2rem; font-weight: 800; }

.tag {
    display: inline-block;
    background: #dcfce7;
    color: #16a34a;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    margin: 3px;
}

.advice-box {
    background: linear-gradient(135deg, #fffbeb, #fef3c7);
    border-radius: 12px;
    padding: 16px 20px;
    border-left: 4px solid #eab308;
    margin-top: 8px;
}

.benefit-item {
    background: #f0fdf4;
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 8px;
    border: 1px solid #e5e7eb;
    font-size: 0.88rem;
    font-weight: 500;
}

.section-header {
    font-size: 0.95rem;
    font-weight: 700;
    color: #1a1a2e;
    margin: 20px 0 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.nutr-box {
    background: #f0fdf4;
    border-radius: 12px;
    padding: 16px 10px;
    text-align: center;
    border: 1px solid #e5e7eb;
}

.nutr-val {
    font-size: 1.4rem;
    font-weight: 800;
    color: #16a34a;
}

.nutr-lbl {
    font-size: 0.75rem;
    color: #6b7280;
    font-weight: 500;
}

.error-box {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 10px;
    padding: 16px 20px;
    color: #ef4444;
    font-weight: 500;
}

.top3-item {
    background: #f9fafb;
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 8px;
    border: 1px solid #e5e7eb;
}

.stButton > button {
    background: #22c55e !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 28px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    width: 100% !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    background: #16a34a !important;
    transform: translateY(-1px) !important;
}

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Hero Section ──────────────────────────────────────────

st.markdown("""
<div style='text-align:center; padding: 40px 0 20px;'>
    <div class='hero-title'>🥗 Scan Your Food.<br/><span>Know What You Eat.</span></div>
    <div class='hero-sub'>Upload a food photo and get instant AI-powered nutrition analysis</div>
</div>
""", unsafe_allow_html=True)


# ── Upload Section ────────────────────────────────────────

uploaded_file = st.file_uploader(
    "Upload a food image",
    type=["jpg", "jpeg", "png", "webp"],
    help="Max 10MB · JPG, PNG, WEBP supported"
)

camera_file = st.camera_input("Or capture from camera")

# Determine active input
active_file = uploaded_file if uploaded_file else camera_file

# ── Analyze Button ────────────────────────────────────────

if active_file:
    image = Image.open(active_file).convert("RGB")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(image, caption="Your Image", use_column_width=True)

    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        analyze = st.button("🔍 Analyze Food")

    if analyze:

        # ── Loading ──
        with st.spinner("Analyzing your food with AI..."):

            # ── CLIP Prediction ──
            prediction = predict_food(image)

            if not prediction["success"]:
                st.markdown("""
                <div class='error-box'>
                    ❌ Could not identify any food in this image.
                    Please upload a clearer food photo.
                </div>
                """, unsafe_allow_html=True)
                st.stop()

            predicted_label = prediction["food"]
            confidence      = prediction["confidence"]
            top3            = prediction["top3"]

            # ── Validation ──
            validation = validate_image(image, predicted_label)

            if not validation["is_valid"]:
                st.markdown(f"""
                <div class='error-box'>❌ {validation['reason']}</div>
                """, unsafe_allow_html=True)
                st.stop()

            # ── Nutrition ──
            nutrition = get_nutrition(predicted_label)

            if not nutrition["found"]:
                st.markdown(f"""
                <div class='error-box'>
                    ❌ '{predicted_label}' detected but nutrition data unavailable.
                </div>
                """, unsafe_allow_html=True)
                st.stop()

            # ── Health Score ──
            health = calculate_health_score(nutrition)

        # ── Results ──────────────────────────────────────

        st.success("✅ Food successfully identified!")
        st.markdown("<br/>", unsafe_allow_html=True)

        # ── Food Header ──
        score_class = (
            "score-excellent" if health["score"] >= 8 else
            "score-good"      if health["score"] >= 6 else
            "score-moderate"  if health["score"] >= 4 else
            "score-poor"
        )

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(image, use_column_width=True)
        with col2:
            st.markdown(f"""
            <div style='padding: 10px 0;'>
                <p style='color:#6b7280; font-size:0.78rem; font-weight:600;
                          text-transform:uppercase; letter-spacing:1px;'>
                    Detected Food
                </p>
                <p class='food-title'>{predicted_label.title()}</p>
                <p class='confidence-text'>Confidence: <strong>{round(confidence * 100, 1)}%</strong></p>
            </div>
            """, unsafe_allow_html=True)

            st.progress(confidence)

        st.markdown("---")

        # ── Health Score ──
        st.markdown("### 💯 Health Score")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div style='text-align:center; background:linear-gradient(135deg,#f0fdf4,#dcfce7);
                        border-radius:16px; padding:24px;'>
                <div class='{score_class}'>{health["score"]}</div>
                <div style='color:#6b7280; font-size:0.8rem;'>out of 10</div>
                <div style='color:#16a34a; font-weight:700; margin-top:4px;'>
                    {health["label"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            bd = health["breakdown"]
            st.metric("Calories", f"{bd['calories']} kcal")
            st.metric("Protein",  f"{bd['protein']}g")

        with col3:
            st.metric("Fat",   f"{bd['fat']}g")
            st.metric("Sugar", f"{bd['sugar']}g")
            st.metric("Fiber", f"{bd['fiber']}g")

        st.markdown("---")

        # ── Nutrition Grid ──
        st.markdown("### 📊 Nutrition Per 100g")
        n = nutrition["per_100g"]
        c1, c2, c3, c4, c5, c6 = st.columns(6)

        for col, label, value, unit in zip(
            [c1, c2, c3, c4, c5, c6],
            ["Calories", "Protein", "Carbs", "Fat", "Fiber", "Sugar"],
            [n["calories"], n["protein"], n["carbs"], n["fat"], n["fiber"], n["sugar"]],
            ["kcal", "g", "g", "g", "g", "g"]
        ):
            with col:
                st.markdown(f"""
                <div class='nutr-box'>
                    <div class='nutr-val'>{value}<span style='font-size:0.7rem;color:#6b7280'>{unit}</span></div>
                    <div class='nutr-lbl'>{label}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # ── Dietary Tags ──
        st.markdown("### 🏷️ Dietary Tags")
        tags_html = " ".join([f"<span class='tag'>{t}</span>" for t in nutrition["dietary_tags"]])
        st.markdown(tags_html, unsafe_allow_html=True)

        st.markdown("---")

        # ── Vitamins & Minerals ──
        st.markdown("### 💊 Vitamins & Minerals")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Vitamins**")
            for v in nutrition["vitamins"]:
                st.markdown(f"✅ {v}")

        with col2:
            st.markdown("**Minerals**")
            for m in nutrition["minerals"]:
                st.markdown(f"⚡ {m}")

        st.markdown("---")

        # ── Disease Prevention ──
        st.markdown("### 🛡️ Disease Prevention")
        for d in nutrition["disease_prevention"]:
            st.markdown(f"""
            <div class='benefit-item'>🛡️ {d}</div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ── Advice ──
        st.markdown("### 💡 Personalized Advice")
        st.markdown(f"""
        <div class='advice-box'>
            <strong>💡 Tip:</strong> {nutrition['advice']}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ── Top 3 Predictions ──
        st.markdown("### 🧠 AI Top Predictions")
        for i, item in enumerate(top3):
            st.markdown(f"""
            <div class='top3-item'>
                <strong>#{i+1}</strong> {item['label'].title()}
                &nbsp;·&nbsp;
                <span style='color:#16a34a; font-weight:700;'>
                    {round(item['confidence'] * 100, 1)}%
                </span>
            </div>
            """, unsafe_allow_html=True)
            st.progress(item["confidence"])

        st.markdown("<br/>", unsafe_allow_html=True)
        st.info("📸 Upload another image above to scan a new food!")

else:
    st.markdown("""
    <div style='text-align:center; padding:40px; background:white;
                border-radius:16px; border: 2px dashed #22c55e;
                color:#6b7280; margin-top:20px;'>
        <div style='font-size:3rem;'>🍽️</div>
        <div style='font-size:1rem; font-weight:600; margin-top:12px;'>
            Upload a food image or use your camera to get started
        </div>
        <div style='font-size:0.82rem; margin-top:8px;'>
            Supports JPG, PNG, WEBP · Max 10MB
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────

st.markdown("""
<br/><hr/>
<div style='text-align:center; color:#6b7280; font-size:0.78rem; padding:16px 0;'>
    AI-SmartNutriScan · Built with CLIP + Streamlit · For educational use only
</div>
""", unsafe_allow_html=True)