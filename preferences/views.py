from django.shortcuts import render, redirect
from .forms import PreferenceForm
from recommendations.recommendations_engine import get_recommendations
from users.models import UserProfile
from django.http import HttpResponse

def home(request):
    """Landing page"""
    return render(request, 'preferences/home.html')

def preference_questionnaire(request):
    """Display the preference form and handle submission"""
    
    if request.method == 'POST':
        form = PreferenceForm(request.POST)
        
        if form.is_valid():
            preferences = form.cleaned_data
            
            request.session['preferences'] = {
                'budget': preferences['budget'],
                'trip_length': preferences['trip_length'],
                'preferred_season': preferences['preferred_season'],
                'interests': ','.join(preferences['interests']),
                'languages': preferences.get('languages', 'English'),
                'departure_city': preferences.get('departure_city', ''),
                'departure_country': '',
                'transport_preference': preferences['transport_preference'],
            }
            
            # Clear cached recommendations when new preferences submitted
            request.session['recommendations'] = None
            
            return redirect('recommendations:results')
    else:
        form = PreferenceForm()
    
    return render(request, 'preferences/questionnaire.html', {'form': form})


def results(request):
    prefs = request.session.get('preferences', {})
    
    if not prefs:
        return redirect('preferences:questionnaire')
    
    # Use cached recommendations if already generated
    cached = request.session.get('recommendations')
    if cached:
        # Reconstruct full city objects from cached data
        from destinations.models import City
        recommendations = []
        for item in cached:
            try:
                city_obj = City.objects.get(id=item['city_id'])
                recommendations.append({
                    'city': city_obj,
                    'total_score': item['total_score'],
                    'breakdown': item['breakdown'],
                    'ai_explanation': item['ai_explanation'],
                })
            except City.DoesNotExist:
                continue
        return render(request, 'recommendations/results.html', {
            'recommendations': recommendations,
            'preferences': prefs,
        })
    
    # Generate fresh recommendations
    temp_profile = type('TempProfile', (), {
        'budget_preference': prefs.get('budget', 'moderate'),
        'preferred_trip_length': prefs.get('trip_length', '3-4'),
        'preferred_season': prefs.get('preferred_season', 'flexible'),
        'interests': prefs.get('interests', ''),
        'languages': prefs.get('languages', 'English'),
        'departure_city': prefs.get('departure_city', ''),
        'departure_country': prefs.get('departure_country', ''),
        'transport_preference': prefs.get('transport_preference', 'no_preference'),
    })()
    
    recommendations = get_recommendations(temp_profile, num_recommendations=3)
    
    # Cache serialisable version in session
    request.session['recommendations'] = [
        {
            'city_id': rec['city'].id,
            'total_score': rec['total_score'],
            'breakdown': rec['breakdown'],
            'ai_explanation': rec.get('ai_explanation', ''),
        }
        for rec in recommendations
    ]
    
    return render(request, 'recommendations/results.html', {
        'recommendations': recommendations,
        'preferences': prefs,
    })


def city_detail(request, city_id):
    """Detailed view of a recommended city"""
    from destinations.models import City, Attraction, Event
    
    prefs = request.session.get('preferences', {})
    
    if not prefs:
        return redirect('preferences:questionnaire')
    
    try:
        city = City.objects.get(id=city_id)
    except City.DoesNotExist:
        return redirect('recommendations:results')
    
    # Reconstruct recommendations from session cache — no Gemini calls
    cached = request.session.get('recommendations')
    
    if not cached:
        return redirect('recommendations:results')
    
    all_recommendations = []
    for item in cached:
        try:
            city_obj = City.objects.get(id=item['city_id'])
            all_recommendations.append({
                'city': city_obj,
                'total_score': item['total_score'],
                'breakdown': item['breakdown'],
                'ai_explanation': item['ai_explanation'],
            })
        except City.DoesNotExist:
            continue

    # Find this city's recommendation data
    city_rec = None
    city_index = None
    for i, rec in enumerate(all_recommendations):
        if rec['city'].id == city_id:
            city_rec = rec
            city_index = i
            break
    
    if not city_rec:
        return redirect('recommendations:results')
    
    # Get matching attractions based on user interests
    user_interests = [interest.strip() for interest in prefs.get('interests', '').split(',')]
    
    interest_category_map = {
        'Art Museums': ['museum_art'],
        'Art & Museums': ['museum_art'],
        'History & Architecture': ['museum_history', 'architecture', 'religious'],
        'Food & Culinary': ['food'],
        'Architecture': ['architecture'],
        'Nightlife & Entertainment': ['nightlife', 'cultural'],
        'Nature & Outdoors': ['nature', 'beach'],
        'Shopping': ['shopping'],
        'Beach & Relaxation': ['beach'],
        'Culture & Local Life': ['cultural', 'food'],
        'Adventure & Sports': ['nature'],
        'Wine & Gastronomy': ['food'],
        'Music & Festivals': ['cultural', 'nightlife'],
        'Photography': ['viewpoint', 'nature', 'architecture'],
    }
    
    relevant_categories = []
    for interest in user_interests:
        if interest in interest_category_map:
            relevant_categories.extend(interest_category_map[interest])
    
    matching_attractions = city.attractions.filter(
        category__in=relevant_categories
    ).order_by('-importance')[:6] if relevant_categories else []
    
    # Get matching events
    user_season = prefs.get('preferred_season', 'flexible')
    
    interest_event_map = {
        'Music & Festivals': ['festival', 'concert'],
        'Food & Culinary': ['food', 'market'],
        'Wine & Gastronomy': ['food'],
        'Culture & Local Life': ['cultural', 'festival', 'market'],
        'Nightlife & Entertainment': ['concert', 'cultural'],
        'Adventure & Sports': ['sports'],
        'Art Museums': ['cultural'],
        'Art & Museums': ['cultural'],
    }
    
    relevant_event_types = []
    for interest in user_interests:
        if interest in interest_event_map:
            relevant_event_types.extend(interest_event_map[interest])
    
    matching_events = []
    if user_season and user_season != 'flexible' and relevant_event_types:
        matching_events = city.events.filter(
            season=user_season,
            event_type__in=relevant_event_types
        )[:4]
    
    # Previous and next navigation
    previous_city_id = None
    next_city_id = None
    
    if city_index is not None:
        if city_index > 0:
            previous_city_id = all_recommendations[city_index - 1]['city'].id
        if city_index < len(all_recommendations) - 1:
            next_city_id = all_recommendations[city_index + 1]['city'].id
    
    context = {
        'city': city,
        'city_rec': city_rec,
        'preferences': prefs,
        'matching_attractions': matching_attractions,
        'matching_events': matching_events,
        'all_recommendations': all_recommendations,
        'current_index': city_index,
        'has_previous': city_index > 0 if city_index is not None else False,
        'has_next': city_index < len(all_recommendations) - 1 if city_index is not None else False,
        'previous_city_id': previous_city_id,
        'next_city_id': next_city_id,
    }
    
    return render(request, 'recommendations/city_detail.html', context)