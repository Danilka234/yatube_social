from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms

User = get_user_model()


class TestUsersForm(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_sign_up_forms(self):
        """Проверяем правильную передачу форм на страницу signup"""
        response = self.guest_client.get(
            reverse("users:signup")
        )
        fields_form_signup = {
            "first_name": forms.fields.CharField,
            "last_name": forms.fields.CharField,
            "username": forms.fields.CharField,
            "email": forms.fields.EmailField,
        }
        for field, expected in fields_form_signup.items():
            with self.subTest(field=field):
                form_field = response.context.get("form").fields[field]
                self.assertIsInstance(form_field, expected)
