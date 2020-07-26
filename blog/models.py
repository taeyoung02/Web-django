from django.db import models
from django.contrib.auth.models import User  # User 객체 제공


# Post는 모델의 이름입니다.
# models은 Post가 장고 모델임을 의미합니다. 이 코드 때문에 장고는 Post가 데이터베이스에 저장되어야 한다고 알게 됩니다.
class Post(models.Model):
    # 블로그 글 제목
    title = models.CharField(max_length=30)  # 길이제한 필요
    # 글 내용
    content = models.TextField()

    head_image = models.ImageField(upload_to='blog/%Y/%m/%d/', blank=True)
    # 언제 작성햇는데
    created = models.DateTimeField()
    # 작성자 누군데
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # 사용자가 삭제되었을때 글은 어떻게 할것이냐 (글도 같이 삭제)

    # 제목 설정
    def __str__(self):
        return '{} :: {}'.format(self.title, self.author)

    def get_absolute_url(self):
        return '/blog/{}/'.format(self.pk)