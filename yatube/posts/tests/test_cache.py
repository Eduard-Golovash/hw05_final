from time import sleep

from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, User

from posts.tests.constants import (
    EXAMPLE_USERNAME,
    EXAMPLE_TEXT,
    INDEX_URL
)


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=EXAMPLE_USERNAME)
        cls.post = Post.objects.create(
            author=cls.user,
            text=EXAMPLE_TEXT,)
        cls.cache_key = 'index_page'

    def setUp(self):
        self.client = Client()

    def test_cache_save(self):
        """Кэш коррекно сохраняет данные."""
        self.assertIsNone(cache.delete(self.cache_key))
        response = self.client.get(reverse(INDEX_URL))
        self.assertContains(response, self.post.text)
        self.assertIsNone(cache.get(self.cache_key))

    def test_cache_update(self):
        """Кэш обновляется каждые 20 секунд."""
        self.assertIsNone(cache.delete(self.cache_key))
        response = self.client.get(reverse(INDEX_URL))
        self.assertContains(response, self.post.text)
        sleep(20)
        response2 = self.client.get(reverse(INDEX_URL))
        self.assertContains(response2, self.post.text)
        self.assertEqual(response.content, response2.content)
