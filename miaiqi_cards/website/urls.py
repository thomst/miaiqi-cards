from django.urls import path
from simple_page.views import page_view
from django.views.defaults import page_not_found


urlpatterns = [
    path('', page_view, name='page', kwargs={'slug': 'home'}),
    path('favicon.ico/', page_not_found, {'exception': Exception('Favicon not found')}),
]
