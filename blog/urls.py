from django.urls import path, include
from . import views
urlpatterns = [
    path('<int:pk>/', views.PostDetail.as_view()),  # primary key
    path('', views.PostList.as_view()),
]
