import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from farmers_app.models import CustomUser
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = "Generate 30 random CustomUser accounts"

    def handle(self, *args, **kwargs):
        user_types = ['farmer', 'buyer', 'transporter', 'admin']
        base_phone_prefix = "+254"

        for _ in range(30):
            username = fake.user_name()
            email = fake.email()
            phone_number = f"{base_phone_prefix}{random.randint(700000000, 799999999)}"
            user_type = random.choice(user_types)

            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password="cp7kvt",  # default password for all
                phone_number=phone_number,
                user_type=user_type,
                is_verified=random.choice([True, False]),
            )

            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created user: {username} ({user_type})"))

        self.stdout.write(self.style.SUCCESS("✅ 30 CustomUser accounts created successfully!"))
