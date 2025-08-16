from django.core.management.base import BaseCommand
from django.utils.text import slugify
from decimal import Decimal
import uuid
from datetime import date, timedelta
import random

from farmers_website.models import Category, SubCategory, Product


class Command(BaseCommand):
    help = "Generate 10 Kenyan vegetable products with realistic details"

    def handle(self, *args, **kwargs):
        # 1️⃣ Create or get Category: Crops
        category, _ = Category.objects.get_or_create(
            name="Crops",
            defaults={"description": "All types of crops including vegetables, cereals, and fruits commonly grown in Kenya."}
        )

        # 2️⃣ Create or get SubCategory: Vegetables
        subcategory, _ = SubCategory.objects.get_or_create(
            category=category,
            name="vegetables",
            defaults={"description": "Fresh Kenyan vegetables sourced directly from smallholder farmers across the country."}
        )

        # 3️⃣ Kenyan vegetables with realistic descriptions
        vegetables_data = [
            {
                "name": "Kale (Sukuma Wiki)",
                "desc": "Locally grown sukuma wiki, a staple leafy green in Kenyan households, rich in vitamins A, C, and K. Perfect for daily meals.",
            },
            {
                "name": "Spinach",
                "desc": "Fresh green spinach leaves grown in the fertile soils of Rift Valley, ideal for steaming, sautéing, or making smoothies.",
            },
            {
                "name": "Cabbage",
                "desc": "Firm, round Kenyan cabbages with crisp leaves, grown organically without synthetic fertilizers. Great for stews and salads.",
            },
            {
                "name": "African Nightshade (Managu)",
                "desc": "Traditional Kenyan leafy vegetable with a slightly bitter taste, prized for its high iron content and medicinal properties.",
            },
            {
                "name": "Amaranth (Terere)",
                "desc": "Nutritious terere leaves, tender and sweet, cultivated by smallholder farmers in Western Kenya. Excellent source of calcium.",
            },
            {
                "name": "Cowpeas Leaves (Kunde)",
                "desc": "Young, tender kunde leaves, high in protein and perfect for traditional Kenyan vegetable stews.",
            },
            {
                "name": "Pumpkin Leaves (Seveve)",
                "desc": "Fresh pumpkin leaves, soft and tasty, commonly cooked with groundnuts or coconut milk in coastal Kenyan cuisine.",
            },
            {
                "name": "Sweet Potatoes Leaves",
                "desc": "Delicious and nutrient-packed sweet potato leaves, popular in rural Kenyan diets and great for boosting immunity.",
            },
            {
                "name": "Collard Greens",
                "desc": "Dark green collard leaves grown under natural sunlight, ideal for stir-frying or adding to soups and stews.",
            },
            {
                "name": "Arrowroot Leaves",
                "desc": "Edible arrowroot leaves rich in fiber, grown along riverbanks in Central Kenya. Best prepared boiled or steamed.",
            },
        ]

        for veg in vegetables_data:
            # Random price between 50 and 200 KES per kg
            price = Decimal(random.randint(50, 200))
            stock_quantity = random.randint(5, 50)

            # Skip if exists
            if Product.objects.filter(name=veg["name"]).exists():
                self.stdout.write(self.style.WARNING(f"{veg['name']} already exists. Skipping..."))
                continue

            # Create product
            product = Product.objects.create(
                name=veg["name"],
                slug=slugify(veg["name"]),
                sku=f"VEG-{uuid.uuid4().hex[:8].upper()}",
                description=veg["desc"],
                short_description=f"Organic {veg['name']} from Kenyan farms.",
                category=category,
                subcategory=subcategory,
                price=price,
                cost_price=price - Decimal(random.randint(5, 20)),
                stock_quantity=stock_quantity,
                unit="kg",
                weight=Decimal("1.00"),
                is_active=True,
                is_organic=True,
                origin=random.choice(["Kiambu", "Murang'a", "Nakuru", "Kericho", "Embu", "Nyeri"]),
                harvest_date=date.today() - timedelta(days=random.randint(0, 3)),
                expiry_date=date.today() + timedelta(days=7)
            )

            self.stdout.write(self.style.SUCCESS(f"Created: {product.name}"))

        self.stdout.write(self.style.SUCCESS("✅ Kenyan vegetables creation complete!"))
