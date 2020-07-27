from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category
from django.utils import timezone
from django.contrib.auth.models import User


# TDD

def create_category(name='life', description=''):
    category, is_created = Category.objects.get_or_create(
        name=name,
        description=description
    )
    return category


def create_post(title, content, author, category=None):
    blog_post = Post.objects.create(
        title=title,
        content=content,
        created=timezone.now(),
        author=author,
        category=category,
    )
    return blog_post



class TestModel(TestCase):
    def setUp(self):
        self.client = Client()  # client가 브라우저 역할 대신
        self.author_000 = User.objects.create(username='smith', password='no')

    def test_post(self):
        category=create_category(

        )
        post_000 = create_post(
            title='The first post',
            content='hello wolrd.',
            author=self.author_000,
            category=category,
        )

        self.assertEqual(category.post_set.count(), 1)  # Post를 post로 가져옴. category에서 post 불러옴

class Testview(TestCase):
    def setUp(self):
        self.client = Client()  # client가 브라우저 역할 대신
        self.author_000 = User.objects.create(username='smith', password='no')

    def check_navbar(self, soup):
        navbar = soup.find("div", id='navbar')
        self.assertIn("Blog", navbar.text)
        self.assertIn("About me", navbar.text)

    def test_post_list_noPost(self):
        response = self.client.get('/blog/')  # Http://~~/blog의 소스를 가져오겠다
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title  # soup = html 태그 가져옴

        self.assertEqual(title.text, 'Blog')

        self.check_navbar(soup)
        # navbar = soup.find("div", id='navbar')
        # self.assertIn("Blog", navbar.text)
        # self.assertIn("About me", navbar.text)

        self.assertEqual(Post.objects.count(), 0)
        self.assertIn("아직 게시물이 없습니다", soup.body.text)


    def test_post_list_post(self):
        post_000 = create_post(
            title='The first post',
            content='hello wolrd.',
            author=self.author_000,
        )

        post_001 = create_post(
            title='The second post',
            content='ss',
            author=self.author_000,
            category=create_category(name='정치/사회')
        )

        self.assertGreater(Post.objects.count(), 0)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        body = soup.body
        self.assertNotIn('아직 게시물이 없습니다.', body.text)
        self.assertIn(post_000.title, body.text)

        post_000_read = body.find('a', id='read-{}'.format(post_000.pk))
        self.assertEqual(post_000_read['href'], post_000.get_absolute_url())

        # category card 에서
        category_card = body.find('div', id='category_card')
        # 미분류(1),정치/사회(1) 있어야함
        self.assertIn('미분류 (1)', category_card.text)
        self.assertIn('정치/사회 (1)', category_card.text)

        # main_div 포스트에는 정치/사회
        main_div = body.find('div', id='main_div')
        self.assertIn('정치/사회', main_div.text)


    def test_post_detail(self):
        post_000 = create_post(
            title='The first post',
            content='hello wolrd.',
            author=self.author_000,
        )

        self.assertGreater(Post.objects.count(), 0)
        post_000_url = post_000.get_absolute_url()
        self.assertEqual(post_000_url, '/blog/{}/'.format(post_000.pk))

        response = self.client.get(post_000_url)  # post_000.get_absolute_url()의 소스를 가져오겠다
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title  # soup = html 태그 가져옴

        self.assertEqual(title.text, '{} - Blog'.format(post_000.title))

        self.check_navbar(soup)

        body = soup.body

        main_div = body.find('div', id='main_div')
        self.assertIn(post_000.title, main_div.text)
        self.assertIn(post_000.author.username, main_div.text)

        self.assertIn(post_000.content, main_div.text)
