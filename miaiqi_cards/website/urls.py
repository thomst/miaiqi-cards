from django.urls import path, include
from simple_page.views import page_view


urlpatterns = [
    path('', page_view, name='page', kwargs={'slug': 'home'}),
    path('postcard/', include('miaiqi_cards.postcards.urls')),
    path('markdownx/', include('markdownx.urls')),
]
