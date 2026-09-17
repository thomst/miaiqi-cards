from django.urls import path
from simple_page.views import page_view


urlpatterns = [
    path('postcard/<int:postcard_id>/', page_view, name='postcard', kwargs={'slug': 'postcard'}),
]
