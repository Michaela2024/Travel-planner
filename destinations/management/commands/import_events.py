import csv
from django.core.management.base import BaseCommand
from destinations.models import City, Event

class Command(BaseCommand):
    help = 'Import events from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    # Find the city
                    city = City.objects.get(name=row['city_name'])
                    
                    # Create the event
                    Event.objects.create(
                        city=city,
                        name=row['event_name'],
                        event_type=row['event_type'],
                        description=row['description'],
                        season=row['season'],
                        specific_months=row['specific_months'],
                        is_free=row['is_free'].lower() == 'true',
                        typical_cost=row['typical_cost'] if row['typical_cost'] else ''
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created event: {row["event_name"]} in {row["city_name"]}')
                    )
                    
                except City.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'✗ City not found: {row["city_name"]}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Error: {str(e)}')
                    )
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Import complete!'))