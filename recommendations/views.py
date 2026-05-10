from django.shortcuts import render
from users.models import UserProfile
from .recommendations_engine import get_recommendations

def evaluation_dashboard(request):
    """
    Test dashboard showing recommendations for all simulated personas
    """
    
    # Get all simulated personas
    personas = UserProfile.objects.filter(is_simulated=True).order_by('name')
    
    # Generate recommendations for each persona
    results = []
    for persona in personas:
        recommendations = get_recommendations(persona, num_recommendations=3)
        results.append({
            'persona': persona,
            'recommendations': recommendations
        })
    
    context = {
        'results': results
    }
    
    return render(request, 'recommendations/evaluation.html', context)

