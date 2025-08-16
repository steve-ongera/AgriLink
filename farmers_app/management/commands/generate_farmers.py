import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from farmers_app.models import CustomUser, FarmerProfile, County, SubCounty, Ward
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = "Generate farmer profiles for all farmers without one"

    def handle(self, *args, **kwargs):
        farm_types = [
            'crops', 'livestock', 'poultry',
            'dairy', 'mixed', 'organic', 'greenhouse'
        ]

        farmers = CustomUser.objects.filter(user_type='farmer').exclude(farmer_profile__isnull=False)

        if not farmers.exists():
            self.stdout.write(self.style.WARNING("⚠ No farmers found without profiles."))
            return

        counties = County.objects.all()
        if not counties.exists():
            self.stdout.write(self.style.ERROR("❌ No counties found. Please run `generate_locations` first."))
            return

        for farmer in farmers:
            # Random location
            county = random.choice(counties)
            subcounties = county.subcounties.all()
            subcounty = random.choice(subcounties)
            wards = subcounty.wards.all()
            ward = random.choice(wards)

            farm_type = random.choice(farm_types)
            farm_name = f"{farmer.first_name} {farm_type.capitalize()} Farm"
            farm_size = round(random.uniform(1, 50), 2)  # in acres
            mpesa_number = f"+2547{random.randint(10000000, 99999999)}"

            profile = FarmerProfile.objects.create(
                user=farmer,
                farm_name=farm_name,
                farm_size=farm_size,
                farm_type=farm_type,
                county=county,
                subcounty=subcounty,
                ward=ward,
                specific_location=fake.street_name(),
                mpesa_number=mpesa_number,
                bank_account=str(random.randint(10000000, 99999999)),
                bank_name=random.choice(["Equity Bank", "KCB", "Co-operative Bank", "Absa Bank", "Family Bank", "Stanbic Bank"]),
                description=fake.paragraph(nb_sentences=3),
                years_experience=random.randint(1, 20),
                certifications=random.choice(["Organic Certified", "GAP Certified", "None", "ISO 22000"]),
                total_sales=round(random.uniform(10000, 1000000), 2),
                rating=round(random.uniform(3.0, 5.0), 2),
                total_reviews=random.randint(0, 200),
                is_verified=random.choice([True, False]),
                is_active=True
            )

            self.stdout.write(self.style.SUCCESS(f"✅ Created profile for {farmer.username} in {ward.name}, {subcounty.name}, {county.name}"))

        self.stdout.write(self.style.SUCCESS("🎯 All farmer profiles created successfully!"))
