Whatdoitake.course 
An intelligent, non-chatbot academic scheduling system built for ShellHacks. Whatdoitake.course simplifies the tedious university registration process by generating optimized, visual weekly schedules based on student workload preferences, degree progress, and personal availability.

The Problem
Every semester, students spend hours toggling between university course portals, professor review sites, and personal calendars trying to construct a balanced schedule. Manual registration planning is overwhelming, fragmented, and fails to account for real-life commitments outside of class.

The Solution
1. Whatdoitake.course transforms registration into a seamless, visual experience:
Preference-Driven Scheduling: Students set their target difficulty, preferred time slots, and academic goals using an intuitive UI.
2. AI Schedule Optimization: Rather than a simple chatbot, our background engine powered by Google Gemini evaluates course data to generate tailored visual class schedules.
3. Peer Collaboration: Integrates directly with a peer network, allowing students to instantly connect with study groups for their generated classes.

Hackathon Tracks & Features
1. Microsoft (What's Missing?): Replaces traditional, chat-window AI with a utility-first workflow tool. The AI operates behind the scenes to directly solve a complex task—building a functional calendar schedule—rather than simply answering questions.
2. Google Cloud (Best Use of Gemini API): Leverages the Google Gemini API to analyze complex course metadata, professor ratings, and user constraints to reason through trade-offs and select the optimal set of classes.
3. INIT National (Building Together): Connects students registered for the same courses into collaborative learning pods, helping builders form study groups, share resources, and maintain engagement throughout the term.
4. GoDaddy Registry: Custom domain setup for an accessible web app experience.

Tech Stack
1. Frontend: HTML5, CSS3, Tailwind CSS, JavaScript
2. Backend: Python, Flask
3. AI Engine: Google Gemini API (google-generativeai)
4. Data Layer: Local mock datasets (CSV/JSON) simulating live course registries and rating platforms

Getting Started

Prerequisites:
Python 3.9+
A Google Gemini API Key

Installation:

Clone the repository:
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY

Install dependencies:
pip install flask google-generativeai python-dotenv

Configure environment variables:
Create a .env file in the root directory and add your Gemini API key:
GEMINI_API_KEY=your_gemini_api_key_here

Run the application:
python app.py

Open your browser and navigate to http://127.0.0.1:5000/.

Future Roadmap
Live Portal Integration: Bypassing manual entry by connecting directly to university SIS endpoints (e.g., Canvas, Banner).
Live RMP Scraper: Automated API fetching from RateMyProfessor for real-time score updates.
Calendar Sync: One-click exporter to Google Calendar, Apple Calendar, and Outlook.
