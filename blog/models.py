from django.db import models
from django.contrib.auth.models import User # User 객체 제공
from django.db.models import OneToOneField
from markdownx.models import MarkdownxField
from markdownx.utils import markdown
from awesome_avatar.fields import AvatarField
import io

class Category(models.Model):
    name = models.CharField(max_length=25, unique=True)
    description = models.TextField(blank=True)
    # 이미 확보된 데이터로부터 유효한 URL을 만드는 방법
    slug = models.SlugField(unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '/blog/category/{}/'.format(self.slug)

    class Meta:
        verbose_name_plural = 'categories'




# Post는 모델의 이름입니다.
# models은 Post가 장고 모델임을 의미합니다. 이 코드 때문에 장고는 Post가 데이터베이스에 저장되어야 한다고 알게 됩니다


class Post(models.Model):
    # 블로그 글 제목
    title = models.CharField(max_length=30)  # 길이제한 필요
    # 글 내용
    content = MarkdownxField()

    head_image = models.ImageField(upload_to='blog/%Y/%m/%d/', blank=True)
    # 언제 작성햇는데
    created = models.DateTimeField(auto_now=True)  # 자동으로 현재시간 채움
    # 작성자 누군데
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 사용자가 삭제되었을때 글은 어떻게 할것이냐 (글도 같이 삭제)

    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-created']

    # 제목 설정
    def __str__(self):
        return '{} :: {}'.format(self.title, self.author)

    def get_absolute_url(self):
        return '/blog/{}/'.format(self.pk)

    def get_markdown_content(self):
        return markdown(self.content)

    def get_update_url(self):
        return self.get_absolute_url() + 'update/'

class Profile(models.Model):
    user = OneToOneField(User, related_name='profile', default=1, on_delete=models.CASCADE)
    avatar = AvatarField(upload_to='avatars', width=100, height=100)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)  # post하나에 여러댓글 달 수 있다
    text = MarkdownxField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_markdown_content(self):
        return markdown(self.text)

    def get_absolute_url(self):
        return self.post.get_absolute_url() + '#comment-id-{}'.format(self.pk)