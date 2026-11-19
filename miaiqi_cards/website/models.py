from django.db import models
from django.urls import reverse
from miaiqi_cards.postcards.models import GallerySection, SetsSection
from miaiqi_cards.contact.models import ContactSection
from miaiqi_cards.shop.models import ShopSection
from miaiqi_cards.welcome.models import WelcomeSection
from simple_page.models import Section, Page


class TextSection(Section):
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)

    def __str__(self):
        return self.title


class FooterSection(Section):
    name = models.CharField(max_length=100, blank=True)
    body = models.TextField(blank=True)

    def __str__(self):
        return self.name


class MiaiqiCardsPage(Page):
    REGIONS = [
        ('main', 'Main Region'),
        ('footer', 'Footer'),
    ]
    REGION_SECTIONS = {
        'main': [
            WelcomeSection,
            TextSection,
            GallerySection,
            SetsSection,
            ShopSection,
            ContactSection,
        ],
        'footer': [FooterSection],
    }
    description = models.TextField(blank=True)

    def get_section(self, section_class):
        for section in self.sections.select_subclasses():
            if isinstance(section, section_class):
                return section
        return None

    @property
    def shop_section(self):
        return self.get_section(ShopSection)

    @property
    def contact_section(self):
        return self.get_section(ContactSection)

    def get_absolute_url(self):
        return reverse('page')
