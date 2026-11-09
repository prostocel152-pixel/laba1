from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Project, Membership, Task


class ModelTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="owner", password="testpass123"
        )
        self.outsider = User.objects.create_user(
            username="outsider", password="testpass123"
        )
        self.project = Project.objects.create(
            name="Тестовый проект",
            owner=self.owner
        )

    def test_duplicate_membership(self):
        Membership.objects.create(
            user=self.owner,
            project=self.project,
            role=Membership.Role.ADMIN
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Membership.objects.create(
                    user=self.owner,
                    project=self.project,
                    role=Membership.Role.ADMIN
                )

    def test_outsider_cannot_be_assigned(self):
        task = Task(
            project=self.project,
            assigned_to=self.outsider,
            title="Тестовая задача"
        )
        with self.assertRaises(ValidationError):
            task.full_clean()