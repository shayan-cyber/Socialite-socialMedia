from django.contrib import admin
from .models import Post, Profile, Like , ChatRoom, Chat, Comment, Following,Story
# Register your models here.
admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(Like)
admin.site.register(Chat)
admin.site.register(ChatRoom)
admin.site.register(Comment)
admin.site.register(Following)
admin.site.register(Story)