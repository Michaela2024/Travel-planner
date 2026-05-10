import csv
from django.core.management.base import BaseCommand
from destinations.models import City

class Command(BaseCommand):
    help = 'Update city hero images from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    city = City.objects.get(name=row['name'])
                    city.hero_image_url = row['hero_image_url']
                    city.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Updated image for: {row["name"]}')
                    )
                    
                except City.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'✗ City not found: {row["name"]}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Error: {str(e)}')
                    )
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Import complete!'))