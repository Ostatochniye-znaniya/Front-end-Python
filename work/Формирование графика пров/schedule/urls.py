
from django.urls import path
from .views import скачать_pdf

urlpatterns = [
    path('pdf/', скачать_pdf, name='скачать_pdf'),
]
