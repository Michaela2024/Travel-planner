from google import genai
from django.conf import settings
from google.genai import types


def generate_city_explanation(city, user_preferences, score_breakdown, total_score):
    """
    Generate personalized explanation for why a city matches the user.
    """

    interest_score = score_breakdown.get('interests', 0)
    season_score = score_breakdown.get('season', 0)
    transport_score = score_breakdown.get('transport', 0)
    departure_city = user_preferences.get('departure_city', 'their home city')

    if interest_score >= 25:
        interest_instruction = "The city is a strong match for their interests. You may describe this positively."
    elif interest_score >= 15:
        interest_instruction = "The city has moderate interest alignment. Mention relevant aspects but do not overstate the match."
    else:
        interest_instruction = "The city has limited interest alignment. Acknowledge one or two relevant aspects honestly but do not describe it as a strong or perfect interest match."

    if season_score == 0:
        season_instruction = "This season is NOT ideal for this city. Do not describe the season as a good time to visit."
    elif season_score >= 8:
        season_instruction = "This is a good season to visit. You may reference it positively."
    else:
        season_instruction = "This season is acceptable but not the city's best. Mention it neutrally."

    if transport_score >= 7:
        transport_instruction = "You may briefly note the city is accessible from the user's departure city, but do NOT name specific routes, services, connections, or journey times."
    else:
        transport_instruction = "STRICT RULE: Do not mention any transport at all — no routes, no journey times, no specific services like Nightjet or Eurostar, no connections via other cities. Transport information is handled elsewhere."
    
    prompt = f"""You are a knowledgeable, well-travelled European travel advisor. You know Europe well and you know where the traveller lives. You give honest, specific recommendations — like a trusted friend who happens to know every city on the continent.

CRITICAL CONSTRAINTS — read before writing:

1. INTEREST ALIGNMENT: {interest_instruction}
2. SEASON: {season_instruction}  
3. TRANSPORT: {transport_instruction}
4. HOME CITY AWARENESS: The user is from {departure_city}. Do not recommend things they already have easy access to at home. If recommending food, wine, architecture, or culture — explain what makes it genuinely different from what they know at home.
5. TONE: Write in an understated, intelligent European tone. No hyperbole. No "absolute dream", "utterly enchanted", "magical", "paradise", "perfect escape". Maximum one exclamation mark, ideally none. One specific well-chosen detail is more persuasive than three superlatives.
6. LENGTH: 2-3 sentences only.

USER PROFILE:
- Budget: {user_preferences.get('budget', 'Not specified')}
- Interests: {user_preferences.get('interests', 'Not specified')}
- Preferred Season: {user_preferences.get('season', 'Not specified')}
- Languages: {user_preferences.get('languages', 'Not specified')}
- Travelling from: {departure_city}, {user_preferences.get('departure_country', '')}
- Transport preference: {user_preferences.get('transport', 'Not specified')}

CITY: {city.name}, {city.country}
- Cost Level: {city.cost_level}
- Primary Language: {city.primary_language}
- Description: {city.description}

MATCH SCORE: {total_score}/100 points
BREAKDOWN:
- Budget Match: {score_breakdown.get('budget', 0)}/30
- Interest Match: {interest_score}/35
- Language Match: {score_breakdown.get('language', 0)}/10
- Seasonal Match: {season_score}/10
- Transport Match: {transport_score}/10
- UNESCO Bonus: {score_breakdown.get('unesco', 0)}/5

Write a 2-3 sentence recommendation that is honest about the match quality, specific to this city, and aware of where the traveller is coming from. Start directly with the city — no preamble."""

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2)
        )
        return response.text.strip()

    except Exception as e:
        print(f"Gemini API error: {e}")
        return f"{city.name} scored {total_score} points based on your preferences, with particularly strong matches in your interests and budget requirements."