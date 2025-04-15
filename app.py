import os
from flask import Flask, request, render_template
from dotenv import load_dotenv
import google.generativeai as genai
import requests

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Set API Keys
GENIE_API_KEY = os.getenv("GEMINI_API_KEY")
OPENFDA_API_KEY = os.getenv("OPENFDA_API_KEY")

# Initialize Gemini API
genai.api_key = GENIE_API_KEY
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to get symptom advice from Gemini
def get_symptom_advice(symptom_text):
    prompt = f"Analyze the symptoms: {symptom_text}. Provide a brief summary and recommend specialists."
    try:
        response = model.generate_content(prompt)
        gemini_analysis = response.text or ""

        # Clean response and remove ** for bold formatting
        gemini_analysis = gemini_analysis.replace("**", "")  # Remove stars used for bold text

        # Split response for summary and specialists
        sentences = gemini_analysis.split("\n")
        summary = " ".join(sentences[:2]) if len(sentences) >= 2 else "No summary available."
        specialists = [line.strip() for line in sentences if "specialist" in line or "doctor" in line]

        return summary, specialists if specialists else ["No specialists recommended."]
    except Exception as e:
        print(f"Error in Gemini API call: {str(e)}")
        return "No analysis available.", ["No specialists recommended."]

# Function to get drug recommendations from OpenFDA
def get_openfda_drugs(symptom):
    url = f"https://api.fda.gov/drug/drugsfda.json?search=symptoms:{symptom}&limit=5"
    headers = {"Authorization": f"Bearer {OPENFDA_API_KEY}"}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if "error" in data:
            return ["No results found in OpenFDA"]

        openfda_drugs = []
        for result in data.get('results', []):
            brand_name = result.get('openfda', {}).get('brand_name', [])
            if brand_name:
                openfda_drugs.append(brand_name[0])
            else:
                openfda_drugs.append("Unknown Drug")

        # Remove duplicates and handle empty results
        return list(set(openfda_drugs)) if openfda_drugs else ["No results found in OpenFDA"]
    except Exception as e:
        print(f"Error in OpenFDA API call: {str(e)}")
        return ["Error fetching OpenFDA data."]


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        symptom_text = request.form.get("symptoms")

        # Default values
        gemini_summary, specialists = "No analysis available.", ["No specialists recommended."]
        openfda_drugs = ["No results found in OpenFDA"]

        try:
            # Get symptom analysis
            gemini_summary, specialists = get_symptom_advice(symptom_text)
        except Exception as e:
            print(f"Error in Gemini advice: {str(e)}")

        try:
            # Get OpenFDA results
            openfda_drugs = get_openfda_drugs(symptom_text)
        except Exception as e:
            print(f"Error in OpenFDA: {str(e)}")

        return render_template("index.html", 
                               symptom_text=symptom_text,
                               gemini_summary=gemini_summary, 
                               specialists=specialists,
                               openfda_drugs=openfda_drugs)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
