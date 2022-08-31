from django.test import TestCase
from accounts.helpers.utils import create_user

mock_data = {
    "email": "uche@gmail.com",
    "phone_number": "08117402659",
    "address": "Lagos, Nigeria",
    "state": "Lagos",
    "country": "Nigeria",
    "password": "#LifeisGr8t",
}


class TestModels(TestCase):
    def setUp(self) -> None:
        self.user = create_user(
            mock_data["email"],
            mock_data["phone_number"],
            mock_data["address"],
            mock_data["state"],
            mock_data["country"],
            mock_data["password"],
        )
        return super().setUp()

    def test_user_creation(self):
        assert self.assertIsNotNone(self.user)

    def test_api_key_was_created(self):
        assert self.assertIsNotNone(user.user_data.api_key)

    def tearDown(self) -> None:
        return super().tearDown()
