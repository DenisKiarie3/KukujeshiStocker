from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.models import Store
from apps.inventory.models import Product, ProductVariant, StockMovement
from apps.inventory.services import record_stock_movement

User = get_user_model()


class Command(BaseCommand):
    help = (
        "DEV ONLY — creates a dev user, store, and product with stock, "
        "then prints a JWT access token for manual frontend testing. "
        "Not used in production; delete once Phase 6 login exists."
    )

    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(
            username="devowner", defaults={"email": "devowner@example.com"}
        )
        user.set_password("devpass123")
        user.save()

        store, _ = Store.objects.get_or_create(
            owner=user, slug="dev-shop", defaults={"name": "Dev Shop"}
        )

        product, _ = Product.objects.get_or_create(
            store=store, name="Sugar 2kg", defaults={"base_price": "250.00"}
        )
        variant, created = ProductVariant.objects.get_or_create(
            product=product, sku="SUGAR-2KG"
        )
        if created:
            record_stock_movement(
                variant=variant,
                movement_type=StockMovement.MovementType.PURCHASE,
                quantity_change=30,
            )

        token = RefreshToken.for_user(user)
        self.stdout.write(self.style.SUCCESS(f"Dev user ready: {user.username}"))
        self.stdout.write(self.style.SUCCESS(f"Dev store: {store.name} ({store.slug})"))
        self.stdout.write(self.style.SUCCESS(
            f"Access token (default lifetime ~5 min — rerun this command for a fresh one):\n{token.access_token}"
        ))