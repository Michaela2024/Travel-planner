import csv
from django.core.management.base import BaseCommand
from destinations.models import City

class Command(BaseCommand):
    help = 'Import cities from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    # Create or update the city
                    city, created = City.objects.update_or_create(
                        name=row['name'],
                        country=row['country'],
                        defaults={
                            'region': row['region'],
                            'primary_language': row['primary_language'],
                            'other_languages': row['other_languages'],
                            'best_seasons': row['best_seasons'],
                            'cost_level': row['cost_level'],
                            'avg_hotel_cost_per_night': row['avg_hotel_cost_per_night'],
                            'avg_meal_cost': row['avg_meal_cost'],
                            'description': row['description'],
                            'highlights': row['highlights'],
                            'is_unesco_heritage': row['is_unesco_heritage'].lower() == 'true',
                            'unesco_sites': row['unesco_sites'] if row['unesco_sites'] else ''
                        }
                    )
                    
                    action = 'Created' if created else 'Updated'
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ {action}: {row["name"]}, {row["country"]}')
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Error with {row.get("name", "unknown")}: {str(e)}')
                    )
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Import complete!'))