import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
import time

client = Client()

response = client.post('/questionnaire/', {
    'budget': 'budget',
    'trip_length': '3-4',
    'preferred_season': 'spring',
    'interests': ['History & Architecture', 'Culture & Local Life'],
    'languages': 'English',
    'departure_city': 'London',
    'departure_country': 'UK',
    'transport_preference': 'prefer_train',
})

print(f"Status: {response.status_code}")
print(f"Redirect: {response.get('Location', 'No redirect')}")

if response.status_code == 302:
    start = time.time()
    results = client.get(response['Location'])
    elapsed = time.time() - start
    print(f"Results status: {results.status_code}")
    print(f"Load time: {elapsed:.1f} seconds")