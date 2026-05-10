from django.urls import path
from . import views

app_name = 'preferences'

urlpatterns = [
    path('', views.home, name='home'),  # Home page at /
    path('questionnaire/', views.preference_questionnaire, name='questionnaire'),  # Questionnaire at /questionnaire/
    path('city/<int:city_id>/', views.city_detail, name='city_detail'),
]