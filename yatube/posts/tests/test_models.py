from django.test import TestCase

from posts.models import Group, Post, User, Comment
from posts.tests.constants import (
    EXAMPLE_TITLE,
    EXAMPLE_SLUG,
    EXAMPLE_DESCRIPTION,
    EXAMPLE_TEXT
)


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title=EXAMPLE_TITLE,
            slug=EXAMPLE_SLUG,
            description=EXAMPLE_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=EXAMPLE_TEXT)
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text=EXAMPLE_TEXT,
        )

    def test_model_post_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        expected_object_text = self.post.text[:15]
        self.assertEqual(expected_object_text, str(self.post))

    def test_model_group_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        expected_object_title = self.group.title
        self.assertEqual(expected_object_title, str(self.group))

    def test_model_comment_have_correct_object_names(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        expected_object_text = self.comment.text[:15]
        self.assertEqual(expected_object_text, str(self.comment))
