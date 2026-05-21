"""Admin permission grants. Store lives in users.mocks.permissions."""

from datetime import datetime
from typing import Dict

from users.mocks.permissions import EXTRA_PERMISSIONS
from users.models import Users


class PermissionManager:
    """Admin-managed permission grants."""

    @staticmethod
    def get_user_permissions(user_id: int, document_id: int = None) -> Dict:
        if user_id not in EXTRA_PERMISSIONS:
            return {}

        if document_id:
            return EXTRA_PERMISSIONS[user_id].get(document_id, {})

        return EXTRA_PERMISSIONS[user_id]

    @staticmethod
    def grant_permission(
        admin_user: Users,
        target_user_id: int,
        document_id: int,
        can_view: bool = True,
        can_edit: bool = False,
        can_delete: bool = False,
    ) -> Dict:
        if target_user_id not in EXTRA_PERMISSIONS:
            EXTRA_PERMISSIONS[target_user_id] = {}

        if document_id not in EXTRA_PERMISSIONS[target_user_id]:
            EXTRA_PERMISSIONS[target_user_id][document_id] = {}

        EXTRA_PERMISSIONS[target_user_id][document_id]["can_view"] = can_view
        EXTRA_PERMISSIONS[target_user_id][document_id]["can_edit"] = can_edit
        EXTRA_PERMISSIONS[target_user_id][document_id]["can_delete"] = can_delete
        EXTRA_PERMISSIONS[target_user_id][document_id]["granted_by"] = admin_user.id
        EXTRA_PERMISSIONS[target_user_id][document_id][
            "granted_at"
        ] = datetime.now().isoformat()

        return {
            "message": f"Permissions granted for user {target_user_id} on document {document_id}",
            "permissions": EXTRA_PERMISSIONS[target_user_id][document_id],
        }

    @staticmethod
    def revoke_permission(target_user_id: int, document_id: int) -> Dict:
        if (
            target_user_id in EXTRA_PERMISSIONS
            and document_id in EXTRA_PERMISSIONS[target_user_id]
        ):
            del EXTRA_PERMISSIONS[target_user_id][document_id]
            return {
                "message": f"Permissions revoked for user {target_user_id} on document {document_id}"
            }

        return {"error": "No permissions found to revoke"}

    @staticmethod
    def check_extra_permission(user_id: int, document_id: int, action: str) -> bool:
        perms = EXTRA_PERMISSIONS.get(user_id, {}).get(document_id, {})

        if action == "view":
            return perms.get("can_view", False)
        if action == "edit":
            return perms.get("can_edit", False)
        if action == "delete":
            return perms.get("can_delete", False)

        return False
