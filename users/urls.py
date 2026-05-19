from django.urls import path
from .views import UsersListCreateView, UserDeleteView, UserUpdateView

urlpatterns = [
    path("users/create/", UsersListCreateView.as_view(), name="create-user"),
    path("users/<int:pk>/update/", UserUpdateView.as_view(), name="user-update"),
    path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="user-delete"),
]
