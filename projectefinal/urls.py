"""
URL configuration for projectefinal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from django.conf import settings
from django.conf.urls.static import static
from views import redirect_signup_to_login_with_message

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.index, name='index'),
    path('users/', include('users.urls')),
    path('core/', include('core.urls')),
    path('books/', include('books.urls')),
    path('accounts/', include('allauth.urls')),
    path('accounts/3rdparty/signup/', redirect_signup_to_login_with_message)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)