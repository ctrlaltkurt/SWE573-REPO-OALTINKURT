from django.urls import path
from . import views

urlpatterns = [
    #path('',views.home, name="home"),
    #path('<int:year>/<str:month>/',views.home, name="home"),
    path('home',views.all_postings, name="home"),    
    path('create_community',views.create_community,name="create-community"),
    path('list_communities',views.list_communities,name="list-communities"),
    path('my_communities',views.my_communities,name="my-communities"),
    path('show_community/<int:community_id> ',views.show_community,name="show-community"),
    path('search_communities',views.search_communities,name="search-communities"),
    path('modify_community/<community_id> ',views.modify_community,name="modify-community"),
    path('modify_post/<posting_id> ',views.modify_post,name="modify-post"),
    path('create_post',views.create_post,name="create-post"),    
    path('my_profile',views.my_profile,name="my-profile"),
    path('my_posts',views.my_postings, name="my-posts"), 
    path('community/<int:community_id>/join/', views.join_community, name='join-community'),
    path('community/<int:community_id>/leave/', views.leave_community, name='leave-community'),
    path('community/<int:community_id>/add_post_type/', views.add_post_type, name='add-post-type'),
]