from django.forms import ModelForm, widgets
from django import forms
from .models import Auction


class AuctionForm(ModelForm):
    class Meta:
        model = Auction
        fields = ["title", "image_url", "description", "category", "starting_bid"]

    def __init__(self, *args, **kwargs):
        super(AuctionForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({"class": "input"})
