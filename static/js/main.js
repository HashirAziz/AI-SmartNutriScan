// ── DOM References ────────────────────────────────────────

const fileInput      = document.getElementById("fileInput");
const uploadZone     = document.getElementById("uploadZone");
const previewZone    = document.getElementById("previewZone");
const previewImg     = document.getElementById("previewImg");
const analyzeBtn     = document.getElementById("analyzeBtn");
const resetBtn       = document.getElementById("resetBtn");
const loader         = document.getElementById("loader");
const errorBox       = document.getElementById("errorBox");
const errorMsg       = document.getElementById("errorMsg");
const results        = document.getElementById("results");
const cameraBtn      = document.getElementById("cameraBtn");
const cameraView     = document.getElementById("cameraView");
const videoStream    = document.getElementById("videoStream");
const captureBtn     = document.getElementById("captureBtn");
const closeCameraBtn = document.getElementById("closeCameraBtn");
const captureCanvas  = document.getElementById("captureCanvas");
const scanAgainBtn   = document.getElementById("scanAgainBtn");

let selectedFile = null;
let cameraStream  = null;


// ── Drag & Drop ───────────────────────────────────────────

uploadZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadZone.classList.add("dragover");
});

uploadZone.addEventListener("dragleave", () => {
  uploadZone.classList.remove("dragover");
});

uploadZone.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadZone.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file) handleFileSelect(file);
});


// ── File Input ────────────────────────────────────────────

fileInput.addEventListener("change", () => {
  if (fileInput.files[0]) handleFileSelect(fileInput.files[0]);
});


// ── Handle File Select ────────────────────────────────────

function handleFileSelect(file) {
  const allowed = ["image/jpeg", "image/png", "image/webp"];

  if (!allowed.includes(file.type)) {
    showError("Invalid file type. Please upload JPG, PNG, or WEBP.");
    return;
  }

  if (file.size > 10 * 1024 * 1024) {
    showError("File too large. Maximum size is 10MB.");
    return;
  }

  selectedFile = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImg.src = e.target.result;
    show(previewZone);
    hide(uploadZone);
    hide(errorBox);
    hide(results);
  };
  reader.readAsDataURL(file);
}


// ── Camera ────────────────────────────────────────────────

cameraBtn.addEventListener("click", async () => {
  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment" }
    });
    videoStream.srcObject = cameraStream;
    hide(uploadZone);
    hide(errorBox);
    show(cameraView);
  } catch (err) {
    showError("Camera access denied or not available.");
  }
});

captureBtn.addEventListener("click", () => {
  captureCanvas.width  = videoStream.videoWidth;
  captureCanvas.height = videoStream.videoHeight;
  captureCanvas.getContext("2d").drawImage(videoStream, 0, 0);

  captureCanvas.toBlob((blob) => {
    selectedFile = new File([blob], "capture.jpg", { type: "image/jpeg" });
    previewImg.src = captureCanvas.toDataURL("image/jpeg");
    stopCamera();
    hide(cameraView);
    show(previewZone);
  }, "image/jpeg", 0.92);
});

closeCameraBtn.addEventListener("click", () => {
  stopCamera();
  hide(cameraView);
  show(uploadZone);
});

function stopCamera() {
  if (cameraStream) {
    cameraStream.getTracks().forEach(t => t.stop());
    cameraStream = null;
  }
}


// ── Analyze ───────────────────────────────────────────────

analyzeBtn.addEventListener("click", () => analyzeFood());

async function analyzeFood() {
  if (!selectedFile) {
    showError("Please select an image first.");
    return;
  }

  const formData = new FormData();
  formData.append("image", selectedFile);

  hide(previewZone);
  hide(errorBox);
  hide(results);
  show(loader);

  try {
    const response = await fetch("/predict", {
      method: "POST",
      body: formData
    });

    const data = await response.json();
    hide(loader);

    if (!data.success) {
      showError(data.error || "Something went wrong. Please try again.");
      show(previewZone);
      return;
    }

    renderResults(data);

  } catch (err) {
    hide(loader);
    showError("Network error. Make sure the server is running.");
    show(previewZone);
  }
}


// ── Render Results ────────────────────────────────────────

function renderResults(data) {
  // Food name & confidence
  document.getElementById("resultFoodName").textContent = data.food;
  document.getElementById("resultImg").src              = data.image_url;
  document.getElementById("confidenceText").textContent = `${data.confidence}%`;

  // Confidence bar
  setTimeout(() => {
    document.getElementById("confidenceFill").style.width = `${data.confidence}%`;
  }, 100);

  // Health score ring
  const score     = data.health_score.score;
  const ringEl    = document.getElementById("scoreRing");
  const circumference = 314;
  const offset    = circumference - (score / 10) * circumference;

  document.getElementById("scoreValue").textContent = score;
  document.getElementById("scoreLabel").textContent = data.health_score.label;

  // Ring color based on score
  if (score >= 8)      ringEl.style.stroke = "#22c55e";
  else if (score >= 6) ringEl.style.stroke = "#3b82f6";
  else if (score >= 4) ringEl.style.stroke = "#f97316";
  else                 ringEl.style.stroke = "#ef4444";

  setTimeout(() => {
    ringEl.style.strokeDashoffset = offset;
  }, 200);

  // Score breakdown
  const bd = data.health_score.breakdown;
  document.getElementById("scoreBreakdown").innerHTML = [
    { label: "Calories", val: `${bd.calories} kcal` },
    { label: "Protein",  val: `${bd.protein}g` },
    { label: "Fat",      val: `${bd.fat}g` },
    { label: "Sugar",    val: `${bd.sugar}g` },
    { label: "Fiber",    val: `${bd.fiber}g` }
  ].map(i => `
    <div class="breakdown-item">
      <strong>${i.val}</strong> ${i.label}
    </div>
  `).join("");

  // Nutrition grid
  const n = data.nutrition.per_100g;
  document.getElementById("nutritionGrid").innerHTML = [
    { label: "Calories", value: n.calories, unit: "kcal" },
    { label: "Protein",  value: n.protein,  unit: "g"    },
    { label: "Carbs",    value: n.carbs,    unit: "g"    },
    { label: "Fat",      value: n.fat,      unit: "g"    },
    { label: "Fiber",    value: n.fiber,    unit: "g"    },
    { label: "Sugar",    value: n.sugar,    unit: "g"    }
  ].map(item => `
    <div class="nutr-item">
      <div class="nutr-value">${item.value}<span class="nutr-unit">${item.unit}</span></div>
      <div class="nutr-label">${item.label}</div>
    </div>
  `).join("");

  // Dietary tags
  document.getElementById("dietaryTags").innerHTML = data.dietary_tags
    .map(tag => `<span class="tag">${tag}</span>`)
    .join("");

  // Vitamins
  document.getElementById("vitaminsList").innerHTML = data.nutrition.vitamins
    .map(v => `<li>${v}</li>`)
    .join("");

  // Minerals
  document.getElementById("mineralsList").innerHTML = data.nutrition.minerals
    .map(m => `<li>${m}</li>`)
    .join("");

  // Disease prevention
  document.getElementById("diseaseList").innerHTML = data.disease_prevention
    .map(d => `<li>${d}</li>`)
    .join("");

  // Advice
  document.getElementById("adviceText").textContent = data.advice;

  // Top 3 predictions
  document.getElementById("top3Wrap").innerHTML = data.top3
    .map((item, i) => `
      <div class="top3-item">
        <span class="top3-rank">#${i + 1}</span>
        <span class="top3-label">${item.label}</span>
        <div class="top3-bar-wrap">
          <div class="top3-bar" style="width: ${item.confidence}%"></div>
        </div>
        <span class="top3-pct">${item.confidence}%</span>
      </div>
    `).join("");

  show(results);

  // Smooth scroll to results
  setTimeout(() => {
    results.scrollIntoView({ behavior: "smooth", block: "start" });
  }, 100);
}


// ── Reset ─────────────────────────────────────────────────

resetBtn.addEventListener("click", resetAll);
scanAgainBtn.addEventListener("click", resetAll);

function resetAll() {
  selectedFile      = null;
  fileInput.value   = "";
  previewImg.src    = "";

  // Reset confidence bar
  document.getElementById("confidenceFill").style.width = "0%";

  // Reset score ring
  document.getElementById("scoreRing").style.strokeDashoffset = "314";

  hide(previewZone);
  hide(results);
  hide(errorBox);
  hide(loader);
  show(uploadZone);

  window.scrollTo({ top: 0, behavior: "smooth" });
}


// ── Helpers ───────────────────────────────────────────────

function show(el) { el.classList.remove("hidden"); }
function hide(el) { el.classList.add("hidden");    }

function showError(msg) {
  errorMsg.textContent = msg;
  show(errorBox);
}