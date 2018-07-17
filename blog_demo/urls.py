"""blog_demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path,re_path
from blogapp import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index),
    path('login/', views.login),
    path('', views.index),
    path('digg/', views.digg),
    path('upload/', views.upload),
    path('comment/', views.comment),
    path('delete/', views.delete),
    path('backend/', views.Back_manage),
    path('code/',views.code),
    re_path('update/(?P<article_id>\d+)', views.update,),
    path('backend/add_article/', views.add_article),
    re_path('(?P<username>\w+)/articles/(?P<article_id>\d+)$', views.article_home),
    re_path('(?P<username>\w+)/(?P<condition>article|category|tag)/(?P<pagam>.*)/', views.home_page),
    path('logout/', views.logout),
    re_path('(?P<username>\w+)/', views.home_page),

]
