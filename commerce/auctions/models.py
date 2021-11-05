from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.db.models.deletion import CASCADE


class User(AbstractUser):
    id = models.BigAutoField(primary_key=True, unique=True, editable=False)
    watchlist = models.ManyToManyField(
        "Auction", blank=True, related_name="watchlisted_by"
    )


class Auction(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False
    )
    title = models.CharField(
        max_length=128,
    )
    image_url = models.CharField(max_length=1024, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")
    created = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        "Category", on_delete=CASCADE, related_name="items", blank=True, null=True
    )
    starting_bid = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.title}"


class Bid(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True, editable=False)
    value = models.DecimalField(max_digits=16, decimal_places=2)
    owner = models.ForeignKey(User, on_delete=CASCADE, related_name="bids")
    auction = models.ForeignKey(Auction, on_delete=CASCADE, related_name="bids")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.auction}: ${self.value}"


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True, editable=False)
    owner = models.ForeignKey(User, on_delete=CASCADE, related_name="comments")
    auction = models.ForeignKey(Auction, on_delete=CASCADE, related_name="comments")
    created = models.DateTimeField(auto_now_add=True)
    message = models.TextField(max_length=256, null=False, default="")

    def __str__(self):
        return f"{self.owner.first_name} {self.owner.last_name} comment in f{self.auction.title}"


class Category(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True, editable=False)
    title = models.CharField(max_length=64, blank=False, null=True)
    description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"
