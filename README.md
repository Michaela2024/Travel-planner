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

---

## Recommendation Engine

Cities are scored against user preferences across six factors with a maximum of 100 points:

| Factor | Max Points | Description |
|--------|-----------|-------------|
| Budget Match | 30 | Direct match scores full points; adjacent budget levels score partial points |
| Interest Match | 35 | Maps user interests to city categories; 7 points per matching interest, capped at 35 |
| Language Match | 10 | Full points for primary language match; partial for secondary languages |
| Season Match | 10 | Full points if user's preferred season matches city's best seasons |
| Transport & Accessibility | 10 | Proximity-based scoring from departure city; adjusted for transport preference |
| UNESCO Bonus | 5 | Bonus for cities with UNESCO heritage sites when user selects history/culture interests |

### Transport Scoring

Transport scoring uses a proximity model based on the departure city's country and the user's transport preference. Western European cities score higher than Central or Southern European cities for train travellers, reflecting general rail accessibility. This is a simplified model — real route data is not used.

**Known limitation:** The departure city must be a recognised major European city. Smaller towns or suburbs will receive neutral transport scoring. Users are advised to enter their nearest major city.

---

## AI Integration

The top-ranked city receives a personalised AI-generated explanation via the Gemini API. The prompt is score-aware — it adjusts the language and framing based on actual match scores, ensuring the explanation does not overstate the quality of a match.

Key prompt design decisions:
- Interest score below 15/35 → explanation acknowledges limited alignment honestly
- Season score of 0 → explanation does not describe the season as ideal
- Transport score below 5 → explanation does not suggest easy accessibility
- Departure city context → explanation contrasts the destination with what the user already has at home
- Tone → understated and specific; hyperbolic travel brochure language explicitly prohibited

Cities ranked #2 and #3 receive a score-based summary rather than a full AI explanation, keeping load times acceptable.

---

## Evaluation Framework

The application includes a systematic eval framework (`eval_recommendations.py`) that tests recommendation quality across five representative user personas using an LLM-as-judge approach.

### Personas tested
- Budget backpacker from London (train preference, summer, history/culture)
- Luxury traveller from Paris (flight preference, spring, wine/art)
- Nature lover from Amsterdam (flexible transport, autumn, nature/adventure/photography)
- Food lover from Madrid (flight preference, winter, food/wine/nightlife)
- Culture seeker from Edinburgh (flight preference, spring, history/music/photography)

### Automated scoring checks
- Budget match: top city should match expected budget level
- Score arithmetic: breakdown should sum to total
- Zero interest scores: flags cities scoring 0 on interests (indicates missing category mapping)

### LLM-as-judge criteria (all binary)
Each AI explanation is evaluated against seven binary criteria:
- `mentions_interests` — references at least one of the user's specific interests
- `transport_hallucination` — mentions specific routes, journey times, or connections
- `is_generic` — could apply to any city
- `personalised_to_user` — references at least two specific user preferences
- `contradicts_score` — describes interests as a strong match when interest score is below 15/35
- `home_context_ignored` — recommends something the user already has at home
- `exaggerated_language` — uses hyperbolic phrases or excessive exclamation marks

Pass/fail is computed deterministically from these binary fields — the LLM judge does not assign a quality score. Current pass rate: **15/15 (100%)** across 5 personas × 3 cities.

### Eval design notes
The judge criteria were derived from error analysis on real outputs — not defined upfront. Initial runs revealed systematic failures (score contradiction, transport hallucination, exaggerated language) which drove both prompt improvements and data quality fixes. This reflects the correct order of operations for LLM eval design: observe failures first, then build criteria around what you find.

---

## Known Limitations

- **Transport scoring** is proximity-based, not derived from real route data. Journey times, connections, and service frequency are not considered.
- **Car travel** is not scored as a transport option.
- **24 cities** currently in the database. European coverage is not exhaustive — Nordic, Eastern European, and Balkan destinations are underrepresented.
- **Departure city lookup** covers major European cities only. Smaller towns receive neutral transport scoring.
- **Interest scoring ceiling** is rarely reached in practice — a city needs to match 5+ user interests to score the maximum 35 points, which requires broad category coverage.
- **No user accounts** — preferences are stored in the session only and not persisted between visits.

---

## Setup and Installation

### Prerequisites
- Python 3.11
- A Google Gemini API key (obtain from [Google AI Studio](https://aistudio.google.com))

### Installation

```bash
git clone <repository-url>
cd european_travel_planner
pip install -r requirements.txt
```

### Environment variables
 
Create a `.env` file in the project root:
 
```
GEMINI_API_KEY=your-gemini-api-key-here
DJANGO_SECRET_KEY=your-django-secret-key-here
DEBUG=True
```
 
### Database setup
 
```bash
python manage.py migrate
```
 
### Run the development server
 
```bash
python manage.py runserver
```
 
The application will be available at `http://127.0.0.1:8000/`.
 
### Run the evaluation suite
 
```bash
python eval_recommendations.py
```
 
