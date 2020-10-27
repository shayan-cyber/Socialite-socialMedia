from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from userpage.models import Profile, Following

@receiver(post_save, sender = User)
def create_profile(sender,instance, created,**kwargs):
    if created:
        Profile.objects.create(user = instance, bio='New Socialite User')
        Following.objects.create(user= instance)

        print('Profile Created')


#following tracker
@receiver(m2m_changed,sender=Following.followed.through)
def add_follower(sender,instance,action,reverse,pk_set,**kwargs):
    '''
    sender => model which wil  send Signal(Following)
    instance => request.user
    action => pre_add,if user followed someone, else pre_remove if user unfollowed someone
    pk_set => set of pk
    '''
    followed_users = []#list of users which request.user has followed
    logged_user = User.objects.get(username = instance)
    for i in pk_set:
        user = User.objects.get(pk=i)
        following_obj = Following.objects.get(user=user)
        followed_users.append(following_obj)
    if action =='pre_add':
        for i in followed_users:
            i.follower.add(logged_user)
            i.save()
    if action =='pre_remove':
        for i in followed_users:
            i.follower.remove(logged_user)
            i.save()
    print('followers')




    pass



