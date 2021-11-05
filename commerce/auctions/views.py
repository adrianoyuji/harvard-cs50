from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from auctions.utils import is_listing_watchlisted
from .forms import AuctionForm

from .models import Bid, User, Auction, Category, Comment


def index(request):
    listings = Auction.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {"listings": listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(
                username,
                email,
                password,
                first_name=request.POST["first_name"],
                last_name=request.POST["last_name"],
            )
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url="/login")
def new_listing(request):
    if request.method == "POST":
        form = AuctionForm(request.POST)
        if form.is_valid():
            auction = Auction(
                title=form["title"].value(),
                image_url=form["image_url"].value(),
                description=form["description"].value(),
                category=Category.objects.get(id=form["category"].value())
                if form["category"].value()
                else None,
                starting_bid=form["starting_bid"].value(),
                owner=User.objects.get(id=request.user.id),
            )
            auction.save()
            return redirect(f"/listing/{auction.id}")
        else:
            return redirect("/")
    else:
        form = AuctionForm()
        return render(request, "auctions/auction_form.html", {"form": form})


def listing_view(request, pk):
    try:
        auction = Auction.objects.get(id=pk)
    except Auction.DoesNotExist:
        return render(
            request,
            "auctions/auction_view.html",
            {"message": "This Auction Listing does not exist."},
        )

    return render(
        request,
        "auctions/auction_view.html",
        {
            "listing": auction,
            "is_watchlisted": is_listing_watchlisted(pk, request.user),
        },
    )


@login_required(login_url="/login")
def create_bid(request, pk):
    try:
        auction = Auction.objects.get(id=pk)
    except Auction.DoesNotExist:
        return render(
            request,
            "auctions/auction_view.html",
            {"message": "This Auction Listing does not exist."},
        )
    if request.method == "POST":
        bidlist = list(auction.bids.all())
        price = 0
        if len(bidlist) > 0:
            price = bidlist[-1].value
        else:
            price = auction.starting_bid
        bid_value = float(request.POST.get("bid_value", ""))

        if bid_value > price:
            bid = Bid.objects.create(
                value=bid_value,
                owner=User.objects.get(id=request.user.id),
                auction=auction,
            )
            bid.save()
            return redirect(f"/listing/{pk}")
        return render(
            request,
            "auctions/auction_view.html",
            {
                "listing": auction,
                "message": "Your bid must be higher than the current one.",
                "is_watchlisted": is_listing_watchlisted(pk, request.user),
            },
        )
    else:
        return render(
            request,
            "auctions/auction_view.html",
            {
                "listing": auction,
                "is_watchlisted": is_listing_watchlisted(pk, request.user),
            },
        )


@login_required(login_url="/login")
def handle_watchlist(request, pk):
    try:
        auction = Auction.objects.get(id=pk)
    except Auction.DoesNotExist:
        return render(
            request,
            "auctions/auction_view.html",
            {"message": "This Auction Listing does not exist."},
        )
    if request.method == "POST":
        user = request.user
        try:
            item = request.user.watchlist.get(pk=pk)
            user.watchlist.remove(item)
            user.save()
        except Auction.DoesNotExist:
            user.watchlist.add(auction)
            user.save()
        return redirect(f"/listing/{pk}")


@login_required(login_url="/login")
def close_listing(request, pk):
    try:
        auction = Auction.objects.get(id=pk)
    except Auction.DoesNotExist:
        return render(
            request,
            "auctions/auction_view.html",
            {"message": "This Auction Listing does not exist."},
        )
    if auction.owner.id == request.user.id:
        auction.is_active = False
        auction.save()
    return redirect("/")


@login_required(login_url="/login")
def create_comment(request, pk):
    try:
        auction = Auction.objects.get(id=pk)
    except Auction.DoesNotExist:
        return render(
            request,
            "auctions/auction_view.html",
            {"message": "This Auction Listing does not exist."},
        )
    if request.method == "POST":
        message = request.POST.get("comment", "")
        comment = Comment.objects.create(
            message=message,
            owner=User.objects.get(id=request.user.id),
            auction=auction,
        )
        comment.save()
    return redirect(f"/listing/{pk}")


@login_required(login_url="/login")
def watchilist(request):
    listings = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {"listings": listings})


def categories_list(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {"categories": categories})


def category_listings(request, pk):
    try:
        category = Category.objects.get(id=pk)
    except Category.DoesNotExist:
        categories = Category.objects.all()
        return render(
            request,
            "auctions/categories.html",
            {
                "categories": categories,
            },
        )

    listings = category.items.filter(is_active=True)

    return render(
        request,
        "auctions/category_listings.html",
        {"listings": listings, "category_title": category.title},
    )
