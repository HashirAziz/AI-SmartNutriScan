import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/nutrition_db.json")

with open(DB_PATH, "r") as f:
    NUTRITION_DB = json.load(f)


def get_nutrition(food_name: str) -> dict:
    """
    Returns nutrition data for the given food name.
    Falls back to None if not found.
    """
    key = food_name.lower().strip()

    if key in NUTRITION_DB:
        data = NUTRITION_DB[key]
        return {
            "found": True,
            "food": key,
            "per_100g": {
                "calories":  data["calories"],
                "protein":   data["protein"],
                "carbs":     data["carbs"],
                "fat":       data["fat"],
                "fiber":     data["fiber"],
                "sugar":     data["sugar"]
            },
            "vitamins":           data["vitamins"],
            "minerals":           data["minerals"],
            "dietary_tags":       data["dietary_tags"],
            "disease_prevention": data["disease_prevention"],
            "advice":             data["advice"]
        }

    return {"found": False, "food": food_name}