from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post, User, Comment
from posts.tests.constants import (
    EXAMPLE_SLUG,
    EXAMPLE_USERNAME,
    EXAMPLE_TEXT,
    EXAMPLE_TITLE,
    EXAMPLE_DESCRIPTION,
    INDEX_URL,
    GROUP_LIST_URL,
    PROFILE_URL,
    POST_DETAIL_URL,
    POST_EDIT_URL,
    POST_CREATE_URL,
    ADD_COMMENT_URL,
    FOLLOW_INDEX_URL,
    PROFILE_FOLLOW,
    PROFILE_UNFOLLOW,
)


class TestsUrls(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username=EXAMPLE_USERNAME,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=EXAMPLE_TEXT,
        )
        cls.group = Group.objects.create(
            title=EXAMPLE_TITLE,
            slug=EXAMPLE_SLUG,
            description=EXAMPLE_DESCRIPTION,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text=EXAMPLE_TEXT,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls(self):
        urls = {
            reverse(INDEX_URL): HTTPStatus.OK,
            reverse(GROUP_LIST_URL,
                    kwargs={'slug': EXAMPLE_SLUG}): HTTPStatus.OK,
            reverse(PROFILE_URL,
                    kwargs={'username': EXAMPLE_USERNAME}): HTTPStatus.OK,
            reverse(POST_DETAIL_URL,
                    kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse(POST_EDIT_URL,
                    kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse(POST_CREATE_URL): HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
            reverse(ADD_COMMENT_URL,
                    kwargs={'post_id': self.post.id}): HTTPStatus.FOUND,
            reverse(FOLLOW_INDEX_URL): HTTPStatus.OK,
            reverse(PROFILE_FOLLOW,
                    kwargs={'username': EXAMPLE_USERNAME}): HTTPStatus.FOUND,
            reverse(PROFILE_UNFOLLOW,
                    kwargs={'username': EXAMPLE_USERNAME}): HTTPStatus.FOUND,
        }
        for url, status_code in urls.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)
