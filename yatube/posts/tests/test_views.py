import tempfile
import shutil
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms
from ..models import Follow, Post, Group
from django.db.models import Count


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Очистим кеш из-за конфликта тестовых значений в бд
        # между тестами.
        cache.clear()
        cls.user = User.objects.create_user(username="authorized_user")
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
        cls.group = Group.objects.create(
            title="Тестовый заголовок",
            slug="test_slug",
            description="Текстовое описание",
        )
        cls.post = Post.objects.create(
            text="Тестовый текст",
            image=uploaded,
            author=cls.user,
            group=cls.group,
        )
        cls.better_post = Post.objects.annotate(
            num_comments=Count('comments')).order_by('-num_comments').first()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_and_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_name = {
            reverse("posts:index"): "posts/index.html",
            reverse("posts:group_list", kwargs={"slug": "test_slug"}): (
                "posts/group_list.html"),
            reverse("posts:profile",
                    kwargs={"username": self.user}): (
                "posts/profile.html"),
            reverse("posts:post_detail",
                    kwargs={"post_id": self.post.id}): (
                "posts/post_detail.html"),
            # reverse("posts:post_detail",
            #         kwargs={"better_post_id": self.better_post.id}): (
            #     "posts/post_detail.html"),
            reverse("posts:post_edit",
                    kwargs={"post_id": self.post.id}): (
                "posts/post_create.html"),
            reverse("posts:post_create"): "posts/post_create.html",
        }
        for reverse_name, template in templates_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:index"))
        test_pages = list(Post.objects.all()[:10])
        self.assertEqual(
            response.context.get("page_obj").object_list, test_pages)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug}))
        test_pages = list(Post.objects.filter(group=self.group)[:10])
        self.assertEqual(
            response.context.get("page_obj").object_list, test_pages)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={
                "username": self.post.author.username
            })
        )
        test_pages_profile = list(Post.objects.filter(author=self.user)[:10])
        self.assertEqual(
            response.context.get("page_obj").object_list, test_pages_profile)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.pk})
        )
        one_object_post = response.context["post"]
        post_author_0 = one_object_post.author.username
        post_group_0 = one_object_post.group.title
        post_text_0 = one_object_post.text
        self.assertEqual(post_author_0, "authorized_user")
        self.assertEqual(post_group_0, "Тестовый заголовок")
        self.assertEqual(post_text_0, "Тестовый текст")

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_field = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_field.items():
            with self.subTest(value=value):
                forms_field = response.context.get("form").fields[value]
                self.assertIsInstance(forms_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk})
        )
        form_field = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_field.items():
            with self.subTest(value=value):
                forms_field = response.context.get("form").fields[value]
                self.assertIsInstance(forms_field, expected)


class TestCaches(TestCase):
    # Создадим отдельный класс, что бы не конфликтовали БД.
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Danilka')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_index_page_cache(self):
        """Проверка хранения кэша на главной странице index."""
        response = self.authorized_client.get(reverse("posts:index"))
        posts = response.content
        # Для отсувствия конфликта тестовых записей, создадим еще один пост.
        Post.objects.create(
            text="Тестовый текст тестируемого кэша.",
            author=self.user,
        )
        response_for_last_post = self.authorized_client.get(
            reverse("posts:index")
        )
        last_post = response_for_last_post.content
        self.assertEqual(last_post, posts)
        cache.clear()
        response_new_post = self.authorized_client.get(
            reverse("posts:index")
        )
        new_post = response_new_post.content
        self.assertNotEqual(last_post, new_post)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="author")
        number_of_posts = 13
        cls.group = Group.objects.create(
            title="Тестовый заголовок",
            slug="test_slug",
            description="Текстовое описание",
        )
        for post_num in range(number_of_posts):
            cls.post = Post.objects.create(
                text="Тестовый текст %s" % post_num,
                author=cls.user,
                group=cls.group,
            )

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        """Проверяем правильное отображение постов на первой странице."""
        self.LENGHT_PAGE = 10
        test_pages = {
            reverse("posts:index"): self.LENGHT_PAGE,
            reverse("posts:group_list",
                    kwargs={"slug": self.group.slug}
                    ): self.LENGHT_PAGE,
            reverse("posts:profile",
                    kwargs={"username": self.post.author.username}
                    ): self.LENGHT_PAGE

        }
        for value, expected in test_pages.items():
            with self.subTest(value=value):
                response = self.guest_client.get(value)
                self.assertEqual(len(
                    response.context.get('page_obj').object_list), expected)

    def test_second_page_contains_three_records(self):
        """Проверяем правильное отображение постов на первой странице."""
        self.LENGHT_PAGE = 3
        test_pages = {
            reverse("posts:index"): self.LENGHT_PAGE,
            reverse("posts:group_list",
                    kwargs={"slug": self.group.slug}
                    ): self.LENGHT_PAGE,
            reverse("posts:profile",
                    kwargs={"username": self.post.author.username}
                    ): self.LENGHT_PAGE

        }
        for value, expected in test_pages.items():
            with self.subTest(value=value):
                response = self.guest_client.get(value + "?page=2")
                self.assertEqual(len(
                    response.context.get('page_obj').object_list), expected)


class TestFollow(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cache.clear()
        cls.author_following = User.objects.create_user(username="Danilka123")
        cls.user_follower = User.objects.create_user(username="Alex")
        cls.post = Post.objects.create(
            author=cls.author_following,
            text="Текст для проверки подписок."
        )

    def setUp(self):
        self.author_following_client = Client()
        self.author_following_client.force_login(self.author_following)
        self.user_follower_client = Client()
        self.user_follower_client.force_login(self.user_follower)

    def test_follow(self):
        # Проверяем возможность подписаться на автора.
        self.user_follower_client.get(
            reverse(
                "posts:profile_follow", kwargs={
                    "username": self.author_following.username
                }
            )
        )
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        # Проверяем возможность подписаться
        # и отписаться от автора.
        self.user_follower_client.get(
            reverse(
                "posts:profile_follow", kwargs={
                    "username": self.author_following.username
                }
            )
        )
        self.user_follower_client.get(
            reverse(
                "posts:profile_unfollow", kwargs={
                    "username": self.author_following.username
                }
            )
        )
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_follow_page(self):
        # Проверяем отображение страницы с подписками на автора.
        Follow.objects.create(
            user=self.user_follower,
            author=self.author_following
        )
        response = self.user_follower_client.get(
            reverse("posts:follow_index")
        )
        post_test_follower = response.context["page_obj"][0]
        post_text_follower = post_test_follower.text
        self.assertEqual(post_text_follower, "Текст для проверки подписок.")
