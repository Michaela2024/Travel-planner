from destinations.models import City, Attraction, Event
from decimal import Decimal
from .gemini_integration import generate_city_explanation
from concurrent.futures import ThreadPoolExecutor


def calculate_city_score(city, user_preferences):
    """
    Calculate how well a city matches user preferences.
    
    Scoring System (100 points max):
    - Budget matching: 30 points
    - Interest matching: 35 points  
    - Language matching: 10 points
    - Seasonal preference: 10 points
    - Transport & accessibility: 10 points
    - UNESCO heritage bonus: 5 points (when relevant to interests)
    """
    
    total_score = 0
    score_breakdown = {}
    
    # 1. BUDGET MATCHING (30 points max)
    budget_score = 0
    user_budget = user_preferences['budget']
    
    if city.cost_level == user_budget:
        budget_score = 30
    elif (user_budget == 'moderate' and city.cost_level in ['budget', 'luxury']):
        budget_score = 15
    elif (user_budget == 'budget' and city.cost_level == 'moderate'):
        budget_score = 15
    elif (user_budget == 'luxury' and city.cost_level == 'moderate'):
        budget_score = 20
    else:
        budget_score = 0
    
    total_score += budget_score
    score_breakdown['budget'] = budget_score

    # 2. INTEREST MATCHING (35 points max)
    interest_score = 0
    user_interests = [interest.strip() for interest in user_preferences['interests']]

    if user_interests and city.primary_categories:
        interest_category_map = {
            'Art Museums': ['art'],
            'Art & Museums': ['art'],
            'History & Architecture': ['history'],
            'Food & Culinary': ['food'],
            'Architecture': ['history', 'culture'],
            'Nightlife & Entertainment': ['nightlife', 'culture'],
            'Nature & Outdoors': ['nature'],
            'Shopping': ['culture'],
            'Beach & Relaxation': ['beach'],
            'Culture & Local Life': ['culture'],
            'Adventure & Sports': ['adventure', 'nature'],
            'Wine & Gastronomy': ['wine', 'food'],
            'Music & Festivals': ['music', 'culture'],
            'Photography': ['art', 'nature', 'culture'],
        }
        
        city_categories = [cat.strip() for cat in city.primary_categories.split(',')]
        
        matches = 0
        for interest in user_interests:
            if interest in interest_category_map:
                mapped_categories = interest_category_map[interest]
                if any(cat in city_categories for cat in mapped_categories):
                    matches += 1
        
        interest_score = min(matches * 7, 35)
    
    total_score += interest_score
    score_breakdown['interests'] = interest_score

    # 3. LANGUAGE MATCHING (10 points max)
    language_score = 0
    user_languages = [lang.strip() for lang in user_preferences['languages']]
    
    if user_languages:
        if city.primary_language in user_languages:
            language_score = 10
        elif city.other_languages:
            city_other_langs = [lang.strip() for lang in city.other_languages.split(',')]
            if any(lang in user_languages for lang in city_other_langs):
                language_score = 7
        elif 'English' in user_languages:
            language_score = 5
    
    total_score += language_score
    score_breakdown['language'] = language_score

    # 4. SEASONAL PREFERENCE (10 points max)
    season_score = 0
    user_season = user_preferences['season']
    
    if user_season and user_season != 'flexible' and city.best_seasons:
        city_seasons = city.best_seasons.lower()
        
        if user_season.lower() in city_seasons:
            season_score = 10
        elif (user_season == 'spring' and ('spring' in city_seasons or 'autumn' in city_seasons)) or \
             (user_season == 'autumn' and ('autumn' in city_seasons or 'spring' in city_seasons)):
            season_score = 5

    total_score += season_score
    score_breakdown['season'] = season_score

    # 5. TRANSPORT & ACCESSIBILITY (10 points max)
    transport_score = 0
    departure_city_name = user_preferences.get('departure_city', '').strip().lower()
    transport_pref = user_preferences.get('transport', 'no_preference')

    departure_city_to_country = {
        # UK
        'london': 'UK', 'manchester': 'UK', 'birmingham': 'UK', 'edinburgh': 'UK',
        'glasgow': 'UK', 'bristol': 'UK', 'leeds': 'UK', 'liverpool': 'UK',
        'oxford': 'UK', 'cambridge': 'UK', 'bath': 'UK', 'york': 'UK','didcot': 'UK', 'reading': 'UK', 'brighton': 'UK', 'Southampton': 'UK',
        'newcastle': 'UK', 'nottingham': 'UK', 'sheffield': 'UK', 'cardiff': 'UK',
        'belfast': 'UK',
        # France
        'paris': 'France', 'lyon': 'France', 'marseille': 'France', 'bordeaux': 'France',
        'toulouse': 'France', 'nice': 'France', 'strasbourg': 'France', 'nantes': 'France',
        # Germany
        'berlin': 'Germany', 'munich': 'Germany', 'hamburg': 'Germany', 'frankfurt': 'Germany',
        'cologne': 'Germany', 'düsseldorf': 'Germany', 'stuttgart': 'Germany', 'dresden': 'Germany',
        # Netherlands
        'amsterdam': 'Netherlands', 'rotterdam': 'Netherlands', 'the hague': 'Netherlands',
        'utrecht': 'Netherlands', 'eindhoven': 'Netherlands',
        # Belgium
        'brussels': 'Belgium', 'antwerp': 'Belgium', 'ghent': 'Belgium', 'bruges': 'Belgium',
        # Spain
        'madrid': 'Spain', 'barcelona': 'Spain', 'seville': 'Spain', 'valencia': 'Spain',
        'bilbao': 'Spain', 'malaga': 'Spain', 'granada': 'Spain',
        # Italy
        'rome': 'Italy', 'milan': 'Italy', 'florence': 'Italy', 'venice': 'Italy',
        'naples': 'Italy', 'turin': 'Italy', 'bologna': 'Italy',
        # Portugal
        'lisbon': 'Portugal', 'porto': 'Portugal', 'faro': 'Portugal',
        # Switzerland
        'zurich': 'Switzerland', 'geneva': 'Switzerland', 'basel': 'Switzerland', 'bern': 'Switzerland',
        # Austria
        'vienna': 'Austria', 'salzburg': 'Austria', 'graz': 'Austria', 'innsbruck': 'Austria',
        # Scandinavia
        'copenhagen': 'Denmark', 'oslo': 'Norway', 'stockholm': 'Sweden', 'helsinki': 'Finland',
        'gothenburg': 'Sweden', 'malmo': 'Sweden', 'bergen': 'Norway',
        # Ireland
        'dublin': 'Ireland', 'cork': 'Ireland', 'galway': 'Ireland',
        # Poland
        'warsaw': 'Poland', 'krakow': 'Poland', 'gdansk': 'Poland', 'wroclaw': 'Poland',
        # Czech Republic
        'prague': 'Czech Republic', 'brno': 'Czech Republic',
        # Hungary
        'budapest': 'Hungary', 'debrecen': 'Hungary',
        # Greece
        'athens': 'Greece', 'thessaloniki': 'Greece',
        # Other
        'regensburg': 'Germany', 'luxembourg': 'Luxembourg', 'valletta': 'Malta',
        'zagreb': 'Croatia', 'ljubljana': 'Slovenia', 'bratislava': 'Slovakia',
        'bucharest': 'Romania', 'sofia': 'Bulgaria', 'belgrade': 'Serbia',
    }

    departure_country = departure_city_to_country.get(departure_city_name, '')

    western_europe = ['France', 'Germany', 'Netherlands', 'Belgium', 'Austria', 'Switzerland', 'Luxembourg']
    southern_europe = ['Italy', 'Spain', 'Portugal', 'Greece', 'Croatia']
    central_europe = ['Czech Republic', 'Poland', 'Hungary', 'Slovakia', 'Slovenia']
    northern_europe = ['Denmark', 'Sweden', 'Norway', 'Finland']

    def get_proximity_score(dep_country, city_country, t_pref):
        if dep_country and city_country.lower() == dep_country.lower():
            return 10
        if city_country in western_europe:
            base = 8
        elif city_country in central_europe or city_country in northern_europe:
            base = 6
        elif city_country in southern_europe:
            base = 5
        else:
            base = 3
        if t_pref == 'prefer_flight':
            return min(base + 1, 10)
        elif t_pref in ['prefer_train', 'train_only']:
            return max(base - 1, 0)
        else:
            return base

    if departure_city_name:
        transport_score = get_proximity_score(departure_country, city.country, transport_pref)
    else:
        transport_score = 5

    total_score += transport_score
    score_breakdown['transport'] = transport_score

    # 6. UNESCO HERITAGE BONUS (5 points max)
    unesco_score = 0
    
    if city.is_unesco_heritage:
        unesco_score = 3
        if any(interest in ['History & Architecture', 'Culture & Local Life', 'Photography']
               for interest in user_interests):
            unesco_score = 5
    
    total_score += unesco_score
    score_breakdown['unesco'] = unesco_score

    return {
        'city': city,
        'total_score': total_score,
        'breakdown': score_breakdown
    }


def get_recommendations(user_profile, num_recommendations=3):
    
    user_prefs = {
        'budget': user_profile.budget_preference,
        'interests': user_profile.interests.split(','),
        'languages': user_profile.languages.split(','),
        'season': user_profile.preferred_season,
        'departure_city': user_profile.departure_city,
        'departure_country': '',
        'transport': user_profile.transport_preference,
    }
    
    all_cities = City.objects.all()
    
    departure_city = user_prefs.get('departure_city', '').strip()
    if departure_city:
        all_cities = all_cities.exclude(name__iexact=departure_city)
    
    scored_cities = []
    for city in all_cities:
        score_data = calculate_city_score(city, user_prefs)
        scored_cities.append(score_data)
    
    scored_cities.sort(key=lambda x: x['total_score'], reverse=True)
    top_cities = scored_cities[:num_recommendations]
    

    def fetch_explanation(score_data):
        # Only generate AI explanation for top city
        top_cities[0]['ai_explanation'] = generate_city_explanation(
            city=top_cities[0]['city'],
            user_preferences=user_prefs,
            score_breakdown=top_cities[0]['breakdown'],
            total_score=top_cities[0]['total_score']
    )

    # Simple score-based text for #2 and #3
    for rec in top_cities[1:]:
        bd = rec['breakdown']
        strengths = []
        if bd.get('budget', 0) >= 25:
            strengths.append('budget')
        if bd.get('interests', 0) >= 14:
            strengths.append('interests')
        if bd.get('season', 0) >= 8:
            strengths.append('season')
        if bd.get('transport', 0) >= 7:
            strengths.append('accessibility')
        if bd.get('unesco', 0) >= 5:
            strengths.append('cultural heritage')

        if strengths:
            rec['ai_explanation'] = f"{rec['city'].name} scores well on {', '.join(strengths)}. View full details for a personalised recommendation."
        else:
            rec['ai_explanation'] = f"{rec['city'].name} is a solid match based on your overall preferences. View full details for a personalised recommendation."

    # Remove ThreadPoolExecutor — no longer needed
    return top_cities
    