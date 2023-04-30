import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from ..models import Post, Group, Comment
from http import HTTPStatus
from django.core.cache import cache


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestPostForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cache.clear()
        cls.user = User.objects.create(username="Danilka")
        cls.group = Group.objects.create(
            title="Тестовый заголовок",
            slug="test_slug",
            description="Текстовое описание",
        )
        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=cls.user,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        cache.clear()

    def test_create_post(self):
        """Проверка создание поста авторизованным пользователем."""
        task_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        new_post = {
            "text": "Новый текст",
            "title": "Новый загаловок",
            "image": uploaded,
        }
        # Создаем новый пост.
        response = self.authorized_user.post(
            reverse("posts:post_create"),
            data=new_post,
            follow=True
        )
        # Проверяем, что после сохранения поста пользователя отправляет на
        # страницу с самим постом.
        self.assertRedirects(
            response, reverse(
                "posts:profile",
                kwargs={"username": self.user.username})
        )
        # Проводим проверку, что создался новый пост.
        self.assertEqual(Post.objects.count(), task_count + 1)
        # Проверяем, что страница не сломалась.
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post(self):
        """Проверка редакторавние поста автором."""
        task_count = Post.objects.count()
        # Добавляем новый пост.
        new_post = {
            "text": "Обновленный текст",
        }
        # Загружаем редактированный текст в пост.
        response = self.authorized_user.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk}),
            data=new_post,
            follow=True,
        )
        # Проверяем, что после сохранения поста пользователя отправляет на
        # страницу с самим постом.
        self.assertRedirects(
            response, reverse(
                "posts:post_detail",
                kwargs={"post_id": self.post.pk}
            )
        )
        # Проводим проверку, что не создался новый пост.
        self.assertEqual(Post.objects.count(), task_count)
        # Проверяем, что пост отредактировался.
        self.assertTrue(
            Post.objects.filter(
                text="Обновленный текст",
            ).exists(),
        )
        # Проверяем, что страница не сломалась.
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Начинаем проверку поста на странице профайла пользователя.
        response_author = self.authorized_user.get(
            reverse("posts:profile", kwargs={"username": self.post.author})
        )
        last_edit_post = response_author.context["post"]
        post_text = last_edit_post.text
        self.assertEqual(post_text, "Обновленный текст")

    def test_add_comment_to_posts(self):
        """Проверка добавление комментария к посту."""
        test_comment = {
            "text": "Мне нравится этот пост."
        }
        response = self.authorized_user.post(
            reverse("posts:add_comment", kwargs={"post_id": self.post.pk}),
            data=test_comment,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                "posts:post_detail",
                kwargs={"post_id": self.post.pk}
            )
        )
        # Проверяем, что комментарий добавился.
        self.assertTrue(
            Comment.objects.filter(
                text="Мне нравится этот пост.",
            ).exists(),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
