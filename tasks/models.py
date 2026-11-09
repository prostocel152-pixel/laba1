from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_projects"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Администратор"
        MEMBER = "MEMBER", "Участник"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.MEMBER
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "project"],
                name="unique_user_project"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.project}"


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "TODO", "Нужно сделать"
        PROGRESS = "PROGRESS", "В процессе"
        DONE = "DONE", "Готово"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.TODO
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["project", "status"],
                name="task_project_status_idx"
            )
        ]

    def clean(self):
        super().clean()
        if self.project_id and self.assigned_to_id:
            is_member = Membership.objects.filter(
                project_id=self.project_id,
                user_id=self.assigned_to_id
            ).exists()
            if not is_member:
                raise ValidationError({
                    "assigned_to": "Исполнитель не состоит в проекте"
                })

    def __str__(self):
        return self.title