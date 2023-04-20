from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


class TestUsersViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="Danil")

    def setUp(self):
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_namespace_in_users_app(self):
        """Проверяем namespace и html шаблоны."""
        namespace_and_templates = {
            reverse("users:signup"): "users/signup.html",
            reverse("users:login"): "users/login.html",
            reverse("users:password_change_form"): (
                "users/password_change_form.html"
            ),
            reverse("users:password_change_done"): (
                "users/password_change_done.html"
            ),
            reverse("users:password_reset_form"): (
                "users/password_reset_form.html"
            ),
            reverse("users:password_reset_done"): (
                "users/password_reset_done.html"
            ),
            reverse("users:password_reset_complete"): (
                "users/password_reset_complete.html"
            ),
            reverse("users:logout"): "users/logged_out.html",
        }
        for namespace, template in namespace_and_templates.items():
            with self.subTest(namespace=namespace):
                response = self.authorized_user.get(namespace)
                self.assertTemplateUsed(response, template)
