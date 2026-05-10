# European City Trip Planner

A personalised travel recommendation web application that matches users with European city destinations based on their preferences, using a custom scoring engine and AI-generated recommendations.

---

## What It Does

Users complete a short questionnaire covering budget, travel season, departure city, transport preference, and interests. The application scores all cities in the database against these preferences and returns the top three matches, with an AI-generated explanation for the best match.

Results can be re-sorted by different priorities — best overall match, best value, easiest to reach, best for interests, or best season — giving users a nuanced view of their options rather than a single ranked list.

---

## Tech Stack

- **Backend:** Python 3.11, Django 5.2
- **AI Integration:** Google Gemini API (`google-genai` SDK), model `gemini-flash-latest`
- **Database:** SQLite (development)
- **Frontend:** Django templates, HTML/CSS, vanilla JavaScript
- **Testing:** Custom eval framework with LLM-as-judge

---

## Application Structure