from django.shortcuts import render, HttpResponse, redirect,HttpResponseRedirect 
from django.urls import reverse_lazy,reverse
#from django.contrib.humanize import naturaltime

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib import messages
from django.contrib.auth.models import User
from . models import Post,Profile, Like, ChatRoom, Chat, Comment, Following, Story
from django.contrib.auth.decorators import login_required
import json
from django.db.models import Max
from random import shuffle
from django.views.generic import ListView
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

# Create your views here.
@login_required(login_url='/')
def userHome(request):
    following_obj = Following.objects.get(user= request.user)
    followed_users = [i for i in following_obj.followed.all()]
    followed_users.append(request.user)
    following_users_posts = Post.objects.filter(user__in = followed_users).order_by('-date')
    chat_rooms = ChatRoom.objects.filter(owner__icontains=request.user.username).annotate(max_pub_date=Max('chat__time')).order_by('-max_pub_date')
    comments = Comment.objects.all().order_by('-time')
    #print(chat_rooms)
    profs =[]
    
    for i in chat_rooms:
        owner = i.chatter1
        #print(owner)
        chatname = str(owner).replace(request.user.username,'')
        user1 = User.objects.filter(username=chatname)
        profile1 = Profile.objects.get(user = user1[0])
        profs.append(profile1)


        
        
        
    #reccomended posts
    my_lists = Post.objects.all().difference(Post.objects.filter(user__in = followed_users))
    posts = list(my_lists)
    shuffle(posts)
    #suggested users
    sugs = Profile.objects.all().difference(Profile.objects.filter(user__in = followed_users))
    suggested_profiles = list(sugs)
    shuffle(suggested_profiles)

    
    liked_post=[]
    for i in following_users_posts:
        is_lked = Like.objects.filter(post = i, user= request.user)
        if is_lked:
            liked_post.append(i)
    stories = Story.objects.filter(user__in = followed_users).order_by('-time')
    sug_stories = Story.objects.all().difference(Story.objects.filter(user__in = followed_users))
    



    context={
        'posts':posts,
        "liked_post":liked_post,
        'profs':profs,
        'chatrooms':chat_rooms,
        'comments': comments,
        'following_users_posts':following_users_posts,
        'suggested_profiles':suggested_profiles,
        'stories':stories,
        "sug_stories":sug_stories
        

    }
    #print(liked_post)


    
    return render(request,'userpage/postfeed.html',context)

def post(request):
    if request.method =='POST':
        image_ = request.FILES['image']
        captions_ = request.POST.get('captions','')
        user_ = request.user
        print(captions_,user_)
        post_obj = Post(user=user_,caption=captions_,image=image_)
        post_obj.save()
        messages.success(request,'Post Has Been Added ')
        return redirect('/userpage')
    else:
        return redirect('/userpage')
        messages.warning(request,'Something Went Wrong')

def delpost(request, ID):
    post_ = Post.objects.filter(pk = ID)
    if post_[0].image :
        image_path = post_[0].image.url # image path to delete

    
    post_.delete()
    messages.info(request,"Post Deleted")
    return redirect('/userpage')
@login_required(login_url='/')
def userProfile(request, username):
    user = User.objects.filter(username=username)
    if user:
        profile = Profile.objects.get(user = user[0])
        post_obj = Post.objects.filter(user= user[0]).order_by('-date')
        is_following = Following.objects.filter(user = request.user, followed = user[0])
        followings = Following.objects.get(user = user[0])
        followings_no = followings.followed.count()
        followers_no = followings.follower.count()
        print(followers_no)


        #for mutual followers
        """
        followers1 = Following.objects.filter(followed= request.user)
        followers2 = Following.objects.filter(followed = user)
        mutuals =  followers1.intersection(followers2)
        print(mutuals)
        """

        #post = getPost(user)
        context = {
            'profile':profile,
            'posts':post_obj,
            'is_following':is_following,
            'followings_no': followings_no,
            'followers_no':followers_no

        }
        return render(request, 'userpage/userProfile.html',context)
    else:
        messages.warning(request, 'User Does Not Exist')
        return redirect('/userpage')





def likepost(request):
    post_id = request.GET.get("likeid","")
    #print(id)
    post = Post.objects.get(pk = post_id)
    user = request.user
    like = Like.objects.filter(post=post, user=user)
    liked_track = False
    
    #Like.liked(post,user)
    #check if like exists
    if like:
        
        Like.dislike(post,user)
    else:
        liked_track= True
        Like.liked(post,user)
    resp = {
        'liked_track':liked_track
    }
    response = json.dumps(resp)
    




    return HttpResponse(response,content_type='application/json')


#chatroom
@login_required(login_url='/')
def talkmain(request,userchat):
    print(userchat)
    print(request.user)
    name_1 = userchat + request.user.username
    name_2 = request.user.username + userchat
    name = name_1 + name_2
    print(name)
    user = User.objects.filter(username=userchat)
    profile = Profile.objects.get(user = user[0])
    #chatroom = ChatRoom.objects.get_or_create(
        #owner=name
    #)
    if ChatRoom.objects.filter(owner__icontains=name_1).union(ChatRoom.objects.filter(owner__icontains=name_2)):
        chatroom_created = ChatRoom.objects.filter(owner__icontains=name_1).union(ChatRoom.objects.filter(owner__icontains=name_2))[0]
    else:
        chatroom_save = ChatRoom(owner=name, chatter1=name_1)
        chatroom_save.save()
        chatroom_created = ChatRoom.objects.filter(owner__icontains=name_1).union(ChatRoom.objects.filter(owner__icontains=name_2))[0]



    
    msgs = Chat.objects.filter( room=chatroom_created.pk).order_by('-time')
    if request.method == 'POST':
        text = request.POST['messages1']
        #room = request.POST['room']
        chatter = request.POST['chatter']
        msg = Chat(text=text, room = chatroom_created, chatter=chatter)
        
        msg.save()
        
    
    return render(request, 'chatroom/talk.html',{'userchat':userchat,'user':user, 'profile':profile, 'chatroom':chatroom_created,'msgs':msgs})




#comment fun
def comment(request,post_id):
    if request.method == 'POST':
        comment_ = request.POST.get('text')
        nested_ = request.POST.get('nested_commentor')
        post_ = Post.objects.get(pk = post_id)

        comment_obj = Comment(text=comment_,commentor=request.user,nestedcommentor=nested_,post=post_)
        comment_obj.save()
        
        
    return redirect('/userpage')


# follow
def follow(request,username):
    main_user = request.user
    to_follow = User.objects.get(username = username)
    #check if user followed already
    following = Following.objects.filter(user =main_user , followed = to_follow)
    if following:
        is_following = True
    else:
        is_following = False
    if is_following:
        Following.unfollow(main_user, to_follow)
        is_following = False
    else:
        Following.follow(main_user, to_follow)
        is_following =True
    resp = {
        'following':is_following,
    }
    response = json.dumps(resp)
    return HttpResponse(response , content_type = 'application/json')


#using class based views for searching users



class Search_User(ListView):
    model = User
    template_name = "userpage/search_user.html"
    def get_queryset(self):
        username = self.request.GET.get('username', '')
        search_results = User.objects.filter(username__icontains = username)
        print(username)
        print(search_results)
        return search_results


#Profile Change


def profile_change(request):
    if request.method == 'POST':
        bio = request.POST.get('bio_')
        image = request.FILES.get('image')
        link = request.POST.get('link_')
        if bio:
            prof1 = Profile.objects.get(user = request.user)
            prof1.bio = bio
            prof1.save()
            print('Bio Updated')
            
        if image:
            prof2 = Profile.objects.get(user = request.user)
            prof2.userImage = image
            prof2.save()
            print('DP Updated')

            
        if link:
            prof3 =Profile.objects.get(user = request.user)
            prof3.connection = link
            prof3.save()
            print('Link Updated')
    return HttpResponseRedirect(reverse('userprofile', args=[str(request.user)]))




def about(request):
    if request.method =="POST":
        email = request.POST.get('email')
        issue = request.POST.get('issue')
        text = request.POST.get('text')
        messages.success(request,'Your Message Sent Successfully')
        print(email)
        print(issue)
        print(text)
        #email to Admin
        template1 = render_to_string('con1.html', { 'email': email, "message":text, "issue":issue})
        email1 = EmailMessage(
            email + ' Has Gave Us Feedback',
            template1,
            settings.EMAIL_HOST_USER,
            ['debroyshayan@gmail.com'],

            )
        email1.fail_silently = False
        email1.send()
        
         

        #email to user

        template2 = render_to_string('con2.html', { 'email': email, "message":text, "issue":issue})
        email2 = EmailMessage(
            email + ' , We Received You Feedback',
            template2,
            settings.EMAIL_HOST_USER,
            [email],

            )
        email2.fail_silently = False
        email2.send()
        

        
    return render(request, 'about.html')


#story
def story(request):
    if request.method =='POST':
        image = request.FILES.get('image')
        story_obj = Story(user= request.user, image=image)
        story_obj.save()
        messages.success(request,'Story Added')



    
    return redirect('/userpage')









"""
def talkmessages(request ,chatroom):
    #print(list(chatroom))
    #croom = chatroom[chatroom.find("(")+1:chatroom.find(",")]
    #print(croom)
    #croom2 = croom[chatroom.find(":")+1:chatroom.find(">")-1]
    #print(croom2)
    msgs = Chat.objects.filter( room=chatroom).order_by('-time')
    results = []
    for msg in msgs:
        result = [msg.text, naturaltime(msg.time)]
        results.append(result)
    return JsonResponse(results, safe = False)

    pass
"""
"""
# nOtifications
from django import template
register = template.Library()
@register.simple_tag(name='unread_messages')
def unread_messages(user):
    return user.Chat.filter(read=False).count()
    #replace the messages_set with the appropriate related_name, and also the filter field. (I am assuming it to be "read")

#register.simple_tag(unread_messages)
"""