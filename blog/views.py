"""Class Based Views"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.core.mail import send_mail

from .models import Post
from .forms import EmailPostForm


class PostListView(ListView):
    """Alternative post list view"""
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 1
    template_name = 'blog/post/list.html'


"""Function Based Views"""

# from django.http import Http404
# from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
# # Create your views here.
# from .models import Post


# def post_list(request):
#     post_list = Post.published.all()
#     paginatior = Paginator(post_list,1)
#     page_number = request.GET.get('page',1)
#     try:
#         posts = paginatior.page(page_number)
#     except EmptyPage:
#         posts = paginatior.page(paginatior.num_pages)
#     except PageNotAnInteger:
#         posts = paginatior.page(1)
#     return render(request, 'blog/post/list.html', {'posts': posts})


def post_detail(request, year, month, day, post):
    # try:
    # post = Post.published.get(id=id)
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED,
                             publish__year=year, publish__month=month, publish__day=day, slug=post)
    # except Post.DoesNotExist:
    # raise Http404("No Post Found.")
    return render(request, 'blog/post/detail.html', {'post': post})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommendeds you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n"\
            f"{cd['name']}\'s comments:{cd['comments']}"
            send_mail(subject,message,'hanzawnyineonline@gmail.com',[cd['to']])
            sent=True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form,'sent':sent})
