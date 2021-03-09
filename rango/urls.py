from django.urls import path
from rango import views
from rango.views import AboutView

app_name = 'rango'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('category/<slug:category_name_slug>/', views.ShowCategory.as_view(), name='show_category'),
    path('add_category/', views.AddCategoryView.as_view(), name='add_category'),
    path('category/<slug:category_name_slug>/add_page/', views.AddPageView.as_view(), name='add_page'),
    # path('register/', views.register, name='register'),
    # path('login/', views.user_login, name='login'),
    path('restricted/', views.restricted, name='restricted'),
    # path('logout/', views.user_logout, name='logout'),
    path('goto/', views.GotoView.as_view(), name='goto'),
    path('register_profile/', views.register_profile, name='register_profile'),
    path('profile/<username>/', views.ProfileView.as_view(), name='profile'),
    path('profiles/', views.ListProfilesView.as_view(), name='list_profiles'),
    path('like_category/', views.LikeCategoryView.as_view(), name='like_category'),
    path('suggest/', views.CategorySuggestionView.as_view(), name='suggest'),
    # path('search/', views.search, name='search'),
    path('search_add_page/', views.SearchAddPageView.as_view(), name='search_add_page'),
    path('chat/<chat_id>/<user_id>/', views.ChatView.as_view(), name='chat'),
    path('chat_add_message/', views.ChatAddMessageView.as_view(), name='chat_add_message'),
    path('message_check/', views.MessageCheckView.as_view(), name='message_check'),
    path('chat_update/', views.ChatUpdateView.as_view(), name='chat_update'),
    path('new_chat/<user_id>/', views.NewChatView.as_view(), name='new_chat'),
    path('chats/<user_id>/', views.ChatsView.as_view(), name='chats'),
]
