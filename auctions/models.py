from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass


class Listing(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    condition = models.CharField(max_length=255, default=None)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    image = models.CharField(max_length=255, blank=True)
    author = models.ForeignKey(User, default=None, on_delete=models.CASCADE) # blank = False means the field cannot be blank
    created = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=255, default="Active")

    def __str__(self):
        return "#{}: listing for {}".format(self.id, self.title)


class Cat(models.Model):
    name = models.CharField(max_length=255)
    listing = models.ManyToManyField(Listing)

    class Meta:
        verbose_name_plural="categories"

    def __str__(self):
        return self.name


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    placed = models.DateTimeField(default=timezone.now)
    listing = models.ForeignKey(Listing, related_name="bids", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"{self.bidder.username} bid ${self.price} on {self.listing.title}"


class Watchlist(models.Model):
    watcher = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    listing = models.ManyToManyField(Listing)

    def __str__(self):
        return f"#{self.id}: watchlist for {self.watcher}"


class Comment(models.Model):
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(default=timezone.now)
    listing = models.ForeignKey(Listing, related_name="comments", null=True, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return "#{}: comment for {}".format(self.id, self.listing.title)