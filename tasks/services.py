
from django.db import transaction
from .models import Project, Membership, Task
from django.contrib.auth import get_user_model
from .models import Project, Membership, Task

@transaction.atomic
def create_project(*, name, owner, description=""):
    project = Project.objects.create(
        name=name,
        owner=owner,
        description=description
    )

    Membership.objects.create(
        user=owner,
        project=project,
        role=Membership.Role.ADMIN
    )

    return project


def create_task(*, project, assigned_to, title,
                description="", status=Task.Status.TODO):
    task = Task(
        project=project,
        assigned_to=assigned_to,
        title=title,
        description=description,
        status=status
    )

    task.full_clean()
    task.save()

    return task

@transaction.atomic
def transfer_project_ownership(project_id, new_owner_id):
    User = get_user_model()

    new_owner = User.objects.get(pk=new_owner_id)

    project = Project.objects.select_for_update().get(
        pk=project_id
    )

    old_owner_id = project.owner_id

    if old_owner_id == new_owner_id:
        return project

   
    list(
        Membership.objects.select_for_update()
        .filter(project=project)
        .order_by("pk")
    )

    Membership.objects.update_or_create(
        user=new_owner,
        project=project,
        defaults={"role": Membership.Role.ADMIN}
    )

    Membership.objects.filter(
        user_id=old_owner_id,
        project=project
    ).update(role=Membership.Role.MEMBER)

    project.owner = new_owner
    project.save(update_fields=["owner"])

    return project