from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
import django

from pyappointment import settings, views

mtypes = '|'.join(settings.BOOKING_TYPES.keys())

urlpatterns = [
    url(r'^$', views.index),
    url(r'^(' + mtypes + r')/?$', views.view_booking_type),
    url(r'^(' + mtypes + r')/?$', views.view_booking_type),
    url(r'^(' + mtypes + r')/([1-2][0-9]{3})-([0-1][0-9])-([0-3][0-9])/?$', views.view_week),
    url(r'^book/(' + mtypes + r')/([1-2][0-9]{3})-([0-1][0-9])-([0-3][0-9])/([0-2][0-9])-([0-5][0-9])?$', views.booking_form)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
