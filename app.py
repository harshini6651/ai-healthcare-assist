from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
import os

# ------------------------------
# App Setup
# ------------------------------
load_dotenv()
app = Flask(__name__)

# ------------------------------
# Configure Gemini AI
# ------------------------------
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("⚠️ GOOGLE_API_KEY not found. Set it in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.0-pro")  # ✅ stable & supported

# ------------------------------
# Routes
# ------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        language = data.get("language", "English")

        if not user_message:
            return jsonify({"response": "⚠️ Please type a message."}), 400

        prompt = f"""
You are a public health AI assistant.
Respond in {language}.
Keep answers short (2–3 sentences).
Base answers on WHO, MoHFW, CDC.
If emergency, advise consulting a doctor.

User: {user_message}
"""

        response = model.generate_content(prompt)
        return jsonify({"response": response.text or "⚠️ No response from AI."})

    except Exception as e:
        return jsonify({"response": f"⚠️ Server error: {str(e)}"}), 500


@app.route("/updates", methods=["POST"])
def updates():
    data = request.get_json()
    update_type = data.get("type", "")
    region = data.get("region", "India")

    if update_type == "alerts":
        return jsonify({"response": fetch_health_alerts(region)})
    elif update_type == "schemes":
        return jsonify({"response": fetch_health_schemes(region)})
    elif update_type == "faq":
        return jsonify({"response": fetch_faqs(region)})

    return jsonify({"response": "No data available."})


# ------------------------------
# Helper Functions
# ------------------------------
def fetch_health_alerts(region):
    if region.lower() == "telangana":
        return "<br>".join([
            "1. Dengue alert in Hyderabad.",
            "2. COVID-19 vaccination drive ongoing.",
            "3. Seasonal flu awareness campaign."
        ])
    return "⚠️ No regional alerts found."


def fetch_health_schemes(region):
    if region.lower() == "telangana":
        return "<br>".join([
            "1. Aarogya Sri Health Insurance Scheme.",
            "2. Telangana Nutrition Mission.",
            "3. Free health checkups for seniors."
        ])
    return "✅ No schemes found."


def fetch_faqs(region):
    return "<br>".join([
        "1. Fever → Stay hydrated, consult doctor if persistent.",
        "2. Dengue prevention → Avoid stagnant water.",
        "3. Flu spreads via droplets → Maintain hygiene."
    ])


# ------------------------------
# Run App
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)