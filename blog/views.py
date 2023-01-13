"""Class Based Views"""
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.core.mail import send_mail
from django.views.decorators.http import require_POST

from .models import Post, Comment
from taggit.models import Tag
from .forms import EmailPostForm, CommentForm, SearchForm
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

# class PostListView(ListView):
#     """Alternative post list view"""
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'


"""Function Based Views"""

# from django.http import Http404
# # Create your views here.
# from .models import Post


def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    paginatior = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginatior.page(page_number)
    except EmptyPage:
        posts = paginatior.page(paginatior.num_pages)
    except PageNotAnInteger:
        posts = paginatior.page(1)
    return render(request, 'blog/post/list.html', {'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, post):
    # try:
    # post = Post.published.get(id=id)
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED,
                             publish__year=year, publish__month=month, publish__day=day, slug=post)
    # except Post.DoesNotExist:
    # raise Http404("No Post Found.")
    comments = post.comments.filter(active=True)

    post_tag_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(
        tags__in=post_tag_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count(
        'tags')).order_by('-same_tags', '-publish')[:4]

    form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'form': form, 'similar_posts': similar_posts})


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
            send_mail(subject, message,
                      'hanzawnyineonline@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            # results = Post.published.annotate(
            # search=SearchVector('title', 'body')).filter(search=query)

            # Stemming and ranking results
            # search_vector = SearchVector('title','body')
            # search_query = SearchQuery(query)
            # results = Post.published.annotate(
            #     search=search_vector,rank=SearchRank(search_vector,search_query)).filter(search=search_query).order_by('-rank')

            # Stemming and removing stop words in different languages
            # search_vector = SearchVector('title','body',config="spanish")
            # search_query = SearchQuery(query,config='spanish')
            # results = Post.published.annotate(
            #     search=search_vector,rank=SearchRank(search_vector,search_query)).filter(search=search_query).order_by('-rank')

            # Weighting queries
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.published.annotate(search=search_vector, rank=SearchRank(
                search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank')

    return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results})
