from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='наименование')
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='слаг'
    )
    description = models.TextField(verbose_name='описание')

    def __str__(self):
        return (self.title)


class Post(models.Model):
    text = models.TextField(max_length=300, verbose_name='текст')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='дата')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='группа',
        related_name='posts'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = 'posts'

    def __str__(self) -> str:
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        max_length=300,
        verbose_name='текст комментария',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата и время',
    )

    def __str__(self) -> str:
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )
