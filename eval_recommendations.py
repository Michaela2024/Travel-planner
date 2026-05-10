import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from recommendations.recommendations_engine import calculate_city_score
from destinations.models import City
from google import genai
from django.conf import settings
import json

# ── Test personas ──────────────────────────────────────────────────────────────

test_personas = [
    {
        'name': 'Budget backpacker from London',
        'budget': 'budget',
        'season': 'summer',
        'departure_city': 'london',
        'transport_preference': 'prefer_train',
        'interests': ['History & Architecture', 'Culture & Local Life'],
        'languages': ['English'],
        'expected_budget': 'budget',
        'expected_nearby': True,
    },
    {
        'name': 'Luxury traveller from Paris',
        'budget': 'luxury',
        'season': 'spring',
        'departure_city': 'paris',
        'transport_preference': 'prefer_flight',
        'interests': ['Wine & Gastronomy', 'Art Museums'],
        'languages': ['English', 'French'],
        'expected_budget': 'luxury',
        'expected_nearby': False,
    },
    {
        'name': 'Nature lover from Amsterdam',
        'budget': 'moderate',
        'season': 'autumn',
        'departure_city': 'amsterdam',
        'transport_preference': 'no_preference',
        'interests': ['Nature & Outdoors', 'Adventure & Sports', 'Photography'],
        'languages': ['English', 'Dutch'],
        'expected_budget': 'moderate',
        'expected_nearby': True,
    },
    {
        'name': 'Food lover from Madrid',
        'budget': 'moderate',
        'season': 'winter',
        'departure_city': 'madrid',
        'transport_preference': 'prefer_flight',
        'interests': ['Food & Culinary', 'Wine & Gastronomy', 'Nightlife & Entertainment'],
        'languages': ['English', 'Spanish'],
        'expected_budget': 'moderate',
        'expected_nearby': False,
    },
    {
        'name': 'Culture seeker from Edinburgh',
        'budget': 'budget',
        'season': 'spring',
        'departure_city': 'edinburgh',
        'transport_preference': 'prefer_flight',
        'interests': ['History & Architecture', 'Music & Festivals', 'Photography'],
        'languages': ['English'],
        'expected_budget': 'budget',
        'expected_nearby': False,
    },
]

# ── Scoring eval ───────────────────────────────────────────────────────────────

def run_scoring_eval(persona):
    """Run scoring for a persona and return top 3 cities with scores."""
    user_prefs = {
        'budget': persona['budget'],
        'interests': persona['interests'],
        'languages': persona['languages'],
        'season': persona['season'],
        'departure_city': persona['departure_city'],
        'departure_country': '',
        'transport': persona['transport_preference'],
    }

    all_cities = City.objects.all().exclude(name__iexact=persona['departure_city'])

    scored = []
    for city in all_cities:
        score_data = calculate_city_score(city, user_prefs)
        scored.append(score_data)

    scored.sort(key=lambda x: x['total_score'], reverse=True)
    print(f"  Scoring done for {persona['name']}")
    return scored[:3], user_prefs


def check_scoring(persona, top_cities):
    """Run automated checks on scoring results."""
    flags = []

    # Check 1: Budget match
    top_city = top_cities[0]
    if top_city['city'].cost_level != persona['expected_budget']:
        flags.append(
            f"⚠️  Budget mismatch: top city is '{top_city['city'].cost_level}' "
            f"but persona wants '{persona['expected_budget']}'"
        )

    # Check 2: Scores add up correctly
    for rec in top_cities:
        bd = rec['breakdown']
        calculated = sum(bd.values())
        if calculated != rec['total_score']:
            flags.append(
                f"⚠️  Score mismatch for {rec['city'].name}: "
                f"breakdown sums to {calculated} but total is {rec['total_score']}"
            )

    # Check 3: Transport note for manual review
    if persona['transport_preference'] in ['prefer_train', 'train_only']:
        transport_scores = [
            (r['city'].name, r['city'].country, r['breakdown']['transport'])
            for r in top_cities
        ]
        flags.append(
            f"ℹ️  Transport scores (train preference): {transport_scores} — manual check recommended"
        )

    # Check 4: Zero interest scores
    for rec in top_cities:
        if rec['breakdown']['interests'] == 0:
            flags.append(
                f"⚠️  {rec['city'].name} scored 0 on interests — "
                f"category mapping may be missing"
            )

    return flags


# ── Gemini explanation + judge ─────────────────────────────────────────────────

def generate_explanation(city_data, user_prefs):
    """Generate explanation using the same prompt as the main app."""
    from recommendations.gemini_integration import generate_city_explanation
    return generate_city_explanation(
        city=city_data['city'],
        user_preferences=user_prefs,
        score_breakdown=city_data['breakdown'],
        total_score=city_data['total_score']
    )


def judge_explanation(explanation, persona, city_name, score_breakdown):
    """Use Gemini as a judge to evaluate the explanation quality."""

    judge_prompt = f"""You are an expert evaluator of AI-generated travel recommendations.
Evaluate the following recommendation explanation and return ONLY a JSON object with no markdown formatting.

USER PROFILE:
- Name/Type: {persona['name']}
- Budget: {persona['budget']}
- Interests: {', '.join(persona['interests'])}
- Departure city: {persona['departure_city']}
- Transport preference: {persona['transport_preference']}
- Season: {persona['season']}

CITY BEING RECOMMENDED: {city_name}

SCORE BREAKDOWN:
- Budget: {score_breakdown.get('budget', 0)}/30
- Interests: {score_breakdown.get('interests', 0)}/35
- Transport: {score_breakdown.get('transport', 0)}/10
- Season: {score_breakdown.get('season', 0)}/10
- Language: {score_breakdown.get('language', 0)}/10
- UNESCO: {score_breakdown.get('unesco', 0)}/5

EXPLANATION TO EVALUATE:
{explanation}

Return this exact JSON structure with no extra text:
{{
  "mentions_interests": <true if the explanation references at least one of the user's specific interests>,
  "transport_hallucination": <true if it mentions specific routes, journey times, or connections>,
  "is_generic": <true if the explanation could apply to any city>,
  "personalised_to_user": <true if it references at least two specific user preferences>,
  "budget_appropriate": <true if the tone and recommendations match the user's budget level>,
  "season_referenced": <true if the explanation mentions the travel season>,
  "contradicts_score": <true if the explanation describes interests as a strong match when interest score is below 15/35>,
  "home_context_ignored": <true if the explanation recommends something the user can easily access at home, for example recommending wine to someone from a wine region, or Dutch cuisine to someone from Amsterdam>,
  "exaggerated_language": <true if the explanation uses hyperbolic phrases like "absolute dream", "utterly enchanted", "magical", "paradise", or has more than one exclamation mark>,
  "flags": [<list of specific issues as strings, empty list if none>],
  "summary": "<one sentence assessment>"
}}"""

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=judge_prompt
        )
        raw = response.text.strip()
        if raw.startswith('```'):
            raw = raw.split('```')[1]
            if raw.startswith('json'):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as e:
        return {'error': str(e)}


# ── Pass/fail logic ────────────────────────────────────────────────────────────

def compute_pass(judgement):
    """Deterministically compute pass/fail from binary judge fields."""
    return (
        judgement.get('mentions_interests', False) and
        judgement.get('personalised_to_user', False) and
        not judgement.get('transport_hallucination', False) and
        not judgement.get('is_generic', False) and
        not judgement.get('contradicts_score', False) and
        not judgement.get('home_context_ignored', False) and
        not judgement.get('exaggerated_language', False)
    )


# ── Report ─────────────────────────────────────────────────────────────────────

def print_report(persona, top_cities, scoring_flags, explanations, judgements):
    print("\n" + "=" * 70)
    print(f"PERSONA: {persona['name']}")
    print("=" * 70)

    print("\n📊 SCORING RESULTS:")
    for i, rec in enumerate(top_cities):
        bd = rec['breakdown']
        print(f"  #{i+1} {rec['city'].name}, {rec['city'].country} — {rec['total_score']}pts")
        print(
            f"       budget:{bd.get('budget',0)} interests:{bd.get('interests',0)} "
            f"language:{bd.get('language',0)} season:{bd.get('season',0)} "
            f"transport:{bd.get('transport',0)} unesco:{bd.get('unesco',0)}"
        )

    if scoring_flags:
        print("\n🚩 SCORING FLAGS:")
        for flag in scoring_flags:
            print(f"  {flag}")
    else:
        print("\n✅ No automated scoring issues detected")

    print("\n🤖 AI EXPLANATIONS + JUDGE VERDICTS:")
    for i, (exp, judgement) in enumerate(zip(explanations, judgements)):
        city_name = top_cities[i]['city'].name
        print(f"\n  [{city_name}]")
        print(f"  Explanation: {exp[:200]}...")

        if 'error' in judgement:
            print(f"  Judge error: {judgement['error']}")
        else:
            passed = compute_pass(judgement)
            emoji = '✅' if passed else '❌'
            print(f"  {emoji} {'PASS' if passed else 'FAIL'} — {judgement.get('summary', '')}")
            print(
                f"     Mentions interests: {judgement.get('mentions_interests')} | "
                f"Transport hallucination: {judgement.get('transport_hallucination')} | "
                f"Generic: {judgement.get('is_generic')} | "
                f"Personalised: {judgement.get('personalised_to_user')} | "
                f"Contradicts score: {judgement.get('contradicts_score')} | "
                f"Home context ignored: {judgement.get('home_context_ignored')} | "
                f"Exaggerated language: {judgement.get('exaggerated_language')}"
            )
            if judgement.get('flags'):
                for flag in judgement['flags']:
                    print(f"     ⚠️  {flag}")


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("🧪 Running recommendation evals...")
    print(f"Testing {len(test_personas)} personas against {City.objects.count()} cities\n")

    total_explanations = 0
    total_passes = 0

    for persona in test_personas:
        # 1. Run scoring
        top_cities, user_prefs = run_scoring_eval(persona)

        # 2. Check scoring automatically
        scoring_flags = check_scoring(persona, top_cities)

        # 3. Generate explanations
        explanations = []
        for city_data in top_cities:
            exp = generate_explanation(city_data, user_prefs)
            explanations.append(exp)

        # 4. Judge each explanation
        judgements = []
        for i, exp in enumerate(explanations):
            judgement = judge_explanation(
                explanation=exp,
                persona=persona,
                city_name=top_cities[i]['city'].name,
                score_breakdown=top_cities[i]['breakdown']
            )
            judgements.append(judgement)

            if 'error' not in judgement:
                total_explanations += 1
                if compute_pass(judgement):
                    total_passes += 1

        # 5. Print report
        print_report(persona, top_cities, scoring_flags, explanations, judgements)

    # Summary
    print("\n" + "=" * 70)
    print("📋 EVAL SUMMARY")
    print("=" * 70)
    print(f"Explanations evaluated: {total_explanations}")
    print(f"Passed: {total_passes}/{total_explanations} "
          f"({round(total_passes/total_explanations*100) if total_explanations else 0}%)")
    print("✅ Eval complete")