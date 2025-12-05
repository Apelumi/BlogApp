from django.shortcuts import render, get_object_or_404
from django.http import Http404, request
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .form import EmailPostForm
from django.core.mail import send_mail

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = 3
    template_name = "blog/post/list.html"


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

# form rendering and form validation
def post_share(request, post_id):
    post = get_object_or_404(
        Post,
        id = post_id,
        status = Post.Status.PUBLISHED
    )
    sent = False
    if request.method == "POST":
        form = EmailPostForm(request.post)
        if form.is_valid():
            cleanData = form.cleaned_data
            post_url = request.build_absolute_url(
                post.get_absolute_url()
            )
            subject = (
                f"{cleanData['name']} ({cleanData['email']})"
                f"recommends you to read {post.title}"
            )
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cleanData['name']} and comments: {cleanData['comments']}"
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