from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from miaiqi_cards.website.models import MiaiqiCardsPage
from miaiqi_cards.postcards.models import (
    GallerySection,
    Postcard,
    PostcardSet,
    PostcardSetPostcard,
    SetsSection,
    SetsSectionPostcardSet,
)


class PostcardSetModelTest(TestCase):
    def test_gallery_section_inherits_postcard_set(self):
        gallery = GallerySection.objects.create(
            title="Gallery",
            slug="gallery",
        )

        postcard_set = PostcardSet.objects.get(pk=gallery.pk)

        self.assertEqual(postcard_set.title, gallery.title)
        self.assertEqual(postcard_set.slug, gallery.slug)

    def test_sets_section_can_contain_non_section_postcard_set(self):
        postcard_set = PostcardSet.objects.create(
            title="Cards",
            slug="cards",
        )
        sets_section = SetsSection.objects.create(
            title="Collections",
            slug="collections",
        )
        SetsSectionPostcardSet.objects.create(
            sets_section=sets_section,
            postcard_set=postcard_set,
            index=0,
        )

        self.assertEqual(list(sets_section.postcard_sets.all()), [postcard_set])

    def test_postcard_set_membership(self):
        postcard_set = PostcardSet.objects.create(
            title="Cards",
            slug="cards",
        )
        postcard = Postcard.objects.create(title="Card")
        PostcardSetPostcard.objects.create(
            postcard_set=postcard_set,
            postcard=postcard,
            index=0,
        )

        self.assertEqual(list(postcard_set.postcards.all()), [postcard])


class PostcardSetPageTest(TestCase):
    def test_non_section_postcard_set_is_rendered(self):
        MiaiqiCardsPage.objects.create(
            title="Home",
            slug="home",
            page_type=ContentType.objects.get_for_model(MiaiqiCardsPage),
        )
        postcard_set = PostcardSet.objects.create(
            title="Cards",
            slug="cards",
        )
        sets_section = SetsSection.objects.create(
            title="Collections",
            slug="collections",
        )
        SetsSectionPostcardSet.objects.create(
            sets_section=sets_section,
            postcard_set=postcard_set,
            index=0,
        )

        response = self.client.get(
            reverse(
                'postcard_set',
                kwargs={
                    'sets_section_slug': sets_section.slug,
                    'postcard_set_slug': postcard_set.slug,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, postcard_set.title)
