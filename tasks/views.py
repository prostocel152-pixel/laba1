
from django.db import transaction
from django.db.models import Count, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from .permissions import TaskPermission, is_project_admin
from .models import Project, Task, Membership
from .serializers import ProjectSerializer, TaskSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from .serializers import AddMemberSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)

        Membership.objects.create(
            project=project,
            user=self.request.user,
            role=Membership.Role.ADMIN
        )

    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        project = self.get_object()

        result = project.tasks.aggregate(
            total=Count("id"),
            todo=Count("id", filter=Q(status="TODO")),
            progress=Count("id", filter=Q(status="PROGRESS")),
            done=Count("id", filter=Q(status="DONE"))
        )

        result["completion_rate"] = (
            round(result["done"] * 100 / result["total"], 2)
            if result["total"] else 0
        )

        return Response(result)
    
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Project.objects.none()

        return Project.objects.filter(
            Q(owner=user) |
            Q(memberships__user=user)
        ).distinct()

    @action(detail=True, methods=["post"])
    def members(self, request, pk=None):
        project = self.get_object()

        is_admin = (
            project.owner_id == request.user.id
            or Membership.objects.filter(
                project=project,
                user=request.user,
                role=Membership.Role.ADMIN
            ).exists()
        )

        if not is_admin:
            raise PermissionDenied(
                "Только администратор может добавлять участников"
            )

        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(
            get_user_model(),
            pk=serializer.validated_data["user_id"]
        )

        membership, created = Membership.objects.get_or_create(
            project=project,
            user=user,
            defaults={"role": Membership.Role.MEMBER}
        )

        return Response(
            {
                "id": membership.id,
                "user": user.username,
                "role": membership.role
            },
            status=(
                status.HTTP_201_CREATED
                if created else status.HTTP_200_OK
            )
        )

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [TaskPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "status",
        "project",
        "assigned_to"

    ]
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()

        return Task.objects.filter(
            Q(project__owner=user) |
            Q(project__memberships__user=user)
        ).distinct().select_related(
            "project", "assigned_to"
        )


    def perform_create(self, serializer):
        project = serializer.validated_data["project"]
        if not is_project_admin(self.request.user, project):
            raise PermissionDenied(
                "Нет права создавать задачи в этом проекте"
            )
        serializer.save()
