"""Document access rules and service. Mock data lives in users.mocks.documents."""

from typing import Dict, List

from users.mocks.documents import Document, MOCK_DOCUMENTS
from users.models import Users
from users.services.permission_service import PermissionManager

from .constants import UserRole


class DocumentPermissionChecker:
    @staticmethod
    def can_view(user: Users, document: Document) -> bool:
        if PermissionManager.check_extra_permission(user.id, document.id, "view"):
            return True
        if user.role == UserRole.ADMIN.value:
            return True
        return user.id == document.owner_id

    @staticmethod
    def can_edit(user: Users, document: Document) -> bool:
        if PermissionManager.check_extra_permission(user.id, document.id, "edit"):
            return True
        if user.role == UserRole.ADMIN.value:
            return True
        return user.id == document.owner_id

    @staticmethod
    def can_delete(user: Users, document: Document) -> bool:
        if PermissionManager.check_extra_permission(user.id, document.id, "delete"):
            return True
        return user.role == UserRole.ADMIN.value


class DocumentService:
    def __init__(self):
        self.documents = MOCK_DOCUMENTS.copy()

    def get_user_documents(self, user: Users) -> List[Dict]:
        result = []
        for doc in self.documents.values():
            if DocumentPermissionChecker.can_view(user, doc):
                result.append(
                    {
                        "id": doc.id,
                        "title": doc.title,
                        "content": doc.content,
                        "owner_id": doc.owner_id,
                        "created_at": doc.created_at.isoformat(),
                    }
                )
        return result

    def create_document(self, user: Users, title: str, content: str) -> Dict:
        new_id = max(self.documents.keys()) + 1
        new_doc = Document(id=new_id, title=title, content=content, owner_id=user.id)
        self.documents[new_id] = new_doc
        return {"id": new_doc.id, "title": new_doc.title, "message": "Document created"}

    def get_document(self, doc_id: int) -> Document:
        return self.documents.get(doc_id)

    def update_document(
        self, user: Users, doc_id: int, title: str, content: str
    ) -> Dict:
        doc = self.documents.get(doc_id)
        if not doc:
            return None

        if not DocumentPermissionChecker.can_edit(user, doc):
            return None

        if title:
            doc.title = title
        if content:
            doc.content = content

        return {"message": "Document updated"}

    def delete_document(self, user: Users, doc_id: int) -> bool:
        doc = self.documents.get(doc_id)
        if not doc:
            return False

        if not DocumentPermissionChecker.can_delete(user, doc):
            return False

        del self.documents[doc_id]
        return True


document_service = DocumentService()
