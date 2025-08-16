# app_name/management/commands/seed_products.py
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from decimal import Decimal
import random
import uuid
from datetime import date, timedelta

from farmers_app.models import FarmerProfile
from farmers_app.models import Category, SubCategory, Product  # Adjust app names accordingly


class Command(BaseCommand):
    help = "Seed the database with real product categories, subcategories, and products"

    def handle(self, *args, **kwargs):
        # Ensure there is at least one farmer
        farmers = FarmerProfile.objects.all()
        if not farmers.exists():
            self.stdout.write(self.style.ERROR("No FarmerProfile found! Please create at least one farmer."))
            return

        farmer = random.choice(farmers)

        categories_data = [
            {
                "name": "Crops",
                "description": "Fresh and seasonal crops from local farms.",
                "subcategories": {
                    "Vegetables": ["Kale (Sukuma Wiki)", "Spinach", "Cabbage", "Tomatoes"],
                    "Fruits": ["Mangoes", "Bananas", "Pineapples"],
                },
            },
            {
                "name": "Livestock",
                "description": "Healthy livestock raised with care.",
                "subcategories": {
                    "Cattle": ["Dairy Cow", "Beef Cattle"],
                    "Goats": ["Boer Goat", "Local Goat"],
                },
            },
            {
                "name": "Poultry",
                "description": "Egg and meat producing poultry.",
                "subcategories": {
                    "Chickens": ["Improved Kienyeji", "Layers", "Broilers"],
                    "Ducks": ["Pekin Duck", "Muscovy Duck"],
                },
            },
            {
                "name": "Dairy",
                "description": "Fresh dairy products.",
                "subcategories": {
                    "Milk": ["Fresh Cow Milk", "Goat Milk"],
                    "Cheese": ["Cheddar Cheese", "Mozzarella"],
                },
            },
            {
                "name": "Fish",
                "description": "Freshwater and farmed fish.",
                "subcategories": {
                    "Freshwater": ["Tilapia", "Catfish"],
                    "Processed": ["Smoked Tilapia", "Fish Fillets"],
                },
            },
            {
                "name": "Grains & Legumes",
                "description": "Cereals, pulses, and legumes.",
                "subcategories": {
                    "Grains": ["Maize", "Rice", "Sorghum"],
                    "Legumes": ["Beans", "Lentils", "Green Grams"],
                },
            },
            {
                "name": "Fertilizers",
                "description": "Organic and inorganic fertilizers.",
                "subcategories": {
                    "Organic": ["Compost", "Manure"],
                    "Inorganic": ["DAP Fertilizer", "Urea Fertilizer"],
                },
            },
            {
                "name": "Herbs & Spices",
                "description": "Fresh and dried herbs and spices.",
                "subcategories": {
                    "Herbs": ["Coriander", "Mint", "Basil"],
                    "Spices": ["Ginger", "Garlic", "Turmeric"],
                },
            },
            {
                "name": "Flowers & Ornamentals",
                "description": "Cut flowers and decorative plants.",
                "subcategories": {
                    "Cut Flowers": ["Roses", "Lilies"],
                    "Potted Plants": ["Ornamental Palm", "Succulents"],
                },
            },
            {
                "name": "Processed Foods",
                "description": "Value-added farm products.",
                "subcategories": {
                    "Packaged": ["Groundnut Paste", "Honey", "Sunflower Oil"],
                    "Baked": ["Banana Bread", "Sweet Potato Chips"],
                },
            },
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={
                    "slug": slugify(cat_data["name"]),
                    "description": cat_data["description"],
                },
            )

            for subcat_name, products in cat_data["subcategories"].items():
                subcategory, _ = SubCategory.objects.get_or_create(
                    category=category,
                    name=subcat_name,
                    defaults={"slug": slugify(subcat_name)},
                )

                for product_name in products:
                    Product.objects.get_or_create(
                        name=product_name,
                        farmer=farmer,
                        category=category,
                        subcategory=subcategory,
                        defaults={
                            "slug": slugify(f"{product_name}-{farmer.farm_name}"),
                            "sku": f"FARM-{uuid.uuid4().hex[:8].upper()}",
                            "description": f"Fresh {product_name} sourced from {farmer.farm_name}.",
                            "short_description": f"Premium quality {product_name} from local farmers.",
                            "price": Decimal(random.randint(50, 500)),
                            "available_quantity": Decimal(random.randint(10, 200)),
                            "unit": "kg",
                            "quality_grade": random.choice(["premium", "grade_a", "organic"]),
                            "harvest_date": date.today() - timedelta(days=random.randint(1, 7)),
                            "expiry_date": date.today() + timedelta(days=random.randint(3, 30)),
                            "farming_method": random.choice(["Organic", "Conventional"]),
                        },
                    )

        self.stdout.write(self.style.SUCCESS("✅ Successfully seeded categories, subcategories, and products."))
