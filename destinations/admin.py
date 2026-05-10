from django.contrib import admin
from .models import City, Attraction, Event

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'cost_level', 'primary_language')
    list_filter = ('country', 'cost_level', 'best_seasons')
    search_fields = ('name', 'country', 'region')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'country', 'region')
        }),
        ('Languages', {
            'fields': ('primary_language', 'other_languages')
        }),
        ('Travel Details', {
            'fields': ('best_seasons', 'cost_level', 'avg_hotel_cost_per_night', 'avg_meal_cost')
        }),
        ('Description & Media', {  # ← UPDATE THIS SECTION
            'fields': ('description', 'hero_image_url', 'highlights')  # ← ADD hero_image_url HERE
        }),
        ('UNESCO Heritage', {
            'fields': ('is_unesco_heritage', 'unesco_sites')
        }),
    )

@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'category', 'importance', 'is_free']
    list_filter = ['category', 'importance', 'is_free', 'city']
    search_fields = ['name', 'city__name']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'event_type', 'season', 'is_free']
    list_filter = ['event_type', 'season', 'is_free', 'city']
    search_fields = ['name', 'city__name']


