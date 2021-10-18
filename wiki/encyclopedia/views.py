from django.shortcuts import render, redirect
from random import randint
from django import forms
from markdown2 import Markdown

from . import util


def index(request):
    return render(
        request,
        "encyclopedia/index.html",
        {"entries": util.list_entries(), "title": "All pages"},
    )


def search(request):
    searchQuery = request.GET.get("q", "")
    entry = util.get_entry(searchQuery)
    if entry != None:
        return redirect(f"/wiki/{searchQuery}")
    entries = util.search_entries_substring(searchQuery)
    if len(entries) > 0:
        return render(
            request,
            "encyclopedia/index.html",
            {"entries": entries, "title": f"Search results for {searchQuery}"},
        )
    else:
        return render(
            request,
            "encyclopedia/index.html",
            {"entries": [], "title": f"No results found for {searchQuery}"},
        )


def wikipage(request, title):
    entry = util.get_entry(title)
    if entry == None:
        return render(request, "encyclopedia/404.html", {"title": title})
    markdowner = Markdown()
    return render(
        request,
        "encyclopedia/entry.html",
        {"entry": markdowner.convert(entry), "title": title},
    )


def random(request):
    entries = util.list_entries()
    return redirect(f"/wiki/{entries[randint(0, len(entries) - 1)]}")


class NewEntryForm(forms.Form):
    title = forms.CharField(label="Entry Title")
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={"rows": 4, "cols": 40, "style": "height: 15em; width: 100%"},
        ),
        label="Entry Content",
    )


def addEntry(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)

        if form.is_valid():
            title = form["title"].value()
            content = form["content"].value()
            if util.get_entry(title) == None:
                util.save_entry(title, content)
                return redirect(f"/wiki/{title}")
            else:
                context = {
                    "form": form,
                    "error": f"{title} already exists",
                    "page_title": "Create New Page",
                }
                return render(request, "encyclopedia/form.html", context)

    else:
        context = {"form": NewEntryForm(), "page_title": "Create New Page"}
        return render(request, "encyclopedia/form.html", context)


def editEntry(request, title):
    if request.method == "POST":
        form = NewEntryForm(request.POST)

        if form.is_valid():
            title = form["title"].value()
            content = form["content"].value()
            if util.get_entry(title) != None:
                util.save_entry(title, content)
                return redirect(f"/wiki/{title}")
            else:
                context = {"form": form, "error": f"{title} does not exist"}
                return render(request, "encyclopedia/form.html", context)
    else:
        entry = util.get_entry(title)
        context = {
            "form": NewEntryForm({"title": title, "content": entry}),
            "page_title": "Edit Page",
        }
        return render(request, "encyclopedia/form.html", context)
