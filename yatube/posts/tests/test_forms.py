import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User, Comment
from posts.tests.constants import (
    EXAMPLE_USERNAME,
    EXAMPLE_TITLE,
    EXAMPLE_SLUG,
    EXAMPLE_DESCRIPTION,
    EXAMPLE_TEXT,
    POST_CREATE_URL,
    POST_EDIT_URL,
    POST_DETAIL_URL,
    PROFILE_URL
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username=EXAMPLE_USERNAME,
        )
        cls.group = Group.objects.create(
            title=EXAMPLE_TITLE,
            slug=EXAMPLE_SLUG,
            description=EXAMPLE_DESCRIPTION,
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=EXAMPLE_TEXT,
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_post_create(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': EXAMPLE_TEXT,
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(reverse(
            POST_CREATE_URL), data=form_data, follow=True)
        self.assertRedirects(response, reverse(
            PROFILE_URL, args=[self.user.username]))
        self.assertEqual(Post.objects.count(), posts_count)
        post = Post.objects.first()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.user)
        self.assertTrue(post.image, form_data['image'])

    def test_post_edit(self):
        post = Post.objects.create(
            text=EXAMPLE_TEXT,
            author=self.user,
        )
        post_data = {
            'text': 'Отредактированный текст'
        }
        response = self.authorized_client.post(reverse(
            POST_EDIT_URL, args=[post.id]), data=post_data)
        self.assertRedirects(response, reverse(
            POST_DETAIL_URL, args=[post.id]), status_code=302)
        edited_post = Post.objects.get(id=post.id)
        self.assertEqual(edited_post.text, post_data['text'])

    def test_comment_auth(self):
        """Комментировать пост может только авторизованный пользователь."""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=[self.post.id]),
            data=form_data, follow=True)
        self.assertRedirects(response, reverse(
            POST_DETAIL_URL, args=[self.post.id]))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
