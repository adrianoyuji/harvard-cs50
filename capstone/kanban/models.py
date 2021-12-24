from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.BigAutoField(primary_key=True, unique=True, editable=False)


class Board(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True, editable=False)
    title = models.CharField(
        max_length=128,
    )
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_boards"
    )
    allowed_users = models.ManyToManyField(User, related_name="allowed_boards")
    created = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "id": self.id,
            "timestamp": self.created.strftime("%b %d %Y, %I:%M %p"),
            "title": self.title,
            "description": self.description,
            "owner": {"id": self.owner.id, "username": self.owner.username},
            "allowed_users": [
                {"id": user.id, "username": user.username}
                for user in list(self.allowed_users.all())
            ],
            "tasks": [task.serialize() for task in list(self.tasks.all())],
        }


class Task(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True, editable=False)
    description = models.TextField(null=True, blank=True)
    title = models.CharField(max_length=32, null=True, blank=True)
    status = models.CharField(
        max_length=16,
        default="todo",
    )
    board = models.ForeignKey("Board", on_delete=models.CASCADE, related_name="tasks")
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_tasks"
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        related_name="assigned_tasks",
        default=None,
        null=True,
        blank=True,
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        related_name="review_tasks",
        default=None,
        null=True,
        blank=True,
    )
    created = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "timestamp": self.created.strftime("%b %d %Y, %I:%M %p"),
            "description": self.description,
            "status": self.status,
            "assignee": {"id": self.assignee.id, "username": self.assignee.username}
            if self.assignee != None
            else None,
            "reviewer": {"id": self.reviewer.id, "username": self.reviewer.username}
            if self.reviewer != None
            else None,
            "owner": {"id": self.owner.id, "username": self.owner.username},
        }


class Notification(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True, editable=False)
    message = models.TextField(null=True, blank=True)
    board = models.ForeignKey("Board", on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    created = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "id": self.id,
            "timestamp": self.created.strftime("%b %d %Y, %I:%M %p"),
            "message": self.message,
            "board": {"id": self.board.id},
        }
