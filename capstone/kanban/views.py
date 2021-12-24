from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.core.paginator import Paginator
import json
from .models import Task, User, Board, Notification


def index(request):
    if request.method == "GET" and "message" in request.GET:
        message = request.GET["message"]
    else:
        message = ""
    return render(request, "kanban/index.html", {"message": message})


@login_required(login_url="/login")
def board_view(request, pk):
    try:
        board = Board.objects.get(id=pk)
        if request.user.id == board.owner.id:
            return render(request, "kanban/board.html")
        try:
            board.allowed_users.get(id=request.user.id)
            return render(request, "kanban/board.html")
        except User.DoesNotExist:
            return redirect("/?message=You are not allowed to see this board.")
    except Board.DoesNotExist:
        return redirect("/?message=Board does not exist")


@login_required(login_url="/login")
def profile(request):
    if request.method == "POST":
        username = request.user.username
        password = request.POST["password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["new_password"]

        if new_password != confirm_password:
            return render(
                request, "kanban/profile.html", {"error": "Passwords do not match"}
            )
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            user.set_password(new_password)
            user.save()
            login(request, user)
            return redirect("/?message=Password changed.")
        else:
            return render(request, "kanban/profile.html", {"error": "Wrong password"})
    else:
        return render(request, "kanban/profile.html")


@login_required(login_url="/login")
def notification_view(request):
    return render(request, "kanban/notifications.html")


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
                "kanban/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "kanban/login.html")


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
                request, "kanban/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request, "kanban/register.html", {"message": "Username already taken."}
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "kanban/register.html")


@login_required(login_url="/login")
def boards_view(request):
    return render(request, "kanban/boards.html")


def boards(request):
    method = request.method
    if method == "GET":
        boards = list(request.user.created_boards.order_by("-created"))
        allowed_boards = list(request.user.allowed_boards.order_by("-created"))
        return JsonResponse(
            {
                "boards": [board.serialize() for board in (boards + allowed_boards)],
            },
            safe=False,
        )
    if method == "POST":
        data = json.loads(request.body)
        newBoard = Board.objects.create(
            title=data["title"],
            description=data["description"],
            owner=User.objects.get(id=request.user.id),
        )
        newBoard.save()
        return JsonResponse(
            {"message": "Board created successfully.", "board": newBoard.serialize()},
            safe=False,
        )

    return JsonResponse(
        {"message": "invalid http method."},
        safe=False,
    )


def board(request, pk):
    method = request.method
    try:
        board = Board.objects.get(id=pk)
    except Board.DoesNotExist:
        return JsonResponse(
            {"message": "Board not found."},
            safe=False,
        )
    if method == "GET":
        if request.user.is_authenticated and (
            board.owner.id == request.user.id
            or board.allowed_users.get(id=request.user.id)
        ):
            return JsonResponse(
                {"board": board.serialize()},
                safe=False,
            )
    if method == "PUT":
        if request.user.is_authenticated and (
            board.owner.id == request.user.id
            or board.allowed_users.get(id=request.user.id)
        ):
            data = json.loads(request.body)
            board.title = data["title"]
            board.description = data["description"]
            board.save()
            return JsonResponse(
                {"message": "Board updated."},
                safe=False,
            )
        else:
            return JsonResponse(
                {"error": "Unauthorized"},
                safe=False,
            )
    if method == "PATCH":
        if request.user.is_authenticated and (
            board.owner.id == request.user.id
            or board.allowed_users.get(id=request.user.id)
        ):
            data = json.loads(request.body)
            try:
                foundUser = User.objects.get(username=data["username"])
                board.allowed_users.add(foundUser)
                board.save()
                return JsonResponse(
                    {"user": {"username": foundUser.username, "id": foundUser.id}},
                    safe=False,
                )
            except User.DoesNotExist:
                return JsonResponse(
                    {"message": "User does not exist."},
                    status=404,
                    safe=False,
                )
    if method == "DELETE":
        if request.user.is_authenticated and (
            board.owner.id == request.user.id
            or board.allowed_users.get(id=request.user.id)
        ):
            board.delete()
            return JsonResponse(
                {"message": "Board successfuly deleted."},
                safe=False,
            )
        else:
            return JsonResponse(
                {"error": "Unauthorized"},
                safe=False,
            )

    return JsonResponse(
        {"message": "invalid http method."},
        safe=False,
    )


def board_invites(request, pk):
    method = request.method
    try:
        board = Board.objects.get(id=pk)
    except Board.DoesNotExist:
        return JsonResponse(
            {"message": "Board not found."},
            safe=False,
        )

    if method == "PATCH":
        if request.user.is_authenticated and (
            board.owner.id == request.user.id
            or board.allowed_users.get(id=request.user.id)
        ):
            data = json.loads(request.body)
            try:
                foundUser = User.objects.get(username=data["username"])
                try:
                    board.allowed_users.get(id=foundUser.id)
                    return JsonResponse(
                        {"message": "User already invited."},
                        status=400,
                        safe=False,
                    )
                except User.DoesNotExist:
                    board.allowed_users.add(foundUser)
                    board.save()
                    foundUser.notifications.add(
                        Notification.objects.create(
                            board=board,
                            message=f"<strong>{request.user.username}</strong> invited you to join <strong>{board.title}</strong>.",
                            recipient=foundUser,
                        )
                    )
                    return JsonResponse(
                        {"user": {"username": foundUser.username, "id": foundUser.id}},
                        safe=False,
                    )
            except User.DoesNotExist:
                return JsonResponse(
                    {"message": "User does not exist."},
                    status=404,
                    safe=False,
                )
    if method == "DELETE":
        if request.user.is_authenticated and (
            board.owner.id == request.user.id
            or board.allowed_users.get(id=request.user.id)
        ):
            data = json.loads(request.body)
            try:
                foundUser = User.objects.get(username=data["username"])
                if foundUser.id == request.user.id or foundUser.id == board.owner.id:
                    return JsonResponse(
                        {"message": "You can't remove yourself or the owner."},
                        status=400,
                        safe=False,
                    )
                board.allowed_users.remove(foundUser)
                board.save()
                return JsonResponse(
                    {"user": {"username": foundUser.username, "id": foundUser.id}},
                    safe=False,
                )
            except User.DoesNotExist:
                return JsonResponse(
                    {"message": "User does not exist."},
                    status=404,
                    safe=False,
                )

    return JsonResponse(
        {"message": "invalid http method."},
        safe=False,
    )


def task(request, pk):
    method = request.method
    try:
        task = Task.objects.get(id=pk)
    except Task.DoesNotExist:
        return JsonResponse(
            {"message": "Task not found."},
            safe=False,
        )
    if method == "GET":
        return JsonResponse(
            {
                "message": "Task found.",
                "task": task.serialize(),
            },
            safe=False,
        )
    if method == "PATCH":
        data = json.loads(request.body)
        task.status = data["status"]
        task.save()
        if task.assignee != None:
            task.assignee.notifications.add(
                Notification.objects.create(
                    board=task.board,
                    message=f"<strong>{request.user.username}</strong> updated the status of <strong>{task.title}</strong>.",
                    recipient=task.assignee,
                )
            )
        if task.reviewer != None:
            task.reviewer.notifications.add(
                Notification.objects.create(
                    board=task.board,
                    message=f"<strong>{request.user.username}</strong> updated the status of <strong>{task.title}</strong>.",
                    recipient=task.reviewer,
                )
            )
        return JsonResponse(
            {
                "message": "Task found.",
                "task": task.serialize(),
            },
            safe=False,
        )
    if method == "PUT":
        data = json.loads(request.body)
        task.description = data["description"]
        task.title = data["title"]
        try:
            assignee = (
                User.objects.get(id=data["assignee_id"])
                if data["assignee_id"] != "0"
                else None
            )
            task.assignee = assignee
            if assignee != None:
                assignee.notifications.add(
                    Notification.objects.create(
                        board=task.board,
                        message=f"<strong>{request.user.username}</strong> assigned <strong>{task.title}</strong> to you.",
                        recipient=task.assignee,
                    )
                )
        except User.DoesNotExist:
            pass
        try:
            reviewer = (
                User.objects.get(id=data["reviewer_id"])
                if data["reviewer_id"] != "0"
                else None
            )
            task.reviewer = reviewer
            if reviewer != None:
                reviewer.notifications.add(
                    Notification.objects.create(
                        board=task.board,
                        message=f"<strong>{request.user.username}</strong> tagged you to review <strong>{task.title}</strong>",
                        recipient=task.reviewer,
                    )
                )
        except User.DoesNotExist:
            pass

        task.status = data["status"]
        task.save()
        return JsonResponse(
            {
                "message": "Task updated.",
                "task": task.serialize(),
            },
            safe=False,
        )

    if method == "DELETE":
        task.delete()
        return JsonResponse(
            {
                "message": "Task delete.",
            },
            status=200,
            safe=False,
        )

    return JsonResponse(
        {"message": "invalid http method."},
        status=400,
        safe=False,
    )


def board_task(request, pk):
    method = request.method
    try:
        board = Board.objects.get(id=pk)
    except Board.DoesNotExist:
        return JsonResponse(
            {"message": "Board not found."},
            safe=False,
        )
    if method == "POST":
        if request.user.is_authenticated and (
            board.owner.id == request.user.id
            or board.allowed_users.get(id=request.user.id)
        ):
            data = json.loads(request.body)
            newTask = Task.objects.create(
                title=data["title"],
                description=data["description"],
                owner=User.objects.get(id=request.user.id),
                assignee=User.objects.get(id=data["assignee_id"])
                if data["assignee_id"] != "0"
                else None,
                reviewer=User.objects.get(id=data["reviewer_id"])
                if data["reviewer_id"] != "0"
                else None,
                board=Board.objects.get(id=pk),
                status=data["status"],
            )
            newTask.save()
            return JsonResponse(
                {
                    "message": "Board created successfully.",
                    "task": newTask.serialize(),
                },
                safe=False,
            )
        else:
            return JsonResponse(
                {"error": "Unauthorized"},
                status=403,
                safe=False,
            )

    return JsonResponse(
        {"message": "invalid http method."},
        status=400,
        safe=False,
    )


def notifications_list(request):
    if request.user.is_authenticated and request.method == "GET":
        notifications = request.user.notifications.order_by("-created")
        paginator = Paginator(notifications, 15)
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
                "notifications": [
                    notification.serialize() for notification in page_obj
                ],
            },
            status=200,
            safe=False,
        )
    else:
        return JsonResponse(
            {"error": "Unauthorized"},
            status=403,
            safe=False,
        )
