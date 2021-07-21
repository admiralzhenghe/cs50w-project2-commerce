from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("inactive", views.inactive, name="inactive"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:c>", views.category, name="category"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:pk>", views.listing, name="listing"), # pk is the Listing id
    path("create", views.create, name="create"),
    path("listing/<int:pk>/comment", views.comment, name="comment"),
    path("listing/<int:pk>/bid", views.bid, name="bid"),
    path("listing/<int:pk>/status", views.status, name="status"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist/<int:pk>", views.add_remove, name="add_remove"),
]