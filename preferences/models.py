from django.db import models
from users.models import UserProfile

class PreferenceSubmission(models.Model):
    # Link to user profile
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='submissions')
    
    # What they searched for
    budget = models.CharField(max_length=20)
    trip_length = models.CharField(max_length=10)
    languages = models.CharField(max_length=200)
    interests = models.TextField()
    preferred_season = models.CharField(max_length=20)

    # ADD THESE:
    departure_city = models.CharField(max_length=100, blank=True)
    departure_country = models.CharField(max_length=100, blank=True)
    
    TRANSPORT_CHOICES = [
        ('no_preference', 'No Preference'),
        ('prefer_train', 'Prefer Train'),
        ('prefer_flight', 'Prefer Flight'),
        ('train_only', 'Train Only (Avoid Flying)'),
        ('bus_ok', 'Open to Bus/Coach'),
    ]
    transport_preference = models.CharField(max_length=20, choices=TRANSPORT_CHOICES, default='no_preference')
    
    # When they searched
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: Store any special notes from this search
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Preference Submission"
        verbose_name_plural = "Preference Submissions"
    
    def __str__(self):
        return f"{self.user_profile.name} - {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"