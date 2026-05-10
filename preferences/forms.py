from django import forms

class PreferenceForm(forms.Form):
    # Budget
    BUDGET_CHOICES = [
        ('budget', 'Budget-Friendly (€50-100/day)'),
        ('moderate', 'Moderate (€100-200/day)'),
        ('luxury', 'Luxury (€200+/day)'),
    ]
    budget = forms.ChoiceField(
        choices=BUDGET_CHOICES,
        widget=forms.RadioSelect,
        label='What is your budget?'
    )
    
    # Trip Length
    TRIP_LENGTH_CHOICES = [
        ('2-3', '2-3 days'),
        ('3-4', '3-4 days'),
        ('5-7', '5-7 days'),
        ('7+', '7+ days'),
    ]
    trip_length = forms.ChoiceField(
    choices=TRIP_LENGTH_CHOICES,
    widget=forms.RadioSelect,
    label='How long is your trip?',
    required=False
)
    
    # Season
    SEASON_CHOICES = [
        ('winter', 'Winter (Dec-Feb)'),
        ('spring', 'Spring (Mar-May)'),
        ('summer', 'Summer (Jun-Aug)'),
        ('autumn', 'Autumn (Sep-Nov)'),
        ('flexible', 'Flexible'),
    ]
    preferred_season = forms.ChoiceField(
        choices=SEASON_CHOICES,
        widget=forms.RadioSelect,
        label='When are you traveling?'
    )
    
    # Interests (Multiple Choice)
    INTEREST_CHOICES = [
        ('Art Museums', 'Art & Museums'),
        ('History & Architecture', 'History & Architecture'),
        ('Food & Culinary', 'Food & Culinary'),
        ('Nightlife & Entertainment', 'Nightlife & Entertainment'),
        ('Nature & Outdoors', 'Nature & Outdoors'),
        ('Shopping', 'Shopping'),
        ('Beach & Relaxation', 'Beach & Relaxation'),
        ('Culture & Local Life', 'Culture & Local Life'),
        ('Adventure & Sports', 'Adventure & Sports'),
        ('Wine & Gastronomy', 'Wine & Gastronomy'),
        ('Music & Festivals', 'Music & Festivals'),
        ('Photography', 'Photography'),
    ]
    interests = forms.MultipleChoiceField(
        choices=INTEREST_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label='What interests you? (Select all that apply)'
    )
    
    # Languages
    languages = forms.CharField(
        max_length=200,
        label='What languages do you speak?',
        help_text='Comma-separated (e.g., English, French, Spanish)',
        required=False
    )
    
    # Departure Location
    departure_city = forms.CharField(
        max_length=100,
        label='Where are you traveling from? (City)',
        required=False
    )
    
    
    # Transport Preference
    TRANSPORT_CHOICES = [
        ('no_preference', 'No Preference'),
        ('prefer_train', 'Prefer Train'),
        ('prefer_flight', 'Prefer Flight'),
        ('train_only', 'Train Only (Avoid Flying)'),
    ]
    transport_preference = forms.ChoiceField(
        choices=TRANSPORT_CHOICES,
        widget=forms.RadioSelect,
        label='Transport preference?'
    )