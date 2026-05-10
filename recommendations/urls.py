from django.urls import path
from preferences import views as pref_views
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('results/', pref_views.results, name='results'),
    path('evaluation/', views.evaluation_dashboard, name='evaluation'),
]