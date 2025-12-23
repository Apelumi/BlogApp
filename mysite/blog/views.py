from django.shortcuts import render, get_object_or_404
from django.http import Http404, request
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentModelForm, SeachForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = 3
    template_name = "blog/post/list.html"


def post_list(request, tag_slug = None):
    post_lists = Post.published.all()

    tag = None
    # tag_slug = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug = tag_slug)
        post_lists = post_lists.filter(tags__in = [tag])
        # post_lists = post_lists.filter(tags=tag).distinct() # this is also go

    # this displays 2 posts per page
    paginator = Paginator(post_lists, 3)
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
        {"posts": posts,
         "tag": tag}
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
        publish__day = day
    )
    # this is to list the current active comments for this post
    comments = post.comments.filter(active = True)

    # form for users to comment
    form = CommentModelForm()

    #retreiving similar posts with the tag
    post_tags_ids = post.tags.values_list("id", flat=True)
    similar_posts = Post.published.filter(tags__in = post_tags_ids).exclude(id = post.id)
    similar_posts = similar_posts.annotate(
        same_tags = Count("tags")
    ).order_by("-same_tags", "-publish")[:4]
    return render(
        request,
        'blog/post/detail.html',
        {"post": post,
         "comments": comments,
         "form": form,
         "similar_posts": similar_posts}
    )

# form rendering and form validation
def post_share(request, post_id):
    post = get_object_or_404(
        Post,
        id = post_id,
        status = Post.Status.PUBLISHED
    )
    sent = False
    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cleanData = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = (
                f"{cleanData['name']} ({cleanData['email']})"
                f"recommends you to read {post.title}"
            )
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cleanData['name']}\'s comments: {cleanData['comments']}"
            )
            send_mail(
                subject=subject,
                message= message,
                from_email= None,
                fail_silently= False,
                recipient_list=[cleanData['to']]
            )
            sent = True
    else:
        form = EmailPostForm()

    return render(
        request,
        "blog/post/share.html",
        {"post": post,
         "form": form,
         "sent": sent}
    )

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id = post_id,
        status = Post.Status.PUBLISHED
    )
    comment = None
    form = CommentModelForm(data = request.POST)
    if form.is_valid():
        #create comment without saving to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # save the comment to the database
        comment.save()

    return render(
        request,
        "blog/post/comment.html",
        {"post": post,
         "forms": form,
         "comment": comment}
    )

def post_search(request):
    form = SeachForm
    query = None
    results = []
    if 'query' in request.GET:
        form = SeachForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]
            results = (
                Post.published.annotate(
                    search = SearchVector('title', 'body'),
                ).filter(search = query)
            )
    return render(
        request,
        'blog/post/search.html',
        {
            "results": results,
            "form": form,
            "query": query
        }
    )
