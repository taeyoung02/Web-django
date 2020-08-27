from django.urls import path, include
from . import views


urlpatterns = [
    path('search/<str:q>/', views.PostSearch.as_view()),
    path('category/<str:slug>/', views.PostListByCategory.as_view()),
    path('<int:pk>/update/', views.PostUpdate.as_view()),
    path('<int:pk>/', views.PostDetail.as_view()),
    path('upload/', views.upload_file),
    path('', views.PostList.as_view()),
]