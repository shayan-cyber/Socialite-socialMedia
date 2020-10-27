from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Post(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    caption = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to = 'Post')



    def __str__(self):
        return str(self.user) + ' from ' + str(self.caption) + "-" + str(self.date)

class Profile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    userImage = models.ImageField(upload_to = 'Profile', default="default/default.png")
    bio = models.CharField(max_length=200)
    connection = models.CharField(max_length=100, blank=True)
    follower = models.IntegerField(default=0)
    following = models.IntegerField(default=0)


    def __str__(self):
        return str(self.user)

class Like(models.Model):
    user = models.ManyToManyField(User, related_name='LikingPost')
    post = models.OneToOneField(Post,on_delete=models.CASCADE)
    #likes = models.IntegerField(default = 0)

    @classmethod
    def liked(cls, post,liking_user):
        obj , create = cls.objects.get_or_create(post = post)
        obj.user.add(liking_user)
    @classmethod
    def dislike(cls, post,disliking_user):
        obj , create = cls.objects.get_or_create(post = post)
        obj.user.remove(disliking_user)
    
    def __str__(self):
        return str(self.post)


# chat system:
class ChatRoom(models.Model):
    #user_requested = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reqed')
    #user_requesting = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reqing')
    owner = models.CharField(max_length=900)
    chatter1 = models.CharField(max_length=200)
    def __str__(self):
        return str(self.owner)


class Chat(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    text = models.TextField()
    time  = models.DateTimeField(auto_now_add=True)
    chatter = models.CharField(max_length=900)
    def __str__(self):
        return str(self.text)


class Comment(models.Model):
    text = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    commentor = models.ForeignKey(User,on_delete=models.CASCADE)
    nestedcommentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nested', null=True)
    time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.text) + ' in ' + str(self.post) + ' from ' + str(self.commentor.username)

#follow models
class Following(models.Model):
    #every user will create one Following model whic will have many users whic the creating user will follow
    user = models.OneToOneField(User, on_delete = models.CASCADE)  
    followed = models.ManyToManyField(User, related_name='followinguser')
    follower = models.ManyToManyField(User, related_name= 'followeruser')

    @classmethod
    def follow(cls,user, another_account):
        obj, create = cls.objects.get_or_create(user = user)
        obj.followed.add(another_account)
        print('followed')
    @classmethod
    def unfollow(cls,user, another_account):
        obj, create = cls.objects.get_or_create(user = user)
        obj.followed.remove(another_account)
        print('unfollowed')
    def __str__(self):
        return str(self.user)


class Story(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    image = image = models.ImageField(upload_to = 'Story')
    time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.user)



