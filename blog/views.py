from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Post, Profile, Comment, Tag
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm,
    ProfileForm, PostForm, CommentForm
)


# ─── Auth Views ───────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data.get('first_name', '')
            user.last_name = form.cleaned_data.get('last_name', '')
            user.save()
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome to DevLog, {user.username}!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'home')
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(next_url)
    else:
        form = CustomAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ─── Home & Feed ──────────────────────────────────────────────────────────────

def home(request):
    posts_qs = Post.objects.filter(status='published').select_related('author', 'author__profile')
    
    # Search
    query = request.GET.get('q', '')
    if query:
        posts_qs = posts_qs.filter(
            Q(title__icontains=query) |
            Q(body__icontains=query) |
            Q(author__username__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    # Tag filter
    tag_slug = request.GET.get('tag', '')
    active_tag = None
    if tag_slug:
        active_tag = get_object_or_404(Tag, slug=tag_slug)
        posts_qs = posts_qs.filter(tags=active_tag)

    paginator = Paginator(posts_qs, 9)
    page = request.GET.get('page', 1)
    posts = paginator.get_page(page)

    popular_posts = Post.objects.filter(status='published').order_by('-views')[:5]
    tags = Tag.objects.all()[:20]

    ctx = {
        'posts': posts,
        'popular_posts': popular_posts,
        'tags': tags,
        'query': query,
        'active_tag': active_tag,
    }
    return render(request, 'blog/home.html', ctx)


# ─── Post Views ───────────────────────────────────────────────────────────────

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)

    # Only increment views for published posts
    if post.status == 'published':
        # Avoid counting author's own views via session
        session_key = f'viewed_post_{post.pk}'
        if not request.session.get(session_key, False):
            post.increment_views()
            request.session[session_key] = True

    comments = post.comments.filter(is_approved=True).select_related('author', 'author__profile')
    comment_form = CommentForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'You must be logged in to comment.')
            return redirect('login')
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment posted!')
            return redirect('post_detail', slug=slug)

    related_posts = Post.objects.filter(
        status='published', tags__in=post.tags.all()
    ).exclude(pk=post.pk).distinct()[:3]

    ctx = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'related_posts': related_posts,
    }
    return render(request, 'blog/post_detail.html', ctx)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if post.status == 'published':
                post.published_at = timezone.now()
            post.save()
            # Save tags
            tags_input = form.cleaned_data.get('tags_input', '')
            if tags_input:
                from django.utils.text import slugify
                tag_names = [t.strip().lower() for t in tags_input.split(',') if t.strip()]
                for tag_name in tag_names:
                    tag, _ = Tag.objects.get_or_create(
                        slug=slugify(tag_name),
                        defaults={'name': tag_name}
                    )
                    post.tags.add(tag)
            messages.success(request, 'Post created successfully!')
            if post.status == 'published':
                return redirect('post_detail', slug=post.slug)
            return redirect('dashboard')
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form, 'action': 'Create'})


@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            updated_post = form.save(commit=False)
            if updated_post.status == 'published' and not post.published_at:
                updated_post.published_at = timezone.now()
            updated_post.save()
            # Update tags
            tags_input = form.cleaned_data.get('tags_input', '')
            updated_post.tags.clear()
            if tags_input:
                from django.utils.text import slugify
                tag_names = [t.strip().lower() for t in tags_input.split(',') if t.strip()]
                for tag_name in tag_names:
                    tag, _ = Tag.objects.get_or_create(
                        slug=slugify(tag_name),
                        defaults={'name': tag_name}
                    )
                    updated_post.tags.add(tag)
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', slug=updated_post.slug)
    else:
        existing_tags = ', '.join(post.tags.values_list('name', flat=True))
        form = PostForm(instance=post, initial={'tags_input': existing_tags})
    return render(request, 'blog/post_form.html', {'form': form, 'post': post, 'action': 'Edit'})


@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
        return redirect('dashboard')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


# ─── Profile Views ────────────────────────────────────────────────────────────

def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.user == user:
        posts = user.posts.all().order_by('-created_at')
    else:
        posts = user.posts.filter(status='published').order_by('-created_at')

    paginator = Paginator(posts, 6)
    page = request.GET.get('page', 1)
    posts_page = paginator.get_page(page)

    ctx = {
        'profile_user': user,
        'profile': profile,
        'posts': posts_page,
        'total_views': profile.total_views,
        'total_posts': profile.total_posts,
    }
    return render(request, 'blog/profile.html', ctx)


@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.email = form.cleaned_data.get('email', '')
            request.user.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'blog/profile_edit.html', {'form': form, 'profile': profile})


# ─── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    user_posts = request.user.posts.all().order_by('-created_at')
    published = user_posts.filter(status='published')
    drafts = user_posts.filter(status='draft')
    total_views = published.aggregate(total=Sum('views'))['total'] or 0
    total_comments = Comment.objects.filter(post__author=request.user).count()

    recent_comments = Comment.objects.filter(
        post__author=request.user
    ).select_related('author', 'post').order_by('-created_at')[:5]

    ctx = {
        'user_posts': user_posts[:10],
        'published_count': published.count(),
        'draft_count': drafts.count(),
        'total_views': total_views,
        'total_comments': total_comments,
        'recent_comments': recent_comments,
    }
    return render(request, 'blog/dashboard.html', ctx)


# ─── Tag View ─────────────────────────────────────────────────────────────────

def tag_posts(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts_qs = Post.objects.filter(tags=tag, status='published').select_related('author', 'author__profile')
    paginator = Paginator(posts_qs, 9)
    page = request.GET.get('page', 1)
    posts = paginator.get_page(page)
    return render(request, 'blog/tag_posts.html', {'tag': tag, 'posts': posts})


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user == comment.author or request.user == comment.post.author:
        post_slug = comment.post.slug
        comment.delete()
        messages.success(request, 'Comment deleted.')
        return redirect('post_detail', slug=post_slug)
    messages.error(request, 'Permission denied.')
    return redirect('home')
