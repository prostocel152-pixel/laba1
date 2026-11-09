from django.contrib.auth import get_user_model
from tasks.models import Task
from tasks.services import create_project

User = get_user_model()
owner = User.objects.get(username="akzhol")

statuses = [
    Task.Status.TODO,
    Task.Status.PROGRESS,
    Task.Status.DONE
]

for i in range(100):
    project = create_project(
        name=f"Учебный проект {i + 1}",
        owner=owner
    )

    tasks = []
    for j in range(10):
        tasks.append(Task(
            project=project,
            assigned_to=owner,
            title=f"Задача {j + 1}",
            status=statuses[j % 3]
        ))

    Task.objects.bulk_create(tasks)

print("Дополнительно создано 100 проектов и 1000 задач")