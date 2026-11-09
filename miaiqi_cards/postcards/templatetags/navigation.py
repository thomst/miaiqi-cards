from django import template
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property

from miaiqi_cards.postcards import models

register = template.Library()


class NavigationMixin:
    @cached_property
    def sets_section(self):
        slug = self.params.get('sets_section_slug')
        return get_object_or_404(models.SetsSection.objects.all(), slug=slug)

    @cached_property
    def postcard_set(self):
        slug = self.params.get('set_slug')
        return get_object_or_404(models.PostcardSet.objects.all(), slug=slug)

    @cached_property
    def gallery(self):
        slug = self.params.get('gallery_slug')
        return get_object_or_404(models.GallerySection.objects.all(), slug=slug)

    @cached_property
    def postcard(self):
        id = self.params.get('postcard_id')
        return get_object_or_404(models.Postcard.objects.all(), id=id)

    @property
    def index(self):
        return [i.pk for i in self.items].index(self.item.pk)

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
        self.params = params
        self.item = self.postcard
        self.items = self.postcard_set.postcards.all()
        self.item_key = 'postcard_id'
        self.url_name = 'set_postcard'

    @property
    def back_url(self):
        kwargs = self.params
        del kwargs['postcard_id']
        return reverse('postcard_set', kwargs=kwargs)


class PostcardSetNavigation(NavigationMixin):
    def __init__(self, params):
        self.params = params
        self.item = self.postcard_set
        self.items = self.sets_section.postcard_sets.all()
        self.item_key = 'set_slug'
        self.url_name = 'postcard_set'

    @property
    def back_url(self):
        return f"{reverse('page')}#{self.sets_section.slug}"


@register.inclusion_tag('postcards/navigation.html')
def navigation(url_params):
    if 'sets_section_slug' in url_params and 'postcard_id' in url_params:
        navigation = SetPostcardNavigation(url_params)
    elif 'sets_section_slug' in url_params:
        navigation = PostcardSetNavigation(url_params)
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
