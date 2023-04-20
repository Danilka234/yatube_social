from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from ..models import Post, Group
from http import HTTPStatus
from django.core.cache import cache


User = get_user_model()


class PostsURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cache.clear()
        cls.author_user = User.objects.create_user(username="author_u")
        cls.another_user = User.objects.create_user(username="another_u")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Текстовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.author_user,
            text="Тестовый пост",
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.another_user)
        self.author_client = Client()
        self.author_client.force_login(self.author_user)

    def test_urls_for_guest_client(self):
        """Проверка неавторизованного пользователя."""
        page_url_names = {
            "/": HTTPStatus.OK,
            f"/group/{self.group.slug}/": HTTPStatus.OK,
            f"/profile/{self.author_user}/": HTTPStatus.OK,
            f"/posts/{self.post.id}/": HTTPStatus.OK,
            "unexisting_page/": HTTPStatus.NOT_FOUND,
        }
        for url, status_code in page_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_for_authorized_client(self):
        """Проверка авторизованного пользователя."""
        page_url_names = {
            "/": HTTPStatus.OK,
            f"/group/{self.group.slug}/": HTTPStatus.OK,
            f"/profile/{self.author_user}/": HTTPStatus.OK,
            f"/posts/{self.post.id}/": HTTPStatus.OK,
            f"/posts/{self.post.id}/edit/": HTTPStatus.FOUND,
            "/create/": HTTPStatus.OK,
            "unexisting_page/": HTTPStatus.NOT_FOUND,
        }
        for url, status_code in page_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_for_author_client(self):
        """Проверка автора поста."""
        page_url_names = {
            "/": HTTPStatus.OK,
            f"/group/{self.group.slug}/": HTTPStatus.OK,
            f"/profile/{self.author_user}/": HTTPStatus.OK,
            f"/posts/{self.post.id}/": HTTPStatus.OK,
            f"/posts/{self.post.id}/edit/": HTTPStatus.OK,
            "/create/": HTTPStatus.OK,
            "unexisting_page/": HTTPStatus.NOT_FOUND,
        }
        for url, status_code in page_url_names.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_uses_correct_template(self):
        """Тестирование URL адресов и шаблонов"""
        templates_url_names = {
            "/": "posts/index.html",
            f"/group/{self.group.slug}/": "posts/group_list.html",
            f"/profile/{self.author_user}/": "posts/profile.html",
            f"/posts/{self.post.id}/": "posts/post_detail.html",
            f"/posts/{self.post.id}/edit/": "posts/post_create.html",
            "/create/": "posts/post_create.html",
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_redirect_anonymous_on_admin_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get("/create/", follow=True)
        self.assertRedirects(
            response, "/auth/login/?next=%2Fcreate%2F"
        )
