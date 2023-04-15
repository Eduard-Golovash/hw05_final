import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User
from posts.tests.constants import (
    EXAMPLE_SLUG,
    EXAMPLE_USERNAME,
    EXAMPLE_TITLE,
    EXAMPLE_DESCRIPTION,
    EXAMPLE_TEXT,
    INDEX_URL,
    GROUP_LIST_URL,
    PROFILE_URL,
    POST_DETAIL_URL,
    POST_EDIT_URL,
    POST_CREATE_URL,
    INDEX_TEMPLATE,
    GROUP_LIST_TEMPLATE,
    PROFILE_TEMPLATE,
    POST_DETAIL_TEMPLATE,
    POST_CREATE_TEMPLATE,
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestsViews(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
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
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse(INDEX_URL): INDEX_TEMPLATE,
            reverse(GROUP_LIST_URL,
                    kwargs={'slug': EXAMPLE_SLUG}): GROUP_LIST_TEMPLATE,
            reverse(PROFILE_URL,
                    kwargs={'username': EXAMPLE_USERNAME}): PROFILE_TEMPLATE,
            reverse(POST_DETAIL_URL,
                    kwargs={'post_id': self.post.id}): POST_DETAIL_TEMPLATE,
            reverse(POST_EDIT_URL,
                    kwargs={'post_id': self.post.id}): POST_CREATE_TEMPLATE,
            reverse(POST_CREATE_URL): POST_CREATE_TEMPLATE,
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_index(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(INDEX_URL))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.text, EXAMPLE_TEXT)
        self.assertTrue(first_object.image, self.uploaded)

    def test_context_group(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(GROUP_LIST_URL, kwargs={'slug': EXAMPLE_SLUG}))
        self.assertEqual(response.context['group'].title, EXAMPLE_TITLE)
        self.assertEqual(
            response.context['group'].description, EXAMPLE_DESCRIPTION)
        self.assertTrue(
            response.context['page_obj'].object_list[0].image, self.uploaded)

    def test_context_profile(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(PROFILE_URL, kwargs={'username': EXAMPLE_USERNAME}))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.text, EXAMPLE_TEXT)
        self.assertTrue(first_object.image, self.uploaded)

    def test_context_detail(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            POST_DETAIL_URL, kwargs={'post_id': self.post.id}))
        post = response.context['post']
        self.assertEqual(post, self.post)
        self.assertTrue(post, self.uploaded)

    def test_context_create(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(POST_CREATE_URL))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        form_data = {
            'text': 'Отредактированный пост',
            'group': self.group.id,
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_context_create_form(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(POST_CREATE_URL))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_additional_verification(self):
        post_data = {
            'text': EXAMPLE_TEXT,
            'group': self.group.id,
        }
        self.authorized_client.post(reverse(
            POST_CREATE_URL), data=post_data, follow=True)
        responce = self.authorized_client.get(reverse(INDEX_URL))
        self.assertContains(responce, post_data['text'])
        responce = self.authorized_client.get(
            reverse(GROUP_LIST_URL, kwargs={'slug': EXAMPLE_SLUG}))
        self.assertContains(responce, post_data['text'])
        responce = self.authorized_client.get(
            reverse(PROFILE_URL, kwargs={'username': EXAMPLE_USERNAME}))
        self.assertContains(responce, post_data['text'])
        new_group = Group.objects.create(
            title='Новая группа',
            slug='new-slug',
            description=EXAMPLE_DESCRIPTION,
        )
        responce = self.authorized_client.get(reverse(
            GROUP_LIST_URL, kwargs={'slug': new_group.slug}))
        self.assertNotContains(responce, post_data['text'])


class TestPaginator(TestCase):

    paginator_urls = [
        (reverse(INDEX_URL), [(1, 10), (2, 4)]),
        (reverse(GROUP_LIST_URL, kwargs={'slug': EXAMPLE_SLUG}), [(1, 10)]),
        (reverse(PROFILE_URL,
                 kwargs={'username': EXAMPLE_USERNAME}), [(1, 10)]),
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username=EXAMPLE_USERNAME,
        )
        cls.group = Group.objects.create(
            title=EXAMPLE_TITLE,
            slug=EXAMPLE_SLUG,
            description=EXAMPLE_DESCRIPTION,
        )
        posts = []
        for i in range(1, 15):
            posts.append(Post(
                author=cls.user, text=EXAMPLE_TEXT, group=cls.group))
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator(self):
        for url, page_counts in self.paginator_urls:
            for page, post_count in page_counts:
                with self.subTest(url=url, page=page):
                    response = self.authorized_client.get(
                        f'{url}?page={page}')
                    self.assertEqual(len(
                        response.context.get('page_obj')), post_count)
