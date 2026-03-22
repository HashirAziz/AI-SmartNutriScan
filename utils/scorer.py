def calculate_health_score(nutrition: dict) -> dict:
    """
    Calculates a health score out of 10 based on macro and micro nutrition.
    Higher fiber, protein = good
    Higher sugar, fat, calories = penalty
    """
    if not nutrition.get("found"):
        return {"score": None, "label": "Unknown", "breakdown": {}}

    per100 = nutrition["per_100g"]

    calories = per100["calories"]
    protein  = per100["protein"]
    carbs    = per100["carbs"]
    fat      = per100["fat"]
    fiber    = per100["fiber"]
    sugar    = per100["sugar"]

    score = 10.0

    # Calorie penalty
    if calories > 350:
        score -= 2.5
    elif calories > 250:
        score -= 1.5
    elif calories > 150:
        score -= 0.5

    # Fat penalty
    if fat > 20:
        score -= 2.0
    elif fat > 10:
        score -= 1.0

    # Sugar penalty
    if sugar > 20:
        score -= 2.0
    elif sugar > 10:
        score -= 1.0

    # Protein bonus
    if protein >= 20:
        score += 1.5
    elif protein >= 10:
        score += 0.8
    elif protein >= 5:
        score += 0.3

    # Fiber bonus
    if fiber >= 5:
        score += 1.0
    elif fiber >= 2:
        score += 0.5

    # Clamp score between 1 and 10
    score = round(max(1.0, min(10.0, score)), 1)

    # Label
    if score >= 8:
        label = "Excellent"
    elif score >= 6:
        label = "Good"
    elif score >= 4:
        label = "Moderate"
    else:
        label = "Poor"

    return {
        "score": score,
        "label": label,
        "breakdown": {
            "calories": calories,
            "protein":  protein,
            "fat":      fat,
            "sugar":    sugar,
            "fiber":    fiber
        }
    }