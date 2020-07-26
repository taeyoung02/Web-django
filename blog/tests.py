from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post
from django.utils import timezone
from django.contrib.auth.models import User


# TDD


def create_post(title, content, author):
    blog_post = Post.objects.create(
        title=title,
        content=content,
        created=timezone.now(),
        author=author,
    )
    return blog_post

class Testview(TestCase):
    def setUp(self):
        self.client = Client()  # client가 브라우저 역할 대신
        self.author_000 = User.objects.create(username='smith', password='no')

    def check_navbar(self, soup):
        navbar = soup.find("div", id='navbar')
        self.assertIn("Blog", navbar.text)
        self.assertIn("About me", navbar.text)

    def test_post_list(self):
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

        post_000 = create_post(
            title='The first post',
            content='hello wolrd.',
            author=self.author_000,
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

        main_div = body.find('div', id = 'main_div')
        self.assertIn(post_000.title, main_div.text)
        self.assertIn(post_000.author.username, main_div.text)

        self.assertIn(post_000.content, main_div.text)