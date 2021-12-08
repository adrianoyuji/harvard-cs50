from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.BigAutoField(primary_key=True, unique=True, editable=False)
    following = models.ManyToManyField("User", blank=True, related_name="followers")


class Post(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True, editable=False)
    message = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True, related_name="liked_posts")

    def __str__(self):
        return f"{self.id}-post"

    def serialize(self, user_id):
        is_liked = False
        if bool(user_id):
            try:
                self.likes.get(id=user_id)
                is_liked = True
            except:
                is_liked = False
        return {
            "id": self.id,
            "message": self.message,
            "timestamp": self.created.strftime("%b %d %Y, %I:%M %p"),
            "likes_count": self.likes.count(),
            "liked": is_liked,
            "owner": {"id": self.owner.id, "username": self.owner.username},
        }
