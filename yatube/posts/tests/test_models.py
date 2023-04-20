from django.test import TestCase
from ..models import Post, Group
from django.contrib.auth import get_user_model


User = get_user_model()


class PostModelTest(TestCase):
    """Тестирование модели Post."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Test_slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост. " * 20,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        object_title_group = group.title
        self.assertEqual(object_title_group, str(group))
        post = PostModelTest.post
        object_text_post = post.text[:15]
        self.assertEqual(object_text_post, str(post)[:15])

    def test_verbose_name(self):
        """Проверка verbose_name в полях, что совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            "text": "Текст",
            "pub_date": "Дата публикации",
            "author": "Автор",
            "group": "Группа",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_test(self):
        """Проверка help_text в полях, что совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_text = {
            "text": "Введите текст поста",
            "group": "Группа, к которой будет относиться пост",
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )
