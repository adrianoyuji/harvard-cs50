from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, request
from django.http.response import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.core.paginator import Paginator
import json

from .models import Post, User


def index(request):
    return render(request, "network/index.html")


@login_required(login_url="/login")
def following_view(request):
    return render(request, "network/following.html")


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
                "network/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "network/login.html")


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
                request, "network/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request, "network/register.html", {"message": "Username already taken."}
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


# API
def posts(request):
    if request.method == "POST" and request.user.is_authenticated:
        data = json.loads(request.body)
        post = Post.objects.create(
            message=data["message"],
            owner=User.objects.get(id=request.user.id),
        )
        post.save()
        return JsonResponse({"message": "success"}, status=201, safe=False)
    if request.method == "GET":
        posts = Post.objects.order_by("-created")
        paginator = Paginator(posts, 10)
        page_number = request.GET.get("page")
        if page_number == None:
            page_number = 1
        page_obj = paginator.get_page(page_number)
        return JsonResponse(
            {
                "pagination": {
                    "page_range": list(paginator.page_range),
                    "current_page": int(page_number),
                    "end_index": int(page_obj.end_index()),
                    "start_index": int(page_obj.start_index()),
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous(),
                },
                "posts": [post.serialize(request.user.id) for post in page_obj],
            },
            safe=False,
        )

    return JsonResponse(
        {"message": "invalid http method."},
        safe=False,
    )


def following_posts(request):
    if request.user.is_authenticated:
        following = list(request.user.following.all())
        following_ids = []
        for x in following:
            following_ids.append(x.id)
        posts = Post.objects.filter(owner__id__in=following_ids).order_by("-created")
        paginator = Paginator(posts, 10)
        page_number = request.GET.get("page")
        if page_number == None:
            page_number = 1
        page_obj = paginator.get_page(page_number)
        return JsonResponse(
            {
                "pagination": {
                    "page_range": list(paginator.page_range),
                    "current_page": int(page_number),
                    "end_index": int(page_obj.end_index()),
                    "start_index": int(page_obj.start_index()),
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous(),
                },
                "posts": [post.serialize(request.user.id) for post in page_obj],
            },
            safe=False,
        )
    else:
        return JsonResponse([], safe=False)


def profile_posts(request, pk):
    try:
        profile = User.objects.get(id=pk)
    except User.DoesNotExist:
        return JsonResponse({"message": "profile not Found"}, status=404, safe=False)
    posts = Post.objects.filter(owner=pk).order_by("-created")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    if page_number == None:
        page_number = 1
    page_obj = paginator.get_page(page_number)
    return JsonResponse(
        {
            "pagination": {
                "page_range": list(paginator.page_range),
                "current_page": int(page_number),
                "end_index": int(page_obj.end_index()),
                "start_index": int(page_obj.start_index()),
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
            "posts": [post.serialize(request.user.id) for post in page_obj],
        },
        safe=False,
    )


def profile_page(request, pk):
    try:
        profile = User.objects.get(id=pk)
    except User.DoesNotExist:
        return render(
            request,
            "network/profile_page.html",
            {"message": "This User does not exist."},
        )

    if request.user.is_authenticated:
        try:
            request.user.following.get(id=pk)
            isFollowing = True
        except User.DoesNotExist:
            isFollowing = False

    return render(
        request,
        "network/profile_page.html",
        {"profile": profile, "pk": int(pk), "is_following": isFollowing},
    )


@login_required(login_url="/login")
def handle_follow(request, pk):
    if request.method == "POST":
        try:
            profile = User.objects.get(id=pk)
        except User.DoesNotExist:
            return render(
                request,
                "network/profile_page.html",
                {"message": "This User does not exist."},
            )
        is_following = request.POST["is_following"]
        user = request.user
        if is_following == "true":
            user.following.remove(profile)
            user.save()
        else:
            user.following.add(profile)
            user.save()
        return redirect(f"/user/{pk}")
    else:
        return redirect(f"/")


def handle_post(request, pk):
    if request.method == "PUT" and request.user.is_authenticated:
        try:
            post = Post.objects.get(id=pk)
        except Post.DoesNotExist:
            return JsonResponse({"message": "post not Found"}, status=404, safe=False)
        if post.owner.id == request.user.id:
            data = json.loads(request.body)
            post.message = data["message"]
            post.save()
            return JsonResponse(
                {"message": "success"},
                status=200,
                safe=False,
            )
        else:
            return JsonResponse(
                {"message": "you are not the owner of this post"},
                status=403,
                safe=False,
            )
    else:
        return JsonResponse(
            {"error": "invalid http method"},
            safe=False,
        )


def handle_like(request, pk):
    if request.method == "PUT" and request.user.is_authenticated:
        try:
            post = Post.objects.get(id=pk)
        except Post.DoesNotExist:
            return JsonResponse({"message": "post not Found"}, status=404, safe=False)

        try:
            post.likes.get(id=request.user.id)
            post.likes.remove(request.user)
            post.save()
            return JsonResponse(
                {"status": "Like", "likes_count": post.likes.count()},
                status=200,
                safe=False,
            )
        except User.DoesNotExist:
            post.likes.add(request.user)
            post.save()
            return JsonResponse(
                {"status": "Liked", "likes_count": post.likes.count()},
                status=200,
                safe=False,
            )
    else:
        return JsonResponse(
            {"error": "invalid http method"},
            safe=False,
        )
