
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from farmers_website.models import Category, SubCategory

class Command(BaseCommand):
    help = "Seed the database with real agricultural data for Categories and SubCategories"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("🌱 Starting to seed real categories and subcategories..."))

        # Real agricultural categories & subcategories for a farmers e-commerce site
        data = {
            "Crops": [
                "Maize",
                "Beans",
                "Sorghum",
                "Irish Potatoes",
                "Sweet Potatoes",
                "Tomatoes",
                "Onions",
                "Cabbage",
                "Kale (Sukuma Wiki)"
            ],
            "Livestock": [
                "Dairy Cows",
                "Beef Cattle",
                "Goats",
                "Sheep",
                "Poultry (Broilers)",
                "Poultry (Layers)",
                "Pigs",
                "Rabbits",
                "Fish (Tilapia, Catfish)"
            ],
            "Fertilizers": [
                "DAP (Di-Ammonium Phosphate)",
                "CAN (Calcium Ammonium Nitrate)",
                "Urea",
                "NPK",
                "Organic Manure",
                "Compost",
                "Foliar Fertilizers"
            ],
            "Farm Equipment": [
                "Tractors",
                "Ploughs",
                "Seed Planters",
                "Water Pumps",
                "Irrigation Kits",
                "Sprayers",
                "Harrows"
            ],
            "Seeds": [
                "Hybrid Maize Seeds",
                "Open-Pollinated Maize Seeds",
                "Vegetable Seeds",
                "Fruit Tree Seedlings",
                "Legume Seeds",
                "Pasture Grass Seeds"
            ],
            "Agrochemicals": [
                "Herbicides",
                "Insecticides",
                "Fungicides",
                "Rodenticides",
                "Pesticides"
            ],
            "Animal Feeds": [
                "Dairy Meal",
                "Beef Finisher",
                "Poultry Starter Mash",
                "Poultry Growers Mash",
                "Pig Feed",
                "Goat Feed",
                "Fish Feed"
            ]
        }

        created_count = 0

        for category_name, subcategories in data.items():
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={
                    "slug": slugify(category_name),
                    "description": f"Quality {category_name.lower()} products available for farmers.",
                    "is_active": True,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Created category: {category_name}"))
            else:
                self.stdout.write(f"ℹ️ Category already exists: {category_name}")

            for sub_name in subcategories:
                subcategory, sub_created = SubCategory.objects.get_or_create(
                    category=category,
                    name=sub_name,
                    defaults={
                        "slug": slugify(sub_name),
                        "description": f"High-quality {sub_name} available under {category_name.lower()} category.",
                        "is_active": True,
                    }
                )

                if sub_created:
                    self.stdout.write(self.style.SUCCESS(f"   ➕ Created subcategory: {sub_name}"))
                else:
                    self.stdout.write(f"   ⚠️ Subcategory already exists: {sub_name}")

        self.stdout.write(self.style.SUCCESS(f"\n🎯 Done! Created {created_count} new categories."))
