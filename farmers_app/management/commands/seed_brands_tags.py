# famers_website/management/commands/seed_brands_tags.py

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from farmers_website.models import Brand, Tag

class Command(BaseCommand):
    help = "Seed the database with real agricultural brands and useful product tags"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("🌱 Starting to seed brands and tags..."))

        # ✅ Real agricultural brands in Kenya
        brands = [
            {
                "name": "Yara Kenya",
                "description": "Leading supplier of crop nutrition solutions and fertilizers in Kenya.",
                "website": "https://www.yara.co.ke/",
            },
            {
                "name": "Twiga Chemicals",
                "description": "Supplier of agrochemicals, fertilizers, and seeds for Kenyan farmers.",
                "website": "https://twigachemicals.com/",
            },
            {
                "name": "BASF East Africa",
                "description": "Global chemical company offering crop protection and seed solutions.",
                "website": "https://www.agriculture.basf.com/",
            },
            {
                "name": "Syngenta Kenya",
                "description": "Provider of crop protection products and high-quality seeds.",
                "website": "https://www.syngenta.co.ke/",
            },
            {
                "name": "Osho Chemical Industries Ltd",
                "description": "Manufacturer and distributor of agrochemicals and farm inputs in East Africa.",
                "website": "https://oshochem.com/",
            },
            {
                "name": "Elgon Kenya Ltd",
                "description": "Supplier of fertilizers, seeds, greenhouses, and irrigation equipment.",
                "website": "https://elgonkenya.com/",
            },
            {
                "name": "Bayer Crop Science Kenya",
                "description": "Global leader in crop protection and seed solutions for Kenyan farmers.",
                "website": "https://www.cropscience.bayer.co.ke/",
            },
            {
                "name": "Amiran Kenya",
                "description": "Supplier of greenhouses, irrigation kits, and farm inputs for modern farming.",
                "website": "https://amirankenya.com/",
            }
        ]

        created_brands = 0
        for brand_data in brands:
            brand, created = Brand.objects.get_or_create(
                name=brand_data["name"],
                defaults={
                    "slug": slugify(brand_data["name"]),
                    "description": brand_data["description"],
                    "website": brand_data["website"],
                    "is_active": True
                }
            )
            if created:
                created_brands += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Created brand: {brand.name}"))
            else:
                self.stdout.write(f"ℹ️ Brand already exists: {brand.name}")

        # ✅ Useful e-commerce tags
        tags = [
            {"name": "New", "color": "#28a745"},
            {"name": "Featured", "color": "#ffc107"},
            {"name": "Organic", "color": "#20c997"},
            {"name": "Bestseller", "color": "#17a2b8"},
            {"name": "Limited Stock", "color": "#dc3545"},
            {"name": "Discount", "color": "#ff5733"},
            {"name": "Pre-Order", "color": "#6f42c1"},
            {"name": "Top Rated", "color": "#007bff"},
        ]

        created_tags = 0
        for tag_data in tags:
            tag, created = Tag.objects.get_or_create(
                name=tag_data["name"],
                defaults={
                    "slug": slugify(tag_data["name"]),
                    "color": tag_data["color"],
                    "is_active": True
                }
            )
            if created:
                created_tags += 1
                self.stdout.write(self.style.SUCCESS(f"🏷️ Created tag: {tag.name}"))
            else:
                self.stdout.write(f"ℹ️ Tag already exists: {tag.name}")

        self.stdout.write(self.style.SUCCESS(
            f"\n🎯 Done! Created {created_brands} new brands and {created_tags} new tags."
        ))
