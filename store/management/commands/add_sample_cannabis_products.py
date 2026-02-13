from django.core.management.base import BaseCommand
from store.models import Category, Brand, Product

class Command(BaseCommand):
    help = 'Create sample cannabis products (blunt and joint)'

    def handle(self, *args, **options):
        cat, _ = Category.objects.get_or_create(name='Cannabis', slug='cannabis')
        brand, _ = Brand.objects.get_or_create(name='Sample Brand', slug='sample-brand')

        blunt, created = Product.objects.get_or_create(
            slug='sample-blunt',
            defaults={
                'category': cat,
                'brand': brand,
                'name': 'Sample Blunt',
                'description': 'Hand-rolled sample blunt. For demo purposes only.',
                'price': 12.00,
                'original_price': 15.00,
                'stock': 50,
                'is_available': True,
                'is_cannabis': True,
                'cannabis_type': 'pre-roll',
                'thc_percentage': 18.5,
                'cbd_percentage': 0.2,
                'unit_weight_g': 1.0,
                'package_amount': '1 blunt',
                'metrc_tag': '',
            }
        )

        joint, created = Product.objects.get_or_create(
            slug='sample-joint',
            defaults={
                'category': cat,
                'brand': brand,
                'name': 'Sample Joint',
                'description': 'Single sample joint. For demo purposes only.',
                'price': 5.00,
                'original_price': 6.00,
                'stock': 100,
                'is_available': True,
                'is_cannabis': True,
                'cannabis_type': 'pre-roll',
                'thc_percentage': 16.0,
                'cbd_percentage': 0.1,
                'unit_weight_g': 0.5,
                'package_amount': '1 joint',
                'metrc_tag': '',
            }
        )

        self.stdout.write(self.style.SUCCESS('Sample cannabis products created/updated.'))
