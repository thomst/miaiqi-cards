from django.urls import path
from . import views


urlpatterns = [
    path('contact/<int:contact_id>/form/', views.form_view, name='contact-form'),
    path('contact/<int:contact_id>/submit/', views.submit_view, name='contact-submit'),
]
