from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.utils import timezone
from django.contrib import messages
from .models import User, Listing, Bid, Comment, Watchlist, Cat


def index(request):
    # bids = Bid.objects.all() # A QuerySet of all bids that share the same ID as the current listing
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(),
        # "bids": bids,
    })


def inactive(request):
    return render(request, "auctions/inactive.html", {
        "listings": Listing.objects.all(),
    })


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def listing(request, pk):
    listing = Listing.objects.get(pk=pk)
    bids = Bid.objects.filter(listing=f"{pk}") # A QuerySet of all bids sharing the same ID as the current listing
    if bids:
        bid = max([[bid.price, bid] for bid in bids])[1] # Find the Bid object with the highest bid price
        price = "${:,.2f}".format(bid.price)
    else:
        bid = None
        price = 0

    try:
        # Find the watchlist object associated with the user
        watchlist = Watchlist.objects.get(watcher=request.user)
        # Check whether the current listing is in the user's watchlist
        match = watchlist.listing.filter(pk=pk)
    except:
        match = None

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "price": price, # Bid price
        "bid": bid, # Bid object used to retrieve the bidder's name
        "match": match,
    })

def categories(request):
    categories = Cat.objects.all().order_by("name")
    return render(request, "auctions/categories.html", {
        "categories": categories,
    })


def category(request, c):
    instance = Cat.objects.get(name=c)
    category = instance.listing.all().order_by("title")
    return render(request, "auctions/category.html", {
        "name": instance.name,
        "category": category
    })

def watchlist(request): # Render the watchlist view
    try: 
        watchlist = Watchlist.objects.get(watcher=request.user)
        watching = watchlist.listing.all() # An array of all the listings in this user's watchlist
    except:
        watching = None
    return render(request, "auctions/watchlist.html", {
        "watching": watching,
    })


def add_remove(request, pk): # Add or remove listings from a user's watchlist
    if request.method == "POST":
        if (request.POST["action"]) == "add":
            try: # If a Watchlist instance associated with the user exists
                watchlist = Watchlist.objects.get(watcher=request.user)
                watchlist.listing.add(Listing.objects.get(pk=pk))
            except: # Make a new Watchlist instance associated with the user
                watchlist = Watchlist(
                    watcher=request.user,
                )
                watchlist.save()
                watchlist.listing.add(Listing.objects.get(pk=pk))
        elif (request.POST["action"]) == "remove":
            watchlist = Watchlist.objects.get(watcher=request.user)
            match = watchlist.listing.get(pk=pk) # Find the listing in the watchlist
            watchlist.listing.remove(match)
    return HttpResponseRedirect(reverse('listing', args=[pk]))


def bid(request, pk):
    if request.method == "POST":
        price = float(request.POST["bid"])
        try: # Check if a bid exists for the listing
            bid = Bid.objects.get(listing=pk) # An QuerySet containing all the bids that share the listing's ID
            if price <= bid.price:
                messages.error(request, 'Your bid must be greater than highest bid price!')
            else: # Update the Bid instance's bidder, placed, and price properties
                bid.bidder = request.user
                bid.placed = timezone.now()
                bid.price = price
                bid.save()
                messages.success(request, 'Success! You are the highest bidder!')
        except: # If a bid does not exist
            starting = Listing.objects.get(pk=pk)
            if (price <= starting.price):
                messages.error(request, 'Your bid must be greater than the starting price!')
            else: # Create an instance of a Bid
                new = Bid(
                    bidder = request.user,
                    listing = Listing.objects.get(pk=pk),
                    price = request.POST["bid"],
                )
                new.save()
                messages.success(request, 'Success! You are the highest bidder!')
    return HttpResponseRedirect(reverse("listing", args=[pk]))


def status(request, pk): # Update the listing's status
    if request.method == "POST":
        listing = Listing.objects.get(pk=pk)
        listing.status = "Closed"
        listing.save(update_fields=["status"])
        return HttpResponseRedirect(reverse("listing", args=[pk]))


def comment(request, pk):
    if request.method == "POST":
        comment = Comment(
            author = request.user, # Pass in the current user object
            listing = Listing.objects.get(pk=pk), # Pass in the current listing object
            text = request.POST["comment"]
        )
        comment.save()
        return HttpResponseRedirect(reverse("listing", args=[pk]))


condition_choices = (
    ("new", "New"),
    ("excellent", "Excellent"),
    ("verygood", "Very Good"),
    ("good", "Good"),
    ("acceptable", "Acceptable")
)


def create(request):
    if request.method == "POST":
        category=request.POST["category"].upper()
        try: # Check if this category instance exists
            cat = Cat.objects.get(name=category)
            # If so, create the Listing
            l = Listing (
                title=request.POST["title"],
                category=category,
                condition=request.POST["condition"],
                price=request.POST["price"],
                description=request.POST["description"],
                image=request.POST["image"],
                author=request.user
            )
            l.save()
            # Then add the listing instance to the category
            cat.save()
            cat.listing.add(Listing.objects.get(pk=l.pk))
        except: # If this category instance does not exist
            # First, create a listing instance
            l = Listing (
                title=request.POST["title"],
                category=category,
                condition=request.POST["condition"],
                price=request.POST["price"],
                description=request.POST["description"],
                image=request.POST["image"],
                author=request.user
            )
            l.save()
            # Then, use the listing instance to create a new category instance
            new = Cat(name = category)
            new.save()
            new.listing.add(Listing.objects.get(pk=l.pk))
        return HttpResponseRedirect(f"listing/{l.pk}")
    else:
        return render(request, "auctions/create.html")