from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
# Create your views here.
from .models import Post



def post_list(request):
    post_list = Post.published.all()
    paginatior = Paginator(post_list,1)
    page_number = request.GET.get('page',1)
    try:
        posts = paginatior.page(page_number)
    except EmptyPage:
        posts = paginatior.page(paginatior.num_pages)
    except PageNotAnInteger:
        posts = paginatior.page(1)
    return render(request, 'blog/post/list.html', {'posts': posts})


def post_detail(request, year, month, day, post):
    # try:
    # post = Post.published.get(id=id)
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED,
                             publish__year=year, publish__month=month, publish__day=day, slug=post)
    # except Post.DoesNotExist:
    # raise Http404("No Post Found.")
    return render(request, 'blog/post/detail.html', {'post': post})
