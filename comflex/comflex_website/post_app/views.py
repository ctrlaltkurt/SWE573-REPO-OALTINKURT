from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Posting, Community, SiteUser, PostType, PostTypeField
from .forms import CommunityForm, PostingForm, PostTypeForm, PostTypeFieldFormSet
from django.db import transaction
from django.db.models import Count, Max
from django.contrib.auth.models import User
from .forms import TransferOwnershipForm
from django.contrib import messages

def transfer_ownership(request, community_id):
    community = get_object_or_404(Community, id=community_id)

    if request.user != community.owner_username:
        return redirect('show-community', community_id=community.id)

    if request.method == 'POST':
        form = TransferOwnershipForm(request.POST, community=community)
        if form.is_valid():
            new_owner = form.cleaned_data['new_owner']
            community.owner_username = new_owner
            community.owner_id = new_owner.id  # Update owner_id as well
            community.members.remove(request.user)
            community.save()
            return redirect('show-community', community_id=community.id)
    else:
        form = TransferOwnershipForm(community=community)

    return render(request, 'posts/transfer_ownership.html', {'form': form, 'community': community})

def add_post_type(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    if request.user != community.owner_username:
        return redirect('show-community', community_id=community.id)

    submitted = False
    if request.method == "POST":
        form = PostTypeForm(request.POST)
        formset = PostTypeFieldFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                post_type = form.save(commit=False)
                post_type.community = community
                post_type.save()

                # Ensure fixed fields are created
                if not post_type.fields.filter(is_fixed=True).exists():
                    PostTypeField.objects.create(
                        post_type=post_type, field_name='post title', field_type='text', is_fixed=True)
                    PostTypeField.objects.create(
                        post_type=post_type, field_name='description', field_type='text', is_fixed=True)

                formset.instance = post_type
                formset.save()
            return HttpResponseRedirect(f'/community/{community_id}/add_post_type?submitted=True')
        else:
            print("Form errors:", form.errors)
            print("Formset errors:", formset.errors)
    else:
        form = PostTypeForm()
        formset = PostTypeFieldFormSet()
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'posts/add_post_type.html', {
        'form': form, 'formset': formset, 'submitted': submitted, 'community': community
    })

def my_profile(request):
    user = request.user  # Gets the current logged-in user
    communities = user.communities.all()  # Retrieves all communities that the user is a part of
    liked_posts = Posting.objects.filter(likes=user)  # Retrieves all posts that the user liked

    # Ensure custom fields are correctly parsed for liked posts
    for post in liked_posts:
        post.custom_fields = post.get_custom_fields()

    return render(request, 'posts/my_profile.html', {
        'user': user,
        'communities': communities,
        'liked_posts': liked_posts
    })

def create_post(request):
    community_id = request.GET.get('community_id')
    community = get_object_or_404(Community, id=community_id)
    post_types = community.post_types.all()

    return render(request, 'posts/select_post_type.html', {'post_types': post_types, 'community': community})

def create_post_form(request):
    post_type_id = request.GET.get('post_type_id')
    if not post_type_id:
        community_id = request.GET.get('community_id')
        return redirect(f'/create_post/?community_id={community_id}')
    
    post_type = get_object_or_404(PostType, id=post_type_id)
    submitted = request.GET.get('submitted', False)
    
    if request.method == "POST":
        form = PostingForm(request.POST, request.FILES, post_type=post_type)
        if form.is_valid():
            posting = form.save(commit=False)
            posting.posted_by = request.user
            posting.community = post_type.community
            posting.post_type = post_type  # Ensure post_type is set
            custom_fields = {field: form.cleaned_data[field] for field in form.cleaned_data if field not in ['name', 'description']}
            print(f"Custom fields before saving: {custom_fields}")  # Debugging print statement
            print(f"Form files: {request.FILES}")  # Debugging print statement
            if 'picture' in request.FILES:
                print(f"Picture field is present: {request.FILES['picture']}")  # Debugging print statement
            else:
                print("Picture field is not present in the uploaded files.")  # Debugging print statement
            posting.set_custom_fields(custom_fields)
            posting.save()
            return redirect(f'/create_post_form/?post_type_id={post_type.id}&submitted=True')
        else:
            print("Form errors:", form.errors)
    else:
        form = PostingForm(post_type=post_type)
        
    return render(request, 'posts/create_post_form.html', {'form': form, 'post_type': post_type, 'submitted': submitted})

def modify_post(request, posting_id):    
    posting = get_object_or_404(Posting, pk=posting_id)
    post_type = posting.post_type

    if request.user != posting.posted_by:
        return render(request, 'posts/modify_post.html', {'posting': posting, 'form': None, 'submitted': False, 'access_denied': True})

    if request.method == "POST":
        form = PostingForm(request.POST, request.FILES, instance=posting, post_type=post_type)
        if form.is_valid():
            updated_posting = form.save(commit=False)
            custom_fields = {field: form.cleaned_data[field] for field in form.cleaned_data if field not in ['name', 'description']}
            updated_posting.set_custom_fields(custom_fields)
            updated_posting.save()
            return redirect('my-posts')
    else:
        form = PostingForm(instance=posting, post_type=post_type)
        
    return render(request, 'posts/modify_post.html', {'posting': posting, 'form': form, 'submitted': False})

def modify_community(request, community_id):    
    community = Community.objects.get(pk=community_id)
    form = CommunityForm(request.POST or None, instance=community)
    if form.is_valid():
        form.save()
        return redirect('list-communities')

    return render(request, 'posts/modify_community.html', {'community': community, 'form': form})

def join_community(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    if request.method == 'POST':
        community.members.add(request.user)  # Add the user to the community
        return redirect('show-community', community_id=community_id)
    return redirect('some_error_page')

def leave_community(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    if request.method == 'POST':
        if request.user.id != community.owner_id:
            community.members.remove(request.user)  # Remove the user from the community
        else:
            return render(request, 'posts/show_community.html', {
                'community': community,
                'error_message': "Community owners cannot leave their own community."
            })
        return redirect('show-community', community_id=community_id)
    return redirect('some_error_page')

def search_communities(request):
    if request.method == "POST":
        searched = request.POST['searched']
        communities = Community.objects.filter(name__contains=searched)
        return render(request, 'posts/search_communities.html', 
        {'searched': searched, 'communities': communities})
    else:
        return render(request, 'posts/search_communities.html', {})


def show_community(request, community_id, template_name='posts/show_community.html'):
    community = get_object_or_404(Community, pk=community_id)
    sort = request.GET.get('sort', 'date')

    # Determine sorting logic
    if sort == 'likes':
        posts = Posting.objects.filter(community=community).annotate(num_likes=Count('likes')).order_by('-num_likes')
    else:
        posts = Posting.objects.filter(community=community).order_by('-posting_date')

    posts_count = posts.count()

    # Query for the most liked post
    most_liked_post = posts.annotate(num_likes=Count('likes')).order_by('-num_likes').first()

    # Query for the last post date based on the actual posting date
    last_post = Posting.objects.filter(community=community).order_by('-posting_date').first()
    last_post_date = last_post.posting_date if last_post else None

    if most_liked_post:
        most_liked_post.custom_fields = most_liked_post.get_custom_fields()  # Ensure custom fields are loaded properly

    for post in posts:
        post.custom_fields = post.get_custom_fields()  # Ensure custom fields are loaded properly

    return render(request, template_name, {
        'community': community,
        'posts': posts,
        'posts_count': posts_count,
        'most_liked_post': most_liked_post,
        'last_post_date': last_post_date,
        'sort': sort
    })



def discover(request):
    # Fetch new communities
    new_communities = Community.objects.all().order_by('-creation_date')[:10]

    # Fetch popular communities by number of posts
    popular_communities = Community.objects.annotate(num_posts=Count('posting')).order_by('-num_posts')[:10]

    # Fetch recently active communities by date of the last post
    recently_active_communities = Community.objects.annotate(last_post_date=Max('posting__posting_date')).order_by('-last_post_date')[:10]
    most_crowded_communities = Community.objects.annotate(member_count=Count('members')).order_by('-member_count')[:5]  # Adjust the number as needed

    return render(request, 'posts/discover.html', {
        'most_crowded_communities': most_crowded_communities,
        'new_communities': new_communities,
        'popular_communities': popular_communities,
        'recently_active_communities': recently_active_communities,
    })



def list_communities(request):
    community_list = Community.objects.all().order_by('-creation_date')
    return render(request, 'posts/list_communities.html', {'community_list': community_list})

def my_communities(request):
    community_list = Community.objects.all().order_by('-creation_date')
    return render(request, 'posts/my_communities.html', {'community_list': community_list})

def create_community(request):
    submitted = False
    if request.method == "POST":
        form = CommunityForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            community.owner_username = request.user
            community.owner_id = request.user.id  # Set the owner_id correctly
            community.save()
            community.members.add(request.user)  # Add the creator to the community's members
            return HttpResponseRedirect('/create_community?submitted=True')
    else:
        form = CommunityForm()
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'posts/create_community.html', {'form': form, 'submitted': submitted})

def my_postings(request):
    posting_list = Posting.objects.filter(posted_by=request.user).order_by('-posting_date')
    
    for post in posting_list:
        post.custom_fields = post.get_custom_fields()
    
    return render(request, 'posts/my_posts.html', {'posting_list': posting_list})


def all_postings(request):
    if request.user.is_authenticated:
        user_communities = Community.objects.filter(members=request.user)
        posting_list = Posting.objects.filter(community__in=user_communities).order_by('-posting_date')
    else:
        posting_list = Posting.objects.annotate(num_likes=Count('likes')).filter(num_likes__gt=1).order_by('-posting_date')

    for post in posting_list:
        post.custom_fields = post.get_custom_fields()  # Ensure custom fields are loaded properly

    return render(request, 'posts/home.html', {'posting_list': posting_list})

def like_post(request, post_id):
    if not request.user.is_authenticated:
        messages.warning(request, "You have to log in to like a post!")
        return redirect('login-user')

    post = get_object_or_404(Posting, id=post_id)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        if post.dislikes.filter(id=request.user.id).exists():
            post.dislikes.remove(request.user)
        post.likes.add(request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def dislike_post(request, post_id):
    if not request.user.is_authenticated:
        messages.warning(request, "You have to log in to dislike a post!")
        return redirect('login-user')

    post = get_object_or_404(Posting, id=post_id)
    if post.dislikes.filter(id=request.user.id).exists():
        post.dislikes.remove(request.user)
    else:
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        post.dislikes.add(request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
