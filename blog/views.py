from django.shortcuts import render
from .models import Post, Category  # . = 지금 폴더안
# post = models.py의 post가져옴
from django.views.generic import ListView, DetailView


# 밑에거 필요없이 위에 2줄로 가능

class PostList(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.order_by('-created')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostList, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()
        # category가 none인것만 걸러서 왼쪽에 갯수 저장
        return context


class PostListbyCategory(PostList):

    def get_queryset(self):
        slug = self.kwargs['slug']
        category = Category.objects.get(slug=slug)


        return Post.objects.filter(category=category).order_by('-created')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(type(self), self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()

        slug = self.kwargs['slug']
        category = Category.objects.get(slug=slug)

        # context['title'] = 'Blog - {}'.format(category)
        return context

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostDetail, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()
        # category가 none인것만 걸러서 왼쪽에 갯수 저장
        return context

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
