from django import template
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property

from miaiqi_cards.postcards import models

register = template.Library()


class NavigationMixin:
    @cached_property
    def sets(self):
        slug = self.params.get('sets_slug')
        return get_object_or_404(models.SetsSection.objects.all(), slug=slug)

    @cached_property
    def gallery(self):
        slug = self.params.get('gallery_slug')
        return get_object_or_404(models.GallerySection.objects.all(), slug=slug)

    @cached_property
    def postcard(self):
        id = self.params.get('postcard_id')
        return get_object_or_404(self.gallery.postcards.all(), id=id)

    @property
    def index(self):
        return [i.id for i in self.items].index(self.item.id)

    @property
    def previous(self):
        return [None, *self.items, None][self.index]

    @property
    def next(self):
        return [None, *self.items, None][self.index + 2]

    @property
    def previous_url(self):
        return self.get_url(self.previous)

    @property
    def next_url(self):
        return self.get_url(self.next)

    def get_url(self, item):
        if item:
            kwargs = self.params.copy()
            kwargs[self.item_key] = getattr(item, 'slug', None) or getattr(item, 'id')
            return reverse(self.url_name, kwargs=kwargs)
        else:
            return None


class PostcardNavigation(NavigationMixin):
    def __init__(self, params):
        self.params = params
        self.item = self.postcard
        self.items = self.gallery.postcards.all()
        self.item_key = 'postcard_id'
        self.url_name = 'postcard'

    @property
    def back_url(self):
        return f"{reverse('page')}#{self.gallery.slug}"


class SetPostcardNavigation(PostcardNavigation):
    def __init__(self, params):
        super().__init__(params)
        self.url_name = 'set_postcard'

    @property
    def back_url(self):
        kwargs = self.params
        del kwargs['postcard_id']
        return reverse('gallery', kwargs=kwargs)


class GalleryNavigation(NavigationMixin):
    def __init__(self, params):
        self.params = params
        self.item = self.gallery
        self.items = self.sets.postcard_sets.all()
        self.item_key = 'gallery_slug'
        self.url_name = 'gallery'

    @property
    def back_url(self):
        return f"{reverse('page')}#{self.sets.slug}"


@register.inclusion_tag('postcards/navigation.html')
def navigation(url_params):
    if 'sets_slug' in url_params and 'postcard_id' in url_params:
        navigation = SetPostcardNavigation(url_params)
    elif 'sets_slug' in url_params:
        navigation = GalleryNavigation(url_params)
    else:
        navigation = PostcardNavigation(url_params)
    return dict(navigation=navigation)


@register.simple_tag
def postcard_url(section, postcard, url_params):
    if url_params:
        kwargs = url_params.copy()
        kwargs['postcard_id'] = postcard.id
        return reverse('set_postcard', kwargs=kwargs)
    else:
        kwargs = dict(gallery_slug=section.slug, postcard_id=postcard.id)
        return reverse('postcard', kwargs=kwargs)
