from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user/<str:pk>", views.profile_page, name="profile_page"),
    path("following", views.following_view, name="following"),
    # API
    path("posts", views.posts, name="posts"),
    path("post/<str:pk>", views.handle_post, name="handle_post"),
    path("following-posts", views.following_posts, name="following_posts"),
    path("user/posts/<str:pk>", views.profile_posts, name="posts"),
    path("follow/<str:pk>", views.handle_follow, name="handle_follow"),
    path("like/<str:pk>", views.handle_like, name="handle_like"),
]
