
from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Membership


def is_project_admin(user, project):
    if not user or not user.is_authenticated:
        return False

    return (
        project.owner_id == user.id
        or Membership.objects.filter(
            user=user,
            project=project,
            role=Membership.Role.ADMIN
        ).exists()
    )


class TaskPermission(BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if is_project_admin(request.user, obj.project):
            return True

        if request.method == "PATCH":
            return (
                obj.assigned_to_id == request.user.id
                and set(request.data.keys()) == {"status"}
            )

        return False
