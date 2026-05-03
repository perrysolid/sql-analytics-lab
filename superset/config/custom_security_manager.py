"""
Custom Security Manager for Option 2 — Dataset Admin Permissions.

Overrides the default ownership check so that users with `can_write Dataset`
permission can edit/delete ANY dataset, not just datasets they own.

This applies ONLY to Dataset objects. Dashboard and Chart ownership checks
remain unchanged (ownership-scoped as in Option 1).
"""
import logging

from flask import g
from flask_appbuilder.models.sqla import Model
from superset.security.manager import SupersetSecurityManager

logger = logging.getLogger(__name__)


class CustomSecurityManager(SupersetSecurityManager):

    def raise_for_ownership(self, resource: Model) -> None:
        """
        Override ownership check to allow dataset-admin access.

        For Dataset (SqlaTable) objects:
          - If the user has the OPT2_Sublime_UserMgmt role, skip the ownership check.
          - This gives them admin-like edit/delete on ALL datasets.

        For all other objects (Dashboard, Chart, etc.):
          - Fall through to the default ownership check (unchanged behavior).
        """
        # Admins always pass (preserve default behavior)
        if self.is_admin():
            return

        # Check if resource is a Dataset (SqlaTable)
        resource_class_name = resource.__class__.__name__
        if resource_class_name == "SqlaTable":
            # Check if user has the OPT2_Sublime_UserMgmt role
            user_roles = [role.name for role in self.get_user_roles()]
            if "OPT2_Sublime_UserMgmt" in user_roles:
                logger.info(
                    "CustomSecurityManager: Allowing dataset admin access for user "
                    "'%s' (role OPT2_Sublime_UserMgmt) on dataset ID=%s",
                    g.user.username if hasattr(g, "user") and g.user else "unknown",
                    resource.id if hasattr(resource, "id") else "?",
                )
                return

        # For everything else, use the default ownership check
        super().raise_for_ownership(resource)
