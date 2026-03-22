import cv2
import numpy as np
from PIL import Image

# Load Haar Cascade for face detection
FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Non-food keywords to reject from CLIP predictions
NON_FOOD_KEYWORDS = [
    "person", "human", "face", "selfie", "animal", "cat", "dog", "bird",
    "car", "tree", "building", "phone", "laptop", "furniture", "flower",
    "grass", "sky", "road", "book", "clothes", "shoe"
]


def pil_to_cv2(image: Image.Image) -> np.ndarray:
    """Convert PIL image to OpenCV BGR format."""
    img_rgb = np.array(image.convert("RGB"))
    return cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)


def detect_face(image: Image.Image) -> bool:
    """
    Returns True if a human face is detected in the image.
    """
    img_cv2 = pil_to_cv2(image)
    gray = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2GRAY)

    faces = FACE_CASCADE.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )

    return len(faces) > 0


def is_non_food(label: str) -> bool:
    """
    Returns True if predicted label matches a known non-food keyword.
    """
    label_lower = label.lower()
    return any(keyword in label_lower for keyword in NON_FOOD_KEYWORDS)


def validate_image(image: Image.Image, predicted_label: str) -> dict:
    """
    Full validation pipeline:
    - Rejects if face detected
    - Rejects if label is non-food
    Returns dict with is_valid flag and reason.
    """
    # Check 1: Face detection
    if detect_face(image):
        return {
            "is_valid": False,
            "reason": "Selfie or human face detected. Please upload a food image."
        }

    # Check 2: Non-food label from CLIP
    if is_non_food(predicted_label):
        return {
            "is_valid": False,
            "reason": f"'{predicted_label}' is not a recognized food item. Please upload a valid food image."
        }

    return {
        "is_valid": True,
        "reason": "Image is valid food."
    }