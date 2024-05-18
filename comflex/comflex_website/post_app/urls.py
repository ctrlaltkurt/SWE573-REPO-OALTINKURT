from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('home', views.all_postings, name="home"),
    path('create_community', views.create_community, name="create-community"),
    path('list_communities', views.list_communities, name="list-communities"),
    path('my_communities', views.my_communities, name="my-communities"),
    path('show_community/<int:community_id>', views.show_community, name="show-community"),
    path('search_communities', views.search_communities, name="search-communities"),
    path('modify_community/<int:community_id>', views.modify_community, name="modify-community"),
    path('modify_post/<int:posting_id>', views.modify_post, name="modify-post"),
    path('create_post/', views.create_post, name='create-post'),  # No parameter needed here
    path('create_post_form/', views.create_post_form, name='create-post-form'),   
    path('my_profile', views.my_profile, name="my-profile"),
    path('my_posts', views.my_postings, name="my-posts"), 
    path('community/<int:community_id>/join/', views.join_community, name='join-community'),
    path('community/<int:community_id>/leave/', views.leave_community, name='leave-community'),
    path('community/<int:community_id>/add_post_type/', views.add_post_type, name='add-post-type'),
    path('like_post/<int:post_id>/', views.like_post, name='like_post'),
    path('dislike_post/<int:post_id>/', views.dislike_post, name='dislike_post'),
    path('community/<int:community_id>/transfer_ownership/', views.transfer_ownership, name='transfer-ownership'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
