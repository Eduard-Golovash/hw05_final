from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from .utils import paginate


@cache_page(60 * 20, key_prefix='index_page')
def index(request):
    posts = Post.objects.select_related('author', 'group').all()
    page_number = request.GET.get('page')
    paginator, page_obj = paginate(posts, page_number)
    context = {
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author').all()
    page_number = request.GET.get('page')
    paginator, page_obj = paginate(posts, page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author).select_related(
        'author',
        'group'
    )
    page_number = request.GET.get('page')
    paginator, page_obj = paginate(posts, page_number)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author,
        ).exists()
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post=post)
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    context = {
        'form': form
    }
    if not form.is_valid():
        return render(request, 'posts/post_create.html', context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {
        'form': form,
        'is_edit': True,
    }
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post.id)
    if not form.is_valid():
        return render(request, 'posts/post_create.html', context)
    form.save()
    return redirect('posts:post_detail', post_id=post.id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    page_number = request.GET.get('page')
    paginator, page_obj = paginate(post_list, page_number)
    context = {
        'page_obj': page_obj,
        'paginator': paginator
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user_follow = get_object_or_404(User, username=username)
    if request.user != user_follow:
        Follow.objects.get_or_create(user=request.user, author=user_follow)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    user_unfollow = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=user_unfollow).delete()
    return redirect('posts:profile', username=username)
