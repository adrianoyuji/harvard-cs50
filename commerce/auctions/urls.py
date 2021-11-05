from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.new_listing, name="createListing"),
    path("listing/<str:pk>", views.listing_view, name="listing"),
    path("listing/bid/<str:pk>", views.create_bid, name="createBid"),
    path("listing/watchlist/<str:pk>", views.handle_watchlist, name="handleWatchlist"),
    path("listing/close/<str:pk>", views.close_listing, name="closeListing"),
    path("listing/comment/<str:pk>", views.create_comment, name="createComment"),
    path("watchlist", views.watchilist, name="watchlist"),
    path("categories", views.categories_list, name="categories"),
    path("categories/<str:pk>", views.category_listings, name="categories_listings"),
]
