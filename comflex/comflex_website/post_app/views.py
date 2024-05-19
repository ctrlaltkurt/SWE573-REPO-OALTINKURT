from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Posting, Community, SiteUser, PostType, PostTypeField
from .forms import CommunityForm, PostingForm, PostTypeForm, PostTypeFieldFormSet
from django.db import transaction
from django.db.models import Count, Max
from django.contrib.auth.models import User
from .forms import TransferOwnershipForm
from django.contrib import messages
from django.db.models import Q
from .forms import AddModeratorForm

def dismiss_user(request, community_id, user_id):
    community = get_object_or_404(Community, id=community_id)
    user_to_dismiss = get_object_or_404(User, id=user_id)

    # Check if the user is either the community owner or a moderator
    if request.user != community.owner_username and request.user not in community.moderators.all():
        messages.error(request, "You do not have permission to dismiss users from this community.")
        return redirect('community-members', community_id=community.id)

    # Only allow dismissal if the user_to_dismiss is a member of the community
    if user_to_dismiss in community.members.all():
        # Community owner can dismiss any user
        if request.user == community.owner_username:
            community.members.remove(user_to_dismiss)
            messages.success(request, f"{user_to_dismiss.username} has been dismissed from the community.")
        # Moderators can dismiss users except other moderators and the community owner
        elif request.user in community.moderators.all():
            if user_to_dismiss != community.owner_username and user_to_dismiss not in community.moderators.all():
                community.members.remove(user_to_dismiss)
                messages.success(request, f"{user_to_dismiss.username} has been dismissed from the community.")
            else:
                messages.error(request, "You cannot dismiss the community owner or other moderators.")
    else:
        messages.error(request, "You cannot dismiss a user who is not a member.")

    return redirect('community-members', community_id=community.id)

def community_members(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    return render(request, 'posts/community_members.html', {'community': community})

def add_moderator(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    
    if request.user != community.owner_username:
        return redirect('show-community', community_id=community.id)

    if request.method == "POST":
        form = AddModeratorForm(request.POST)
        if form.is_valid():
            new_moderator = form.cleaned_data['new_moderator']
            community.moderators.add(new_moderator)
            community.save()
            return redirect('show-community', community_id=community.id)
    else:
        form = AddModeratorForm()

    return render(request, 'posts/add_moderator.html', {'form': form, 'community': community})


def remove_moderator(request, community_id, user_id):
    community = get_object_or_404(Community, id=community_id)
    if request.user != community.owner_username:
        return redirect('show-community', community_id=community.id)

    moderator = get_object_or_404(User, id=user_id)
    community.moderators.remove(moderator)
    community.save()
    return redirect('show-community', community_id=community.id)

def resign_moderator(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    if request.user in community.moderators.all():
        community.moderators.remove(request.user)
    return redirect('show-community', community_id=community_id)


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
    if request.user != community.owner_username and request.user not in community.moderators.all():
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

def my_liked_posts(request):
    user = request.user  # Gets the current logged-in user
    communities = user.communities.all()  # Retrieves all communities that the user is a part of
    liked_posts = Posting.objects.filter(likes=user)  # Retrieves all posts that the user liked

    # Ensure custom fields are correctly parsed for liked posts
    for post in liked_posts:
        post.custom_fields = post.get_custom_fields()

    return render(request, 'posts/liked_posts.html', {
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
            messages.success(request, "You have successfully left the community.")
        else:
            messages.error(request, "Community owners cannot leave their own community.")
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


def advanced_search(request):
    return render(request, 'posts/advanced_search.html')

def advanced_search_results(request):
    # Community search parameters
    community_name = request.GET.get('community_name', '')
    community_description = request.GET.get('community_description', '')
    creation_date_start = request.GET.get('creation_date_start')
    creation_date_end = request.GET.get('creation_date_end')
    min_members = request.GET.get('min_members', 0)
    max_members = request.GET.get('max_members', None)
    min_posts = request.GET.get('min_posts', 0)
    max_posts = request.GET.get('max_posts', None)
    last_post_date_start = request.GET.get('last_post_date_start')
    last_post_date_end = request.GET.get('last_post_date_end')

    # Post search parameters
    post_name = request.GET.get('post_name', '')
    post_description = request.GET.get('post_description', '')
    post_date_start = request.GET.get('post_date_start')
    post_date_end = request.GET.get('post_date_end')
    min_likes = request.GET.get('min_likes', 0)
    max_likes = request.GET.get('max_likes', None)

    # Convert numeric values to int, handling empty values
    min_members = int(min_members) if min_members else 0
    max_members = int(max_members) if max_members else None
    min_posts = int(min_posts) if min_posts else 0
    max_posts = int(max_posts) if max_posts else None
    min_likes = int(min_likes) if min_likes else 0
    max_likes = int(max_likes) if max_likes else None

    # Flags to check which type of search is being performed
    search_communities = bool(community_name or community_description or creation_date_start or creation_date_end or min_members or max_members or min_posts or max_posts or last_post_date_start or last_post_date_end)
    search_posts = bool(post_name or post_description or post_date_start or post_date_end or min_likes or max_likes)

    # Initial querysets
    communities = Community.objects.all().annotate(
        member_count=Count('members', distinct=True),
        num_posts=Count('posting', distinct=True),
        last_post_date=Max('posting__posting_date')
    )
    posts = Posting.objects.all().annotate(num_likes=Count('likes'))

    # Apply community filters
    if search_communities:
        if community_name:
            communities = communities.filter(name__icontains=community_name)
        if community_description:
            communities = communities.filter(description__icontains=community_description)
        if creation_date_start:
            communities = communities.filter(creation_date__gte=creation_date_start)
        if creation_date_end:
            communities = communities.filter(creation_date__lte=creation_date_end)
        if min_members:
            communities = communities.filter(member_count__gte=min_members)
        if max_members is not None:
            communities = communities.filter(member_count__lte=max_members)
        if min_posts:
            communities = communities.filter(num_posts__gte=min_posts)
        if max_posts is not None:
            communities = communities.filter(num_posts__lte=max_posts)
        if last_post_date_start:
            communities = communities.filter(last_post_date__gte=last_post_date_start)
        if last_post_date_end:
            communities = communities.filter(last_post_date__lte=last_post_date_end)
    else:
        communities = Community.objects.none()  # No communities should be returned if not searching for communities

    # Apply post filters
    if search_posts:
        if post_name:
            posts = posts.filter(name__icontains=post_name)
        if post_description:
            posts = posts.filter(description__icontains=post_description)
        if post_date_start:
            posts = posts.filter(posting_date__gte=post_date_start)
        if post_date_end:
            posts = posts.filter(posting_date__lte=post_date_end)
        if min_likes:
            posts = posts.filter(num_likes__gte=min_likes)
        if max_likes is not None:
            posts = posts.filter(num_likes__lte=max_likes)

        # Fetch custom fields for posts
        for post in posts:
            post.custom_fields = post.get_custom_fields()
    else:
        posts = Posting.objects.none()  # No posts should be returned if not searching for posts

    return render(request, 'posts/advanced_search_results.html', {'communities': communities, 'posts': posts, 'search_communities': search_communities, 'search_posts': search_posts})

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
    recently_active_communities = Community.objects.annotate(
        last_post_date=Max('posting__posting_date')
    ).filter(last_post_date__isnull=False).order_by('-last_post_date')[:10]

    # Fetch most crowded communities by number of members
    most_crowded_communities = Community.objects.annotate(member_count=Count('members')).order_by('-member_count')[:5]

    return render(request, 'posts/discover.html', {
        'new_communities': new_communities,
        'popular_communities': popular_communities,
        'recently_active_communities': recently_active_communities,
        'most_crowded_communities': most_crowded_communities,
    })



def list_communities(request):
    community_list = Community.objects.all().order_by('-creation_date')
    return render(request, 'posts/list_communities.html', {'community_list': community_list})

def my_communities(request):
    # Fetch all communities the user is part of
    community_list = Community.objects.filter(members=request.user).order_by('-creation_date')

    # Fetch communities owned by the user
    owned_communities = community_list.filter(owner_id=request.user.id)

    # Fetch communities the user moderates
    moderated_communities = community_list.filter(moderators=request.user)

    # Fetch communities the user joined but does not own or moderate
    joined_communities = community_list.exclude(owner_id=request.user.id).exclude(moderators=request.user)

    return render(request, 'posts/my_communities.html', {
        'owned_communities': owned_communities,
        'moderated_communities': moderated_communities,
        'joined_communities': joined_communities,
    })

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
