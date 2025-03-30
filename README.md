# 🧠 The Recollector

An AI-powered memory authentication system that replaces passwords with something more human: memories.

**The Recollector** helps individuals—especially those living with Alzheimer's and other cognitive challenges—authenticate by recognizing personal images instead of typing passwords. It’s not just secure; it’s a memory-reinforcing experience.

---

## 🔍 Features

- 🔐 **Passwordless authentication** via visual memory challenges  
- 🧠 **Cognitive support** for users with memory impairments  
- 🖼️ **Custom memory keys** based on user-uploaded personal photos  
- 🧪 AI-driven decoy generation to ensure challenge security  
- 💡 Dark-mode optimized, accessible UI  
- 🧾 Testimonial grid and responsive frontend with Bootstrap + CSS glow aesthetics

---

## 📸 How It Works

1. **Register** and upload 5 meaningful images.
2. The app creates a visual memory profile ("memory key").
3. When logging in, users are shown challenges to identify their own images among decoys.
4. Each correct answer reinforces familiarity and strengthens memory cues.

---

## 💻 Technologies Used

- **Flask** — lightweight Python backend
- **Jinja2** — templating for dynamic HTML
- **Bootstrap 5** — responsive layout
- **Custom CSS** — neon-inspired dark theme with accessibility in mind
- **(Optional)**: OpenCV / Gemini / ML model (describe your image-processing stack if applicable)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- `pip`
- (Optional) virtualenv

### Installation

```bash
git clone https://github.com/yourusername/recollector.git
cd recollector
pip install -r requirements.txt
