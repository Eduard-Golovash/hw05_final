from django.test import TestCase, Client
from django.urls import reverse

from django.contrib.auth.models import User

from posts.models import Post, Follow
from django.core.cache import cache

from posts.tests.constants import (
    EXAMPLE_USERNAME,
    EXAMPLE_USERNAME_1,
    EXAMPLE_TEXT,
    EXAMPLE_TEXT_1,
)


class FollowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username=EXAMPLE_USERNAME)
        self.user1 = User.objects.create_user(username=EXAMPLE_USERNAME_1)
        self.post = Post.objects.create(
            text=EXAMPLE_TEXT,
            author=self.user,
        )
        self.post1 = Post.objects.create(
            text=EXAMPLE_TEXT_1,
            author=self.user1,
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_follow(self):
        """Пользователь может подписаться на другого пользователя"""
        response = self.authorized_client.post(reverse(
            'posts:profile_follow', args=[self.user1.username]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=self.user1).exists())

    def test_unfollow(self):
        """Пользователь может отписаться от другого пользователя"""
        Follow.objects.create(user=self.user, author=self.user1)
        response = self.authorized_client.post(reverse(
            'posts:profile_unfollow', args=[self.user1.username]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=self.user1).exists())

    def test_following(self):
        """В ленте отображаются посты тех пользователей,
        на которых подписан текущий пользователь"""
        Follow.objects.create(user=self.user, author=self.user1)
        response = self.authorized_client.get(
            reverse('posts:follow_index'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.post1.author, self.user1)
        self.assertContains(response, self.post1.text)

    def test_not_following(self):
        """В ленте не отображаются посты тех пользователей,
        на которых не подписан текущий пользователь"""
        Follow.objects.all().delete()
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.post.text)
        self.assertNotContains(response, self.post1.text)
        Follow.objects.create(user=self.user, author=self.user1)
        response = self.authorized_client.get(
            reverse('posts:follow_index'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post1.text)
