from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_simulated', 'budget_preference', 'preferred_trip_length', 'preferred_season']
    list_filter = ['is_simulated', 'budget_preference', 'preferred_trip_length', 'preferred_season']
    search_fields = ['name', 'bio', 'occupation']
    
    fieldsets = (
    ('Profile Info', {
        'fields': ('user', 'name', 'is_simulated', 'bio', 'age', 'occupation')
    }),
    ('Location & Transport', {
        'fields': ('departure_city', 'departure_country', 'transport_preference')
    }),
    ('Travel Preferences', {
        'fields': ('budget_preference', 'preferred_trip_length', 'languages', 'interests', 'preferred_season')
    }),
    ('Additional', {
        'fields': ('notes',)
    }),
)


