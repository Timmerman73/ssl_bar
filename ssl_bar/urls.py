"""ssl_bar URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from BarApp import views

from django.conf import settings  
from django.conf.urls.static import static  

urlpatterns = [
    path('',views.index,name="home"),
    path('admin/', admin.site.urls,name="admin"),
    path('register/',views.register,name="register"),
    path('login/',views.v_login,name="login"),
    path('logout/',views.v_logout,name="logout"),
    path('add_saldo/',views.add_saldo,name="add_saldo"),
    path('tikkie_change/',views.tikkie_change,name="tikkie_change"),
    path('baradmin_add/',views.bar_admin_add,name="baradmin_add"),
    path('baradmin_change/',views.bar_admin_change,name="baradmin_change"),
    path('baradmin_delete/',views.bar_admin_delete,name="baradmin_delete"),
    path('stats/',views.index,name="stats"),
]


if settings.DEBUG:  
        urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)  
