import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

FOOD_LABELS = [
    "apple", "banana", "orange", "mango", "grapes", "strawberry", "watermelon",
    "pineapple", "avocado", "blueberry", "pizza", "burger", "sandwich", "hotdog",
    "french fries", "pasta", "spaghetti", "rice", "biryani", "fried chicken",
    "grilled chicken", "sushi", "salad", "caesar salad", "omelette", "scrambled eggs",
    "pancakes", "waffles", "bread", "toast", "butter", "cheese", "yogurt", "milk",
    "chocolate cake", "ice cream", "donut", "cookie", "brownie", "cheesecake",
    "soup", "lentil soup", "steak", "salmon", "shrimp", "tacos", "burrito",
    "dal", "chapati", "samosa"
]

CONFIDENCE_THRESHOLD = 0.18

class CLIPFoodClassifier:
    def __init__(self):
        print("[INFO] Loading CLIP model...")
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.model.eval()
        print(f"[INFO] CLIP model loaded on {self.device}")

    def predict(self, image: Image.Image):
        text_prompts = [f"a photo of {label}" for label in FOOD_LABELS]

        inputs = self.processor(
            text=text_prompts,
            images=image,
            return_tensors="pt",
            padding=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits_per_image
            probs = logits.softmax(dim=1)

        top_prob, top_idx = probs[0].topk(3)

        results = []
        for prob, idx in zip(top_prob, top_idx):
            results.append({
                "label": FOOD_LABELS[idx.item()],
                "confidence": round(prob.item(), 4)
            })

        best = results[0]

        if best["confidence"] < CONFIDENCE_THRESHOLD:
            return {"success": False, "reason": "not_food", "predictions": results}

        return {"success": True, "food": best["label"], "confidence": best["confidence"], "top3": results}


# Singleton instance
classifier = CLIPFoodClassifier()


def predict_food(image: Image.Image):
    return classifier.predict(image)