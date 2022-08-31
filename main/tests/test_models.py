from django.test import TestCase
from main.models import Order, VendorProfile, Comments
from django.contrib.auth import get_user_model

User = get_user_model()


class TestModels(TestCase):
    def setUp(self) -> None:
        return super().setUp()
        ...

    def tearDown(self) -> None:
        return super().tearDown()
