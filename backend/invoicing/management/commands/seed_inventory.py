from django.core.management.base import BaseCommand
from invoicing.models import Item, Inventory

# A list of tuples. Each tuple contains:
# (item_name, item_description, unit_price_in_cents, stock_quantity)
ITEMS_TO_CREATE = [
    ("Laptop", "A high-performance laptop with 16GB RAM and 512GB SSD.", 120000, 10),
    ("Mouse", "A wireless optical mouse with ergonomic design.", 2500, 50),
    ("Keyboard", "A full-size mechanical keyboard with RGB backlighting.", 7500, 30),
    ("Monitor", "A 27-inch 4K UHD monitor with HDR support.", 35000, 15),
    ("Webcam", "A 1080p HD webcam with a built-in microphone.", 6000, 25),
    ("Docking Station", "A USB-C docking station with multiple ports.", 15000, 20),
]

class Command(BaseCommand):
    help = 'Seeds the database with initial Item and Inventory data.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Seeding database with Items and Inventory...'))
        
        for name, desc, price_cents, stock in ITEMS_TO_CREATE:
            # Use update_or_create to avoid creating duplicates if the command is run again.
            # It finds an object with the given parameters (name in this case) and either
            # updates it with the defaults or creates a new one.
            item, created = Item.objects.update_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'unit_price_cents': price_cents,
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'  -> Successfully created Item: "{name}"'))
            else:
                self.stdout.write(self.style.WARNING(f'  -> Item "{name}" already exists. Updating...'))

            # Create or update the corresponding inventory record for the item.
            inventory, inv_created = Inventory.objects.update_or_create(
                item=item,
                defaults={'quantity_on_hand': stock}
            )

            if inv_created:
                self.stdout.write(f'     - Created inventory with stock of {stock}.')
            else:
                self.stdout.write(f'     - Updated inventory stock to {stock}.')

        self.stdout.write(self.style.SUCCESS('Database seeding complete.'))