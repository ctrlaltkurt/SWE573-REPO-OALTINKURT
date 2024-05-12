from django.shortcuts import render, redirect, get_object_or_404
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from django.http import HttpResponseRedirect
from .models import Posting, Community, SiteUser
from .forms import CommunityForm , PostingForm
# Create your views here.


def my_profile(request):
    user = request.user  # Gets the current logged-in user
    communities = user.communities.all()  # Retrieves all communities that the user is a part of
    return render(request, 'posts/my_profile.html', {
        'user': user,
        'communities': communities
    })


'''
def my_profile(request):
	user_info = SiteUser.objects.all()
	return render(request, 'posts/my_profile.html', 
		{'user_info' : user_info})
'''
'''
def create_post(request):
	submitted = False
	if request.method == "POST":
		form = PostingForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/create_post?submitted=True')
	else:
		form = PostingForm
		if 'submitted' in request.GET:
			submitted = True

	return render(request, 'posts/create_post.html', {'form' : form , 'submitted' : submitted })
'''

def create_post(request):
	submitted = False
	if request.method == "POST":
		form = PostingForm(request.POST)
		if form.is_valid():
			posting = form.save(commit= False)
			posting.posted_by = request.user
			posting.save()
			#form.save()
			return HttpResponseRedirect('/create_post?submitted=True')

	else:
		form = PostingForm
		if 'submitted' in request.GET:
			submitted = True

	return render(request, 'posts/create_post.html', {'form' : form , 'submitted' : submitted })

def modify_post(request,posting_id):	
	posting = Posting.objects.get(pk=posting_id)
	form = PostingForm(request.POST or None, instance=posting)
	if form.is_valid():
		form.save()
		return redirect('my-posts')

	return render(request, 'posts/modify_post.html',
		{'posting' : posting, 'form':form})


def modify_community(request,community_id):	
	community = Community.objects.get(pk=community_id)
	form = CommunityForm(request.POST or None, instance=community)
	if form.is_valid():
		form.save()
		return redirect('list-communities')

	return render(request, 'posts/modify_community.html', 
		{'community' : community, 'form':form})

def join_community(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    if request.method == 'POST':
        community.members.add(request.user)  # Add the user to the community
        # Redirect to the community page with the specific community_id
        return redirect('show-community', community_id=community_id)
    # Optionally handle GET request or invalid request method
    return redirect('some_error_page')

def leave_community(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    if request.method == 'POST':
        community.members.remove(request.user)  # Remove the user from the community
        return redirect('show-community', community_id=community_id)
    return redirect('some_error_page')

def search_communities(request):
	if request.method == "POST":
		searched = request.POST['searched']
		communities = Community.objects.filter(name__contains=searched)
		return render(request, 'posts/search_communities.html', 
		{'searched':searched,'communities':communities})
	else:
		return render(request, 'posts/search_communities.html', 
		{})


def show_community(request,community_id):
	community = Community.objects.get(pk=community_id)
	posts = Posting.objects.filter(community=community).order_by('-posting_date')
	posts_count = posts.count()
	return render(request, 'posts/show_community.html', 
		{'community' : community, 'posts': posts, 'posts_count' : posts_count})


def list_communities(request):
	community_list = Community.objects.all().order_by('-creation_date')
	return render(request, 'posts/list_communities.html', 
		{'community_list' : community_list})

def my_communities(request):
	community_list = Community.objects.all().order_by('-creation_date')
	return render(request, 'posts/my_communities.html', 
		{'community_list' : community_list})


def create_community(request):
	submitted = False
	if request.method == "POST":
		form = CommunityForm(request.POST)
		if form.is_valid():
			community = form.save(commit= False)
			community.owner_username = request.user
			community.save()
			#form.save()
			return HttpResponseRedirect('/create_community?submitted=True')
	else:
		form = CommunityForm
		if 'submitted' in request.GET:
			submitted = True

	return render(request, 'posts/create_community.html', {'form' : form , 'submitted' : submitted })

'''
def create_community(request):
	submitted = False
	if request.method == "POST":
		form = CommunityForm(request.POST)
		if form.is_valid():
			community = form.save(commit= False)
			community.owner_id = request.user.id
			community.save()
			#form.save()
			return HttpResponseRedirect('/create_community?submitted=True')
	else:
		form = CommunityForm
		if 'submitted' in request.GET:
			submitted = True

	return render(request, 'posts/create_community.html', {'form' : form , 'submitted' : submitted })
'''

def my_postings(request):
	posting_list = Posting.objects.all().order_by('-posting_date')
	return render(request, 'posts/my_posts.html', 
		{'posting_list' : posting_list})


def all_postings(request):
	posting_list = Posting.objects.all().order_by('-posting_date')
	return render(request, 'posts/home.html', 
		{'posting_list' : posting_list})


def home(request,year=datetime.now().year,month=datetime.now().strftime('%B')):
	name="Onur"
	#Convert month from name to number
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number) 

	# get current year
	now = datetime.now()
	current_year = now.year
	current_month = now.month
	# create a calendar

	cal1 = HTMLCalendar().formatmonth(year,month_number)

	# create a current date calendar

	cal2 = HTMLCalendar().formatmonth(current_year,current_month)

	# get current time

	current_time = now.strftime('%H:%M')

	return render(request,'posts/home.html',{
		"name": name,
		"year": year,
		"month": month,
		"month_number": month_number,
		"cal1" : cal1,
		"cal2" : cal2,
		"current_year" : current_year,
		"current_month" : current_month,
		"current_time" : current_time
		})