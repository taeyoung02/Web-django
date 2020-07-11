from django.shortcuts import render
from .models import Post  # . = 지금 폴더안
# post = models.py의 post가져옴
from django.views.generic import ListView


class PostList(ListView):
    model = Post


# 밑에거 필요없이 위에 2줄로 가능

def get_queryset(self):
    return Post.objects.order_by('-created')
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
