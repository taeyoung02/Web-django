from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from .models import Post, Category, Profile  # . = 지금 폴더안
# post = models.py의 post가져옴
from .forms import CommentForm
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
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

class AvatarChangeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']

def change_avatar(request):
    if request.method == 'POST':
        form = AvatarChangeForm(request.POST, request.FILES,
                                instance=request.user.profile)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/profile/')
    else:
        form = AvatarChangeForm(instance=request.user.profile)

    return render(request, 'template.html', {'form': form})

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
