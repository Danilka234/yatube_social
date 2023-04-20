from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_author_page(self):
        """Проверка url страницы about на работоспособность."""
        response = self.guest_client.get("/about/author/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech_page(self):
        """Проверка url страницы tech на работоспособность."""
        response = self.guest_client.get("/about/tech/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_templates_in_about(self):
        """Проверка url и шаблонов."""
        template_urls = {
            "/about/author/": "about/author.html",
            "/about/tech/": "about/tech.html",
        }
        for url, template in template_urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_namespace_in_about_app(self):
        """Проверка namespace в приложении about."""
        namespace_and_temlates = {
            reverse("about:author"): "about/author.html",
            reverse("about:tech"): "about/tech.html",
        }
        for namespace, template in namespace_and_temlates.items():
            with self.subTest(namespace=namespace):
                response = self.guest_client.get(namespace)
                self.assertTemplateUsed(response, template)
