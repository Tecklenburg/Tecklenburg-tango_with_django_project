from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rango.models import Category, Page


class CategoryMethodTests(TestCase):
    def test_ensure_views_are_positive(self):
        """
        Ensures the number of views received for a Category are positive or zero
        """
        category = add_category('test', -1, 0)

        self.assertEqual((category.views >= 0), True)

    def test_slug_line_creation(self):
        """
        Checks to make sure a category is created, an appropriate slug is created
        Example "Random Category String" should be "random-category-string".
        """
        category = add_category("Random Category String")

        self.assertEqual(category.slug, 'random-category-string')


class IndexViewTests(TestCase):
    def test_index_view_with_no_categories(self):
        """
        If no categories exist, the appropriate message should be displayed.
        """
        response = self.client.get(reverse('rango:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are no categories present.')
        self.assertQuerysetEqual(response.context['categories'], [])

    def test_index_view_with_categories(self):
        """
        Checks whether categories are displayed correctly when present
        """
        add_category('Python', 1, 1)
        add_category('C++', 1, 1)
        add_category('Erlang', 1, 1)

        response = self.client.get(reverse('rango:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python")
        self.assertContains(response, "C++")
        self.assertContains(response, "Erlang")

        num_categories = len(response.context['categories'])
        self.assertEquals(num_categories, 3)


class PageMethodsTests(TestCase):
    def test_page_last_visit_not_in_the_future(self):
        category = add_category('test')
        page = add_page(category, 'test_page', 'https://google.com',
                        last_view=timezone.now() + timedelta(days=1))

        self.assertTrue(page.last_visit < timezone.now())

    def test_page_last_visit_is_updated_when_page_is_visited(self):
        category = add_category('test')
        page = add_page(category, 'test_page', 'https://google.com')
        create_time = page.last_visit

        response = self.client.get(reverse('rango:goto'), {'page_id': page.id})
        page.refresh_from_db()

        self.assertTrue(create_time < page.last_visit)


def add_page(cat, title, url, views=0, last_view=timezone.now()):
    page = Page.objects.get_or_create(category=cat, title=title)[0]
    page.url = url
    page.views = views
    page.last_visit = last_view
    page.save()
    return page


def add_category(name, views=0, likes=0):
    category = Category.objects.get_or_create(name=name)[0]
    category.views = views
    category.likes = likes

    category.save()
    return category
