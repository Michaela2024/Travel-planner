from django.db import models
from preferences.models import PreferenceSubmission
from destinations.models import City

class Recommendation(models.Model):
    # What search generated this recommendation
    preference_submission = models.ForeignKey(
        PreferenceSubmission, 
        on_delete=models.CASCADE, 
        related_name='recommendations'
    )
    
    # Which city is being recommended
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    
    # Scoring
    score = models.DecimalField(max_digits=5, decimal_places=2, help_text="Total score (0-100)")
    weighted_score = models.DecimalField(max_digits=5, decimal_places=2, help_text="Algorithm score")
    ai_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Gemini API score")
    
    # AI-Generated Content
    match_reasoning = models.TextField(blank=True, help_text="Why this city matches (from Gemini)")
    personalized_description = models.TextField(blank=True, help_text="Custom description for user")
    
    # Ranking
    rank = models.IntegerField(help_text="Position in results (1=best match)")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['preference_submission', 'rank']
        unique_together = ['preference_submission', 'city']  # Can't recommend same city twice in one search
    
    def __str__(self):
        return f"#{self.rank}: {self.city.name} (Score: {self.score}) for {self.preference_submission.user_profile.name}"