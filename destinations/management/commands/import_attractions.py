import csv
from django.core.management.base import BaseCommand
from destinations.models import City, Attraction

class Command(BaseCommand):
    help = 'Import attractions from CSV file'

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
                    
                    # Create the attraction (skip entry_fee field)
                    Attraction.objects.create(
                        city=city,
                        name=row['name'],
                        category=row['category'],
                        description=row['description'],
                        is_free=row['is_free'].lower() == 'true',
                        entry_fee= None,  # Leave blank
                        importance=int(row['importance'])
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created: {row["name"]} in {row["city_name"]}')
                    )
                    
                except City.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'✗ City not found: {row["city_name"]}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Error with {row.get("name", "unknown")}: {str(e)}')
                    )
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Import complete!'))