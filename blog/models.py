from django.db import models
from django.contrib.auth.models import User  # User 객체 제공


class Post(models.Model):
    # 블로그 글 제목
    title = models.CharField(max_length=30)  # 길이제한 필요
    # 글 내용
    content = models.TextField()
    # 언제 작성햇는데
    created = models.DateTimeField()
    # 작성자 누군데
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 사용자가 삭제되었을때 글은 어떻게 할것이냐 (글도 같이 삭제)