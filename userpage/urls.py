"""socialite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path,include
from . import views
from .views import Search_User


urlpatterns = [
    path('', views.userHome, name="userHome"),
    path('post', views.post, name="post"),
    path('like', views.likepost, name="likepost"),
    path("delete/<int:ID>", views.delpost, name="delpost"),
    path("profile/<str:username>", views.userProfile, name="userprofile"),
    path("chat/<str:userchat>", views.talkmain, name="talk"),
    path('comment/<int:post_id>',views.comment, name="comment"),
    path('user/follow/<str:username>', views.follow, name = 'follow'),
    path('search', Search_User.as_view(), name = 'search_user'),
    path('profile_change', views.profile_change, name = 'profile_change'),
    path('about', views.about, name = 'about'),
    path('story', views.story, name = 'story'),
    



    #path('messages/<int:chatroom>', views.talkmessages, name="messages"),


    #chat
    
    
    

]


