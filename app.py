import csv
import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from dotenv import load_dotenv

# Load environment variables (pulls your GEMINI_API_KEY from the .env file)

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enables cross-origin requests from frontend

# Initialize the Gemini Client
client = genai.Client()

def read_courses():
    """Reads course dataset from local CSV."""
    courses = []
    if not os.path.exists('courses.csv'):
        return courses
    with open('courses.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            courses.append(row)
    return courses

@app.route('/')
def home():
    return jsonify({"status": "active", "message": "WhatDoITake.course backend is running!"})

@app.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    data = request.json or {}
    
    major = data.get('major', 'Computer Science')
    time_pref = data.get('time_preference', 'Any')
    difficulty_pref = data.get('difficulty', 'Balanced')
    taken_courses = data.get('taken_courses', [])

    all_courses = read_courses()

    prompt = f"""
    You are an expert university academic advisor.
    Student Major: {major}
    Time Preference: {time_pref}
    Workload/Difficulty Preference: {difficulty_pref}
    
    CRITICAL CONSTRAINT:
    The student has ALREADY TAKEN these courses: {taken_courses}.
    DO NOT select or include any of these completed courses in the new schedule.
    
    Available Course Pool:
    {json.dumps(all_courses)}
    
    TASK:
    Select exactly 4 unique courses from the available pool that best fit the student's preferences and major.
    Make sure class times DO NOT overlap.
    
    RESPONSE FORMAT REQUIREMENT:
    Return ONLY a valid JSON array containing exactly 4 course objects directly from the input pool.
    Do NOT include Markdown formatting, backticks, or extra text.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )

        raw_text = response.text.strip()
        
        # Strip potential markdown code blocks if present
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        schedule = json.loads(raw_text.strip())

        return jsonify({
            "status": "success",
            "schedule": schedule
        })

    except Exception as e:
        print("Backend Error:", str(e))
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)