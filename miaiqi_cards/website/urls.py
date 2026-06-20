from django.urls import path
from simple_page.views import page_view


urlpatterns = [
    path('', page_view, name='page', kwargs={'slug': 'home'}),
]
