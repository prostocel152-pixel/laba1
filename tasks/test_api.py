from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Membership, Task
from .services import create_project, create_task


class TaskAPITests(APITestCase):
    def setUp(self):
        User = get_user_model()

        self.owner = User.objects.create_user(
            username="owner", password="test12345"
        )
        self.member = User.objects.create_user(
            username="member", password="test12345"
        )
        self.outsider = User.objects.create_user(
            username="outsider", password="test12345"
        )

        self.project = create_project(
            name="Тестовый проект", owner=self.owner
        )

        Membership.objects.create(
            user=self.member,
            project=self.project,
            role=Membership.Role.MEMBER
        )

        self.task = create_task(
            project=self.project,
            assigned_to=self.member,
            title="Первая задача"
        )

    def test_create_task(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post("/api/tasks/", {
            "project": self.project.id,
            "assigned_to": self.member.id,
            "title": "Новая задача"
        })
        self.assertEqual(response.status_code, 201)

    def test_short_title(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post("/api/tasks/", {
            "project": self.project.id,
            "title": "АБ"
        })
        self.assertEqual(response.status_code, 400)

    def test_stats(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(
            f"/api/projects/{self.project.id}/stats/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total"], 1)

    def test_filter_tasks(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get("/api/tasks/?status=TODO")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_member_cannot_delete(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.delete(
            f"/api/tasks/{self.task.id}/"
        )
        self.assertEqual(response.status_code, 403)

    def test_member_can_update_own_status(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.patch(
            f"/api/tasks/{self.task.id}/",
            {"status": "DONE"}
        )
        self.assertEqual(response.status_code, 200)

    def test_outsider_cannot_view(self):
        self.client.force_authenticate(user=self.outsider)
        response = self.client.get(
            f"/api/tasks/{self.task.id}/"
        )
        self.assertEqual(response.status_code, 404)

    def test_anonymous_cannot_view(self):
        response = self.client.get("/api/tasks/")
        self.assertIn(response.status_code, (401, 403))