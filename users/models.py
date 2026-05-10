from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    # Link to Django's built-in User model (optional - for when you add authentication later)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Profile Info
    name = models.CharField(max_length=100, help_text="Name or persona description")
    is_simulated = models.BooleanField(default=False, help_text="Is this a test persona?")
    
    bio = models.TextField(blank=True, help_text="Rich persona backstory for portfolio demo")
    age = models.IntegerField(null=True, blank=True, help_text="Persona age")
    occupation = models.CharField(max_length=100, blank=True, help_text="Persona occupation")
    
    # ADD THESE NEW FIELDS HERE:
    departure_city = models.CharField(max_length=100, blank=True, help_text="Where are you traveling from?")
    departure_country = models.CharField(max_length=100, blank=True, help_text="Departure country")
    
    TRANSPORT_CHOICES = [
        ('no_preference', 'No Preference'),
        ('prefer_train', 'Prefer Train'),
        ('prefer_flight', 'Prefer Flight'),
        ('train_only', 'Train Only (Avoid Flying)'),
        ('bus_ok', 'Open to Bus/Coach'),
    ]
    transport_preference = models.CharField(
        max_length=20, 
        choices=TRANSPORT_CHOICES, 
        default='no_preference',
        help_text="Preferred mode of transport"
    )
    # Budget Preferences
    BUDGET_CHOICES = [
        ('budget', 'Budget-Friendly (€50-100/day)'),
        ('moderate', 'Moderate (€100-200/day)'),
        ('luxury', 'Luxury (€200+/day)'),
    ]
    budget_preference = models.CharField(max_length=20, choices=BUDGET_CHOICES)
    
    # Trip Length Preferences
    TRIP_LENGTH_CHOICES = [
        ('2-3', '2-3 days'),
        ('3-4', '3-4 days'),
        ('5-7', '5-7 days'),
        ('7+', '7+ days'),
    ]
    preferred_trip_length = models.CharField(max_length=10, choices=TRIP_LENGTH_CHOICES)
    
    # Language Preferences (stored as comma-separated)
    languages = models.CharField(max_length=200, help_text="Comma-separated, e.g., 'English,Spanish'")
    
    # Interests (stored as comma-separated)
    interests = models.TextField(help_text="Comma-separated interests")
    
    # Travel Period
    SEASON_CHOICES = [
        ('winter', 'Winter (Dec-Feb)'),
        ('spring', 'Spring (Mar-May)'),
        ('summer', 'Summer (Jun-Aug)'),
        ('autumn', 'Autumn (Sep-Nov)'),
        ('flexible', 'Flexible'),
    ]
    preferred_season = models.CharField(max_length=20, choices=SEASON_CHOICES, default='flexible')
    
    # Additional Notes
    notes = models.TextField(blank=True, help_text="Additional preferences or persona description")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        persona_type = " (Simulated)" if self.is_simulated else ""
        return f"{self.name}{persona_type}"