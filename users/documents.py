from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
from .models import Users


@dataclass
class Document:
    """Mock document"""
    id: int
    title: str
    content: str
    owner_id: int
    created_at: datetime = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now()



MOCK_DOCUMENTS: Dict[int, Document] = {
    1: Document(
        id=1,
        title="Django JWT Setup",
        content="Step by step guide to add JWT authentication...",
        owner_id=2 
    ),
    2: Document(
        id=2,
        title="My Python Notes",
        content="List comprehensions, decorators, generators...",
        owner_id=1  
    ),
    3: Document(
        id=3,
        title="Docker Commands",
        content="docker-compose up --build, docker exec...",
        owner_id=1 
    ),
}


class DocumentPermissionChecker:
    """Simple permission system"""
    
    @staticmethod
    def can_view(user: Users, document: Document) -> bool:
        # Admin can view everything
        if user.role == 'admin':
            return True
        # Users can view only their own documents
        return user.id == document.owner_id
    
    @staticmethod
    def can_edit(user: Users, document: Document) -> bool:
        # Same rules as view
        return DocumentPermissionChecker.can_view(user, document)
    
    @staticmethod
    def can_delete(user: Users, document: Document) -> bool:
        # Only admins can delete
        return user.role == 'admin'


class DocumentService:
    def __init__(self):
        self.documents = MOCK_DOCUMENTS.copy()
    
    def get_user_documents(self, user: Users) -> List[Dict]:
        """Get documents user can see"""
        result = []
        for doc in self.documents.values():
            if DocumentPermissionChecker.can_view(user, doc):
                result.append({
                    "id": doc.id,
                    "title": doc.title,
                    "content": doc.content,
                    "owner_id": doc.owner_id,
                    "created_at": doc.created_at.isoformat()
                })
        return result
    
    def create_document(self, user: Users, title: str, content: str) -> Dict:
        """Create new document"""
        new_id = max(self.documents.keys()) + 1
        new_doc = Document(
            id=new_id,
            title=title,
            content=content,
            owner_id=user.id
        )
        self.documents[new_id] = new_doc
        return {
            "id": new_doc.id,
            "title": new_doc.title,
            "message": "Document created"
        }
    
    def update_document(self, user: Users, doc_id: int, title: str, content: str) -> Dict:
        """Update document if allowed"""
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
        """Delete document if allowed"""
        doc = self.documents.get(doc_id)
        if not doc:
            return False
        
        if not DocumentPermissionChecker.can_delete(user, doc):
            return False
        
        del self.documents[doc_id]
        return True


document_service = DocumentService()