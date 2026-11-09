from rest_framework import serializers
from .models import Project, Task, Membership


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id", "name", "description",
            "owner", "created_at"
        ]
        read_only_fields = ["id", "owner", "created_at"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id", "project", "assigned_to",
            "title", "description",
            "status", "created_at"
        ]
        read_only_fields = ["id", "created_at"]

    def validate_title(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError(
                "Название должно содержать минимум 3 символа"
            )
        return value

    def validate(self, attrs):
        if (
            self.instance
            and "project" in attrs
            and attrs["project"].pk != self.instance.project_id
        ):
            raise serializers.ValidationError({
                "project": "Нельзя менять проект задачи"
            })
        project = attrs.get(
            "project",
            self.instance.project if self.instance else None
        )
        assigned_to = attrs.get(
            "assigned_to",
            self.instance.assigned_to if self.instance else None
        )

        if assigned_to and project:
            exists = Membership.objects.filter(
                project=project,
                user=assigned_to
            ).exists()
            if not exists:
                raise serializers.ValidationError({
                    "assigned_to": "Пользователь не участник проекта"
                })

        return attrs

class AddMemberSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1)

class AddMemberSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1)