from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Users
from .serializers import CustomTokenObtainPairSerializer, UserSerializer
from .constants import UserRole
from .documents import document_service, DocumentPermissionChecker
from .services.permission_service import PermissionManager
from .permissions import IsAdmin


class UserCreateView(APIView):
    """Public registration - POST only"""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersListView(APIView):
    """Authenticated users can list users; non-admins see active users only."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != UserRole.ADMIN.value:
            users = Users.objects.filter(is_active=True)
        else:
            users = Users.objects.all()

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk=None):
        if pk is not None and pk != request.user.id:
            if request.user.role != UserRole.ADMIN.value:
                return Response(
                    {"error": "You do not have permission to deactivate this user"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            user = get_object_or_404(Users, pk=pk)
        else:
            user = request.user

        if not user.is_active:
            return Response(
                {"error": "User is already deactivated"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = False
        user.save()

        return Response(
            {"message": f"User {user.email} successfully deactivated"},
            status=status.HTTP_200_OK,
        )


class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk=None):
        if pk is None:
            user = request.user
        else:
            is_admin = request.user.role == UserRole.ADMIN.value
            is_self = request.user.id == pk
            if not (is_self or is_admin):
                return Response(
                    {"error": "You do not have permission to update this user"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            user = get_object_or_404(Users, pk=pk)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT view that uses email instead of username"""

    serializer_class = CustomTokenObtainPairSerializer


class DocumentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        documents = document_service.get_user_documents(request.user)
        return Response(
            {"count": len(documents), "documents": documents},
            status=status.HTTP_200_OK,
        )


class DocumentGetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, doc_id):
        document = document_service.get_document(doc_id)
        if not document:
            return Response(
                {"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if not DocumentPermissionChecker.can_view(request.user, document):
            return Response(
                {"error": "You do not have permission to view this document"},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            {
                "id": document.id,
                "title": document.title,
                "content": document.content,
                "owner_id": document.owner_id,
                "created_at": document.created_at.isoformat(),
            },
            status=status.HTTP_200_OK,
        )


class DocumentUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, doc_id):
        document = document_service.get_document(doc_id)
        if not document:
            return Response(
                {"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if not DocumentPermissionChecker.can_edit(request.user, document):
            return Response(
                {"error": "You do not have permission to edit this document"},
                status=status.HTTP_403_FORBIDDEN,
            )

        title = request.data.get("title")
        content = request.data.get("content")

        updated_doc = document_service.update_document(
            user=request.user, doc_id=doc_id, title=title, content=content
        )

        if updated_doc is None:
            return Response(
                {"error": "Update failed"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(updated_doc, status=status.HTTP_200_OK)


class AdminPermissionListView(APIView):
    """Admin can see all permissions"""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        users = Users.objects.all()
        result = []

        for user in users:
            user_perms = {
                "user_id": user.id,
                "email": user.email,
                "role": user.role,
                "own_documents": [],
                "granted_permissions": [],
            }

            for doc_id, doc in document_service.documents.items():
                if doc.owner_id == user.id:
                    user_perms["own_documents"].append(
                        {"document_id": doc_id, "title": doc.title}
                    )

            extra = PermissionManager.get_user_permissions(user.id)
            for doc_id, perms in extra.items():
                doc = document_service.get_document(doc_id)
                user_perms["granted_permissions"].append(
                    {
                        "document_id": doc_id,
                        "document_title": doc.title if doc else "Unknown",
                        "can_view": perms.get("can_view", False),
                        "can_edit": perms.get("can_edit", False),
                        "can_delete": perms.get("can_delete", False),
                        "granted_by": perms.get("granted_by"),
                        "granted_at": perms.get("granted_at"),
                    }
                )

            result.append(user_perms)

        return Response({"permissions": result})


class AdminGrantPermissionView(APIView):
    """Admin grants permissions to a user"""

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        target_user_id = request.data.get("user_id")
        document_id = request.data.get("document_id")
        can_view = request.data.get("can_view", True)
        can_edit = request.data.get("can_edit", False)
        can_delete = request.data.get("can_delete", False)

        try:
            Users.objects.get(id=target_user_id, is_active=True)
        except Users.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        document = document_service.get_document(document_id)
        if not document:
            return Response({"error": "Document not found"}, status=404)

        result = PermissionManager.grant_permission(
            request.user, target_user_id, document_id, can_view, can_edit, can_delete
        )

        return Response(result, status=status.HTTP_201_CREATED)


class AdminRevokePermissionView(APIView):
    """Admin revokes permissions from a user"""

    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request):
        target_user_id = request.data.get("user_id")
        document_id = request.data.get("document_id")

        result = PermissionManager.revoke_permission(target_user_id, document_id)

        if "error" in result:
            return Response(result, status=404)

        return Response(result, status=status.HTTP_200_OK)
