from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus


User = get_user_model()


class UserTestURLS(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="authorized_user")

    def setUp(self):
        self.guest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_urls_for_not_authorizied_user(self):
        """Проверка Status code для не авторизованного пользователя."""
        urls = {
            "/auth/signup/": HTTPStatus.OK,
            "/auth/login/": HTTPStatus.OK,
            "/auth/password_change/": HTTPStatus.FOUND,
            "/auth/password_change/done/": HTTPStatus.FOUND,
            "/auth/password_reset/": HTTPStatus.OK,
            "/auth/password_reset/done/": HTTPStatus.OK,
            "/auth/reset/<uidb64>/<token>/": HTTPStatus.OK,
            "/auth/reset/done/": HTTPStatus.OK,
            "/auth/logout/": HTTPStatus.OK,
        }
        for url, status_code in urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_for_authorizied_user(self):
        """Проверка Status code для авторизованного пользователя."""
        urls = {
            "/auth/signup/": HTTPStatus.OK,
            "/auth/login/": HTTPStatus.OK,
            "/auth/password_change/": HTTPStatus.OK,
            "/auth/password_change/done/": HTTPStatus.OK,
            "/auth/password_reset/": HTTPStatus.OK,
            "/auth/password_reset/done/": HTTPStatus.OK,
            "/auth/reset/<uidb64>/<token>/": HTTPStatus.OK,
            "/auth/reset/done/": HTTPStatus.OK,
            "/auth/logout/": HTTPStatus.OK,
        }
        for url, status_code in urls.items():
            with self.subTest(url=url):
                response = self.authorized_user.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_uses_correct_template(self):
        """Тестирование URL адресов и шаблонов"""
        template_name = {
            "/auth/signup/": "users/signup.html",
            "/auth/login/": "users/login.html",
            "/auth/password_change/": "users/password_change_form.html",
            "/auth/password_change/done/": "users/password_change_done.html",
            "/auth/password_reset/": "users/password_reset_form.html",
            "/auth/password_reset/done/": "users/password_reset_done.html",
            "/auth/reset/<uidb64>/<token>/": (
                "users/password_reset_confirm.html"
            ),
            "/auth/reset/done/": "users/password_reset_complete.html",
            "/auth/logout/": "users/logged_out.html",
        }
        for url, template in template_name.items():
            with self.subTest(url=url):
                response = self.authorized_user.get(url)
                self.assertTemplateUsed(response, template)
