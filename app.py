import csv
import os
from flask import Flask, request, jsonify, render_template
from google import genai
from dotenv import load_dotenv

# Load environment variables (pulls your GEMINI_API_KEY from the .env file)
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize the Gemini Client
client = genai.Client()

def read_courses():
    """Reads the mock course data from our CSV file into a Python list."""
    courses = []
    # Make sure 'courses.csv' is in the same folder as this file
    with open('courses.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            courses.append(row)
    return courses

@app.route('/')
def home():
    return render_template('index.html')


# The core route that handles the scheduling magic
@app.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    # 1. Get the student's preferences sent from the frontend UI
    user_data = request.json
    major = user_data.get('major', 'Undecided')
    time_pref = user_data.get('time_preference', 'Any')
    difficulty = user_data.get('difficulty', 'Any')

    # 2. Load your mock course data
    available_courses = read_courses()

    # 3. Build the prompt for Gemini using the user's data and the CSV data
    prompt = f"""
    You are an expert academic advisor for a university.
    The student is a {major} major.
    Time preference: {time_pref}
    Workload/Difficulty preference: {difficulty}
    
    Here is the mock list of available courses:
    {available_courses}
    
    Based on these preferences, pick exactly 4 courses to create a balanced semester schedule. 
    Return your answer as a clean JSON array of the 4 course objects. Do not include Markdown blocks (```json). Just return the raw JSON text.
    """

    # 4. Call the Gemini API
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        # 5. Send the AI's generated schedule back to the frontend
        return jsonify({"status": "success", "schedule": response.text})
    except Exception as e:
        # If something breaks, tell the frontend what happened
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Starts the local development server
    app.run(debug=True, port=5001)