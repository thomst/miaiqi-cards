from django.urls import path, include
from simple_page.views import page_view
from . import views


urlpatterns = [
    path('', page_view, name='page', kwargs={'slug': 'home'}),
    path('postcard/<int:gallery_id>/<int:postcard_id>/', views.postcard, name='postcard'),
    path('markdownx/', include('markdownx.urls')),
]
