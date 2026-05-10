
from django.contrib import admin
from .models import Recommendation

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['rank', 'city', 'get_user_name', 'score', 'weighted_score', 'ai_score', 'created_at']
    list_filter = ['rank', 'city', 'created_at']
    search_fields = ['city__name', 'preference_submission__user_profile__name', 'match_reasoning']
    readonly_fields = ['created_at']
    
    def get_user_name(self, obj):
        return obj.preference_submission.user_profile.name
    get_user_name.short_description = 'User'
