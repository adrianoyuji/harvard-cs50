from django.urls import path

from . import views

urlpatterns = [
    # Views
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("boards", views.boards_view, name="boards"),
    path("board/<str:pk>", views.board_view, name="board"),
    path("profile", views.profile, name="profile"),
    path("notifications", views.notification_view, name="notifications"),
    # APIs
    path("api/boards", views.boards, name="boards_api"),
    path("api/boards/<str:pk>", views.board, name="board_api"),
    path("api/boards/<str:pk>/invites", views.board_invites, name="board_invites_api"),
    path("api/board/<str:pk>/task", views.board_task, name="board_task_api"),
    path("api/task/<str:pk>", views.task, name="task_api"),
    path("api/notifications", views.notifications_list, name="notifications_api"),
]
