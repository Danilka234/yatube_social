from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from .models import Post, Group, User, Follow
from django.core.paginator import Paginator
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required


SORT_VALUE = 10  # Количество вывода записей для сортировки.


def page_content(queryset, request):
    paginator = Paginator(queryset, SORT_VALUE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return {
        "page_obj": page_obj
    }


def index(request):
    template = ("posts/index.html")
    name = "Это главная страница проекта Yatube"
    posts = Post.objects.all()
    # Считаем количество комментариев каждого поста и
    # передаем в контекст для отображения лучшего поста.
    better_post = Post.objects.annotate(
        num_comments=Count('comments')).order_by('-num_comments').first()
    context = {
        "top_name": name,
        "posts": posts,
        "better_post": better_post
    }
    context.update(page_content(posts, request))
    return render(request, template, context)


def group_posts(request, slug):
    template = ("posts/group_list.html")
    group = get_object_or_404(Group, slug=slug)
    name = f"Записи сообщества {group}"
    posts = group.posts.all()
    context = {"top_name": name,
               "group": group,
               "posts": posts
               }
    context.update(page_content(posts, request))
    return render(request, template, context)


def profile(request, username):
    template = ("posts/profile.html")
    author = get_object_or_404(User, username=username)
    posts = author.posts.filter(author=author).all()
    name = f"Профайл пользователя {author}"
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following = False
    context = {
        "top_name": name,
        "author": author,
        "posts": posts,
        "following": following
    }
    context.update(page_content(posts, request))
    return render(request, template, context)


def post_detail(request, post_id):
    template = ("posts/post_detail.html")
    post = get_object_or_404(Post, pk=post_id)
    posts_count = Post.objects.filter(author=post.author).count()
    top_name = f"Пост {post.text[:30]}"
    comments = post.comments.all()
    form = CommentForm(
        request.GET or None
    )
    context = {
        "top_name": top_name,
        "posts_count": posts_count,
        "post": post,
        "form": form,
        "comments": comments
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = "posts/post_create.html"
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect("posts:profile", username=form.author)
    context = {
        "form": form
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = "posts/post_create.html"
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect("posts:post_detail", post_id=post.pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id=post.pk)
    context = {
        "post": post,
        "form": form,
        "is_edit": True,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    spacename = "posts:post_detail"
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(spacename, post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    context = {}
    context.update(page_content(posts, request))
    template = "posts/follow.html"
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    return_page = "posts:profile"
    author = User.objects.get(username=username)
    if_follower = Follow.objects.filter(
        user=request.user,
        author=author
    )
    if author != request.user and not if_follower.exists():
        Follow.objects.create(
            user=request.user,
            author=author
        )
    return redirect(return_page, author.username)


@login_required
def profile_unfollow(request, username):
    return_page = "posts:profile"
    author = get_object_or_404(User, username=username)
    if_follower = Follow.objects.filter(
        user=request.user,
        author=author
    )
    if if_follower.exists():
        if_follower.delete()
    return redirect(return_page, author.username)
