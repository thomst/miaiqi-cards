from django.template import Context, Template
from django.test import TestCase
from miaiqi_cards.website.models import TextSection
from .models import WelcomeSection


class MenuTagTests(TestCase):
    def setUp(self):
        self.welcome = WelcomeSection.objects.create(title='Welcome', subtitle='Subtitle')
        self.about = TextSection.objects.create(title='About us')
        self.news = TextSection.objects.create(title='News')
        self.welcome.title_nav.add(self.about)
        self.welcome.subtitle_nav.add(self.news)

    def render(self, source):
        template = Template('{% load menu %}' + source)
        return template.render(Context({'section': self.welcome}))

    def test_menu_of_a_single_nav_links_to_the_sections(self):
        html = self.render("{% menu section 'title_nav' %}")

        self.assertIn('class="title_nav" href="#about-us"', html)
        self.assertNotIn('News', html)

    def test_menu_without_nav_contains_all_navs(self):
        html = self.render('{% menu section %}')

        self.assertIn('class="title_nav" href="#about-us"', html)
        self.assertIn('class="subtitle_nav" href="#news"', html)
        self.assertLess(html.index('About us'), html.index('News'))
