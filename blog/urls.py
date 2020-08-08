from django.urls import path, include
from . import views
urlpatterns = [
path('search/<str:q>/', views.PostSearch.as_view()),
    path('<int:pk>/', views.PostDetail.as_view()),  # primary key
    path('', views.PostList.as_view()),
    path('category/<str:slug>/', views.PostListByCategory.as_view()),
    path('<int:pk>/new_comment', views.new_comment),
    path('<int:pk>/update/', views.PostUpdate.as_view()),
    path('create/', views.PostCreate.as_view())
]
