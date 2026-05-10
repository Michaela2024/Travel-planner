from django.contrib import admin
from .models import PreferenceSubmission

@admin.register(PreferenceSubmission)
class PreferenceSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user_profile', 'budget', 'trip_length', 'preferred_season', 'submitted_at']
    list_filter = ['budget', 'trip_length', 'preferred_season', 'submitted_at']
    search_fields = ['user_profile__name', 'interests', 'languages']
    date_hierarchy = 'submitted_at'
    readonly_fields = ['submitted_at']