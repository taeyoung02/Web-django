from django.shortcuts import render, redirect
from .models import Post, Category# . = 지금 폴더안
# post = models.py의 post가져옴
from .forms import CommentForm
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from django.db.models import Q

class PostList(ListView):
    model = Post
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostList, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()
        # category가 none인것만 걸러서 왼쪽에 갯수 저장
        return context


class PostSearch(PostList):
    def get_queryset(self):
        q = self.kwargs['q']  # args:tuple, kwargs:dictionary
        object_list = Post.objects.filter(Q(title__contains=q) | Q(content__contains=q))
        # 제목과 내용 모두 검색
        return object_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostSearch, self).get_context_data()  # super로 PostList갖다씀
        context['search_info'] = 'Search "{}"'.format(self.kwargs['q'])  # 검색내용 보여주기위해
        return context


class PostCreate(LoginRequiredMixin, CreateView):
    model=Post
    fields = [
        'title', 'content', 'head_image', 'category'
    ]

    def form_valid(self, form):
        if self.request.user.is_authenticated():
            form.instance.author = self.request.user
            return super(type(self), self).form_valid(form)
        else:
            return redirect('/blog/')

class PostListByCategory(PostList):

    def get_queryset(self):
        slug = self.kwargs['slug']

        if slug == '_none':
            category=None
        else:
            category = Category.objects.get(slug=slug)


        return Post.objects.filter(category=category).order_by('-created')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(type(self), self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()

        slug = self.kwargs['slug']

        if slug == '_none':
            context['category'] = '미분류'
        else:
            category = Category.objects.get(slug=slug)
            context['category'] = category
        # context['title'] = 'Blog - {}'.format(category)
        return context

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostDetail, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()
        # category가 none인것만 걸러서 왼쪽에 갯수 저장
        context['Comment_form'] = CommentForm()

        return context

def new_comment(request, pk):
    post = Post.objects.get(pk=pk)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect(comment.get_absolute_url())
    else:
        return redirect('/blog/')



class PostUpdate(UpdateView):
    model = Post
    fields = [
        'title', 'content', 'head_image', 'category'
    ]

# def post_detail(request, pk):
#     blog_post = Post.objects.get(pk=pk)
#
#     return render(
#         request,
#         'blog/post_detail.html',
#         {
#             'blog_post': blog_post,
#         }
#     )

# Create your views here.

# def index(request):
#     posts = Post.objects.all()
#
#     return render(
#         request,
#         'blog/post_list.html',  # templates의 html 필요
#         {
#             'posts': posts,  # 템플릿에 전함
#         }
#     )
