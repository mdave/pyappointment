"""pyappointment URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin

from . import settings
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^admin/', admin.site.urls),
    url(r'^view/([1-2][0-9]{3})-([0-1][0-9])-([0-3][0-9])/?$', views.view_week),
    url(r'^book/([1-2][0-9]{3})-([0-1][0-9])-([0-3][0-9])/([0-2][0-9])-([0-5][0-9])?$', views.booking_form),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
