import random
from django.core.management.base import BaseCommand
from farmers_app.models import CustomUser, BuyerProfile, County, SubCounty, Ward
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = "Generate buyer profiles for all buyers without one"

    def handle(self, *args, **kwargs):
        buyer_types = [
            'individual', 'restaurant', 'retailer',
            'processor', 'exporter', 'institution'
        ]

        buyers = CustomUser.objects.filter(user_type='buyer').exclude(buyer_profile__isnull=False)

        if not buyers.exists():
            self.stdout.write(self.style.WARNING("⚠ No buyers found without profiles."))
            return

        counties = County.objects.all()
        if not counties.exists():
            self.stdout.write(self.style.ERROR("❌ No counties found. Please run your county generation command first."))
            return

        for buyer in buyers:
            # Random location
            county = random.choice(counties)
            subcounty = random.choice(county.subcounties.all())
            ward = random.choice(subcounty.wards.all())

            buyer_type = random.choice(buyer_types)
            business_name = ""
            if buyer_type != "individual":
                business_name = fake.company()

            mpesa_number = f"+2547{random.randint(10000000, 99999999)}"
            alternative_phone = f"+2547{random.randint(10000000, 99999999)}"
            preferred_products = ", ".join(fake.words(nb=random.randint(3, 6)))

            profile = BuyerProfile.objects.create(
                user=buyer,
                buyer_type=buyer_type,
                business_name=business_name,
                county=county,
                subcounty=subcounty,
                ward=ward,
                delivery_address=fake.street_address(),
                mpesa_number=mpesa_number,
                alternative_phone=alternative_phone,
                preferred_products=preferred_products,
                max_delivery_distance=random.randint(10, 200),
                total_orders=random.randint(0, 500),
                total_spent=round(random.uniform(1000, 2000000), 2),
                is_active=True
            )

            self.stdout.write(self.style.SUCCESS(f"✅ Created profile for {buyer.username} ({buyer_type}) in {ward.name}, {subcounty.name}, {county.name}"))

        self.stdout.write(self.style.SUCCESS("🎯 All buyer profiles created successfully!"))
