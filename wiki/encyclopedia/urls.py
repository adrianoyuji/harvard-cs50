from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.wikipage, name="entry"),
    path("search", views.search, name="search"),
    path("random", views.random, name="random"),
    path("add", views.addEntry, name="add-entry"),
    path("edit/<str:title>", views.editEntry, name="edit-entry"),
]
