import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _


class VendorProfile(models.Model):
    user = models.OneToOneField(
        "accounts.User", on_delete=models.CASCADE, related_name="v_data"
    )
    vendor_id = models.CharField("Order ID", max_length=255, default=str(uuid.uuid4()))
    business_name = models.CharField("Business Name", max_length=255)
    opening_time = models.IntegerField("Opening Time", default=8)
    closing_time = models.IntegerField("Closing Time", default=6)
    price_per_kg = models.IntegerField("Price Per Kg", default=6)

    is_taking_orders = models.BooleanField(default=True)


# choice class
class OrderStatusChoices(models.IntegerChoices):
    PENDDING = 2
    DELIVERED = 0
    CANCELLED = 1


# choice class


class Order(models.Model):
    OrderStatusChoices = [
        (0, "DELIVERED"),
        (1, "CANCELLED"),
        (2, "PENDING"),
    ]
    customer = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="orders"
    )
    vendor = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="vendor_orders",
        null=True,
    )
    order_id = models.CharField("Order ID", max_length=255, default=str(uuid.uuid4()))
    amount = models.IntegerField("Amount")
    pickup_address = models.CharField("Pickup Address", max_length=255)
    dropoff_address = models.CharField("DropOff Address", max_length=255)
    order_status = models.CharField(
        "Order Status", max_length=255, choices=OrderStatusChoices
    )
    package_size_in_kg = models.CharField("Size of Package in Kg", max_length=255)
    description = models.TextField("Order Description")
    date_created = models.DateTimeField(auto_now_add=True)
    date_delivered = models.DateTimeField(null=True)

    is_delivered = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_accepted = models.BooleanField(default=False)


class Reviews(models.Model):
    Ratings = [
        (1, "ABYSMAL"),
        (2, "POOR"),
        (3, "AVERAGE"),
        (4, "GOOD"),
        (5, "EXCELLENT"),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="review")
    review_id = models.CharField("Review ID", max_length=255, default=str(uuid.uuid4()))
    ratings = models.CharField("Ratings", max_length=255, choices=Ratings)


class Comments(models.Model):
    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="comments"
    )
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    text = models.TextField("Text")
    review = models.ForeignKey(
        Reviews, on_delete=models.CASCADE, related_name="comments"
    )
