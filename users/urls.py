from django.urls import path

from .views import (
    UserCreateView,
    UsersListView,
    UserDeleteView,
    UserUpdateView,
    DocumentListView,
    DocumentGetView,
    DocumentUpdateView,
    AdminPermissionListView,
    AdminGrantPermissionView,
    AdminRevokePermissionView,
)

urlpatterns = [
    path("users/create/", UserCreateView.as_view(), name="create-user"),
    path("users/", UsersListView.as_view(), name="list-users"),
    path("users/<int:pk>/update/", UserUpdateView.as_view(), name="user-update"),
    path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="user-delete"),
    path("documents/", DocumentListView.as_view(), name="document-list"),
    path("documents/<int:doc_id>/", DocumentGetView.as_view(), name="document-get"),
    path(
        "documents/<int:doc_id>/update/",
        DocumentUpdateView.as_view(),
        name="document-update",
    ),
    path(
        "admin/permissions/",
        AdminPermissionListView.as_view(),
        name="admin-permissions",
    ),
    path(
        "admin/permissions/grant/",
        AdminGrantPermissionView.as_view(),
        name="admin-grant-permission",
    ),
    path(
        "admin/permissions/revoke/",
        AdminRevokePermissionView.as_view(),
        name="admin-revoke-permission",
    ),
]
