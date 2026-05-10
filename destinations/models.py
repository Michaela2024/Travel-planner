
from django.db import models

class City(models.Model):
    # Basic Information
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True)  # e.g., "Tuscany", "Catalonia"
    description = models. TextField()
    hero_image_url = models.URLField(max_length=500, blank=True, default='') 
    primary_categories = models.CharField(max_length=200, blank=True, help_text="Comma-separated: art,food,history")  # ADD THIS LINE
    highlights = models.TextField()
    highlights = models.TextField(help_text="What makes this city special")
    # Languages
    primary_language = models.CharField(max_length=50)
    other_languages = models.CharField(max_length=200, blank=True, help_text="Comma-separated")
    
    # Unesco world heritage sites
    # 
    # :
    is_unesco_heritage = models.BooleanField(
        default=False, 
        help_text="Has UNESCO World Heritage Site(s)"
    )
    unesco_sites = models.TextField(
        blank=True, 
        help_text="List UNESCO World Heritage sites in this city"
    )
    # Climate & Seasons
    best_seasons = models.CharField(max_length=200, help_text="e.g., 'Spring,autumn'")
    
    CATEGORY_CHOICES = [
    ('art', 'Art & Museums'),
    ('history', 'History & Architecture'),
    ('food', 'Food & Culinary'),
    ('nature', 'Nature & Outdoors'),
    ('beach', 'Beach & Relaxation'),
    ('nightlife', 'Nightlife & Entertainment'),
    ('culture', 'Culture & Local Life'),
    ('adventure', 'Adventure & Sports'),
    ('wine', 'Wine & Gastronomy'),
    ('music', 'Music & Festivals'),
]
    # Cost Information
    COST_LEVEL_CHOICES = [
        ('budget', 'Budget-Friendly'),
        ('moderate', 'Moderate'),
        ('luxury', 'Luxury'),
    ]
    cost_level = models.CharField(max_length=20, choices=COST_LEVEL_CHOICES)
    avg_hotel_cost_per_night = models.DecimalField(max_digits=6, decimal_places=2)
    avg_meal_cost = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Characteristics
    description = models.TextField()
    highlights = models.TextField(help_text="What makes this city special")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Cities"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name}, {self.country}"# Create your models here.
    

class Attraction(models.Model):
    # Relationship
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='attractions')
    
    # Basic Info
    name = models.CharField(max_length=200)
    
    CATEGORY_CHOICES = [
        ('museum_art', 'Art Museum'),
        ('museum_history', 'History Museum'),
        ('museum_science', 'Science Museum'),
        ('architecture', 'Architecture & Monuments'),
        ('nature', 'Nature & Parks'),
        ('beach', 'Beach'),
        ('cultural', 'Cultural Venue'),
        ('food', 'Food & Markets'),
        ('nightlife', 'Nightlife'),
        ('shopping', 'Shopping'),
        ('religious', 'Religious Site'),
        ('viewpoint', 'Viewpoint'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    
    description = models.TextField()
    
    # Pricing
    is_free = models.BooleanField(default=False)
    entry_fee = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Popularity/Importance
    IMPORTANCE_CHOICES = [
        (1, 'Must See'),
        (2, 'Highly Recommended'),
        (3, 'Worth Visiting'),
        (4, 'Optional'),
    ]
    importance = models.IntegerField(choices=IMPORTANCE_CHOICES, default=3)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['importance', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.city.name})"
    
class Event(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='events')
    name=models. CharField(max_length=200)

    EVENT_TYPE_CHOICES = [
        ('festival', 'Festival'),
        ('market', 'Market'),
        ('concert', 'Concert/Music'),
        ('sports', 'Sports Event'),
        ('cultural', 'Cultural Event'),
        ('food', 'Food & Wine Event'),
        ('seasonal', 'Seasonal Event'),
    ]
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    
    description = models.TextField()
    
    # Timing
    SEASON_CHOICES = [
        ('winter', 'Winter'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('autumn', 'Autumn'),
        ('year_round', 'Year Round'),
    ]
    season = models.CharField(max_length=20, choices=SEASON_CHOICES)
    
    # More specific timing (optional)
    specific_months = models.CharField(max_length=100, blank=True, help_text="e.g., 'December', 'June-August'")
    
    # Pricing
    is_free = models.BooleanField(default=False)
    typical_cost = models.CharField(max_length=100, blank=True, help_text="e.g., '€20-50'")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['season', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.city.name} ({self.get_season_display()})"
