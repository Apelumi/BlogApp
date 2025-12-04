from django.shortcuts import render, get_object_or_404
from django.http import Http404, request
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def post_list(request):
    post_lists = Post.published.all()
    # this displays 2 posts per page
    paginator = Paginator(post_lists, 2)
    page_number = request.GET.get('page')

    # this is to check for any errors with paginations
    try:
       posts = paginator.page(page_number)
    except PageNotAnInteger:
        # if page_number is not an integer
        posts = paginator.page(1)

    except EmptyPage:
        # If page_number is out of range get last page of result
        posts = paginator.page(paginator.num_pages)
    # print(posts)
    return render(
        request,
        'blog/post/list.html',
        {"posts": posts}
    )

def post_detail(request, year, month, day, post):

    # try:
    #     post = Post.published.get(id=id)
    # except Post.DoesNotExist:
    #     raise Http404("Post not found")

    post = get_object_or_404(
        Post,
        # this is for creating a very good seo related url
        status = Post.Status.PUBLISHED,
        slug = post,
        publish__year = year,
        publish__month = month,
        publish__day = day)
    return render(
        request,
        'blog/post/detail.html',
        {"post": post}
    )
