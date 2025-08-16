import random
from django.core.management.base import BaseCommand
from farmers_website.models import Product, ProductAttribute, ProductReview

class Command(BaseCommand):
    help = "Generate realistic Product Attributes and Reviews"

    def handle(self, *args, **kwargs):
        products = list(Product.objects.all())

        if not products:
            self.stdout.write(self.style.ERROR("No products found. Please add some products first."))
            return

        # ---------- Create Product Attributes ----------
        attributes_list = [
            ("Color", ["Red", "Blue", "Green", "Yellow", "Black", "White"]),
            ("Size", ["Small", "Medium", "Large", "XL"]),
            ("Variety", ["Hybrid", "Local", "Improved"]),
            ("Material", ["Plastic", "Metal", "Wood", "Fiber"]),
            ("Weight", ["1kg", "2kg", "5kg", "10kg"]),
        ]

        for product in products:
            for name, values in attributes_list:
                if random.choice([True, False]):  
                    value = random.choice(values)
                    ProductAttribute.objects.get_or_create(
                        product=product,
                        name=name,
                        value=value
                    )

        # ---------- Realistic Data Sources ----------
        customer_names = [
            "James Mwangi", "Grace Njeri", "Peter Otieno", "Mary Wanjiku",
            "Brian Kiptoo", "Lucy Chebet", "Samuel Kariuki", "Ann Atieno",
            "David Mutua", "Rose Nyambura", "Kevin Omondi", "Esther Wairimu"
        ]

        review_titles = [
            "Very satisfied with the quality",
            "Exceeded my expectations",
            "Not worth the price",
            "Highly recommend this product",
            "Average quality, could be better",
            "Perfect for my needs",
            "Fast delivery and great service",
            "Poor packaging but good product",
        ]

        review_comments = [
            "The product was exactly as described and the quality is top-notch. Delivery was fast and communication was excellent.",
            "I was impressed by the durability and finishing of this item. Will definitely order again.",
            "The product works fine but the packaging was a bit damaged upon arrival. Still, it’s worth the price.",
            "Not very happy with the purchase. The product didn’t meet my expectations based on the description.",
            "I received my order earlier than expected. Everything was well packaged and the quality is great.",
            "This is my second time buying from this seller and they never disappoint. Highly recommended.",
            "The size and color were perfect. Exactly what I needed for my project.",
            "The item was okay, but I feel the price could be slightly lower for better value.",
        ]

        # ---------- Create Product Reviews ----------
        for product in products:
            for _ in range(random.randint(2, 6)):  # 2-6 reviews per product
                name = random.choice(customer_names)
                email = f"{name.split()[0].lower()}{random.randint(10,99)}@example.com"
                phone = f"+2547{random.randint(10,99)}{random.randint(100000,999999)}"

                ProductReview.objects.create(
                    product=product,
                    customer_name=name,
                    customer_email=email,
                    customer_phone=phone,
                    rating=random.randint(1, 5),
                    title=random.choice(review_titles),
                    comment=random.choice(review_comments),
                    is_approved=True  # Make all real reviews visible
                )

        self.stdout.write(self.style.SUCCESS("Realistic Product Attributes and Reviews generated successfully!"))
