import random
import string
from django.core.management.base import BaseCommand
from farmers_app.models import CustomUser, TransporterProfile, County
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = "Generate transporter profiles for all transporters without one"

    def handle(self, *args, **kwargs):
        vehicle_types = [
            'motorcycle', 'tuk_tuk', 'pickup', 'van', 'truck', 'lorry'
        ]

        transporters = CustomUser.objects.filter(user_type='transporter').exclude(transporter_profile__isnull=False)

        if not transporters.exists():
            self.stdout.write(self.style.WARNING("⚠ No transporters found without profiles."))
            return

        counties = County.objects.all()
        if not counties.exists():
            self.stdout.write(self.style.ERROR("❌ No counties found. Please run your county generation command first."))
            return

        for transporter in transporters:
            # Location
            base_county = random.choice(counties)

            # Random service counties (between 3 and 10)
            service_counties = random.sample(list(counties), k=random.randint(3, min(10, len(counties))))

            # Vehicle info
            vehicle_type = random.choice(vehicle_types)
            vehicle_registration = f"K{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)} {random.randint(100, 999)}{random.choice(string.ascii_uppercase)}"
            # Correct vehicle registration to match Kenyan format e.g., KDA 123A
            vehicle_registration = f"K{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)} {random.randint(100, 999)}{random.choice(string.ascii_uppercase)}"

            vehicle_capacity = round(random.uniform(50, 5000), 2)  # kg

            mpesa_number = f"+2547{random.randint(10000000, 99999999)}"
            driving_license = f"DL{random.randint(100000, 999999)}"
            insurance_number = f"INS{random.randint(10000, 99999)}"

            profile = TransporterProfile.objects.create(
                user=transporter,
                business_name=fake.company(),
                vehicle_type=vehicle_type,
                vehicle_registration=vehicle_registration,
                vehicle_capacity=vehicle_capacity,
                base_county=base_county,
                max_distance=random.randint(50, 500),
                rate_per_km=round(random.uniform(20, 150), 2),
                minimum_charge=round(random.uniform(200, 1000), 2),
                mpesa_number=mpesa_number,
                driving_license=driving_license,
                insurance_number=insurance_number,
                total_deliveries=random.randint(0, 1000),
                total_earnings=round(random.uniform(5000, 5000000), 2),
                rating=round(random.uniform(2.5, 5.0), 2),
                total_reviews=random.randint(0, 500),
                is_verified=random.choice([True, False]),
                is_available=random.choice([True, False]),
                is_active=True
            )

            # Add service counties (ManyToMany)
            profile.service_counties.set(service_counties)

            self.stdout.write(self.style.SUCCESS(
                f"✅ Created transporter {transporter.username} ({vehicle_type}, {vehicle_registration}) based in {base_county.name}"
            ))

        self.stdout.write(self.style.SUCCESS("🚚 All transporter profiles created successfully!"))
