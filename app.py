import csv
import json
import os
from pathlib import Path

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
from google.genai import types


# --------------------------------------------------
# SETUP
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)
CORS(app)

# Make sure the API key exists
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY was not found. "
        "Make sure your .env file contains GEMINI_API_KEY=your_key"
    )

# Gemini client
client = genai.Client(api_key=api_key)


# --------------------------------------------------
# COURSE DATA
# --------------------------------------------------

def read_courses():
    """
    Read course information from courses.csv.
    """

    csv_path = BASE_DIR / "courses.csv"

    if not csv_path.exists():
        raise FileNotFoundError(
            f"courses.csv was not found at: {csv_path}"
        )

    courses = []

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            # Remove extra spaces from column names/values
            cleaned_row = {
                str(key).strip(): str(value).strip()
                for key, value in row.items()
            }

            courses.append(cleaned_row)

    return courses


# --------------------------------------------------
# ROUTES
# --------------------------------------------------

@app.route("/")
def home():
    """
    Serve the main website.
    """
    return render_template("index.html")


@app.route("/api/health")
def health():
    """
    Simple backend test.
    """
    return jsonify({
        "status": "success",
        "message": "WhatDoITake.course backend is running!"
    })


@app.route("/api/courses")
def get_courses():
    """
    Return all courses from the CSV.
    """
    try:
        courses = read_courses()

        return jsonify({
            "status": "success",
            "count": len(courses),
            "courses": courses
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# --------------------------------------------------
# GEMINI SCHEDULE GENERATOR
# --------------------------------------------------

@app.route("/api/generate_schedule", methods=["POST"])
def generate_schedule():

    try:
        data = request.get_json(silent=True) or {}

        # ------------------------------------------
        # Student information
        # ------------------------------------------

        major = data.get(
            "major",
            "Computer Science"
        )

        time_preference = data.get(
            "time_preference",
            "Any"
        )

        difficulty_preference = data.get(
            "difficulty",
            "Balanced"
        )

        taken_courses = data.get(
            "taken_courses",
            []
        )

        interests = data.get(
            "interests",
            ""
        )

        # ------------------------------------------
        # Load courses
        # ------------------------------------------

        all_courses = read_courses()

        if not all_courses:
            return jsonify({
                "status": "error",
                "message": "courses.csv is empty."
            }), 400

        # ------------------------------------------
        # Remove courses already completed
        # ------------------------------------------

        available_courses = []

        for course in all_courses:

            course_name = course.get(
                "Course Name",
                ""
            )

            course_code = course.get(
                "Course Code",
                ""
            )

            already_taken = (
                course_name in taken_courses
                or course_code in taken_courses
            )

            if not already_taken:
                available_courses.append(course)

        if len(available_courses) == 0:
            return jsonify({
                "status": "error",
                "message": "There are no available courses after removing completed courses."
            }), 400

        # ------------------------------------------
        # Build Gemini prompt
        # ------------------------------------------

        prompt = f"""
You are an expert university academic scheduling assistant.

Your job is to select the best courses from the provided university course catalog.

STUDENT INFORMATION

Major:
{major}

Preferred class time:
{time_preference}

Preferred workload/difficulty:
{difficulty_preference}

Student interests:
{interests}

Completed courses:
{json.dumps(taken_courses)}

IMPORTANT RULES

1. Only recommend courses from the AVAILABLE COURSE POOL.
2. Never recommend a course the student has already completed.
3. Do not invent courses.
4. Do not modify course information.
5. Recommend up to 4 courses.
6. Try to choose courses relevant to the student's major.
7. Respect the student's preferred class time.
8. Respect the student's workload preference.
9. Do not recommend courses whose meeting times overlap.
10. If the data contains prerequisite information, use it.
11. Return the courses exactly as they appear in the input data.

AVAILABLE COURSE POOL:

{json.dumps(available_courses, indent=2)}

Return the recommended courses.
"""

        # ------------------------------------------
        # Ask Gemini for structured JSON
        # ------------------------------------------

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )

        raw_text = response.text

        if not raw_text:
            raise ValueError(
                "Gemini returned an empty response."
            )

        # ------------------------------------------
        # Convert Gemini response to Python
        # ------------------------------------------

        schedule = json.loads(raw_text)

        if not isinstance(schedule, list):
            raise ValueError(
                "Gemini did not return a JSON array."
            )

        # ------------------------------------------
        # Safety check:
        # Only return courses that actually exist
        # in our CSV.
        # ------------------------------------------

        valid_courses = []

        for recommended_course in schedule:

            if not isinstance(recommended_course, dict):
                continue

            matches = [
                course
                for course in available_courses
                if (
                    course.get("Course Code")
                    == recommended_course.get("Course Code")
                )
                and (
                    course.get("Course Name")
                    == recommended_course.get("Course Name")
                )
            ]

            if matches:
                valid_courses.append(matches[0])

        # Remove duplicates
        unique_courses = []
        seen_codes = set()

        for course in valid_courses:

            code = course.get("Course Code")

            if code not in seen_codes:
                seen_codes.add(code)
                unique_courses.append(course)

        return jsonify({
            "status": "success",
            "schedule": unique_courses
        })

    except json.JSONDecodeError as e:

        print("JSON ERROR:", e)

        return jsonify({
            "status": "error",
            "message": "Gemini returned invalid JSON."
        }), 500

    except Exception as e:

        print("BACKEND ERROR:", repr(e))

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )