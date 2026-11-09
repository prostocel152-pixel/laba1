from django.db import connection
from django.db.models import Count, Q, Prefetch
from django.test.utils import CaptureQueriesContext

from tasks.models import Project, Task


def read_projects(queryset):
    for project in queryset:
        for task in project.tasks.all():
            if task.assigned_to:
                _ = task.assigned_to.username


with CaptureQueriesContext(connection) as before:
    read_projects(Project.objects.all())

optimized = Project.objects.prefetch_related(
    Prefetch(
        "tasks",
        queryset=Task.objects.select_related("assigned_to")
    )
)

with CaptureQueriesContext(connection) as after:
    read_projects(optimized)

print("До оптимизации:", len(before))
print("После оптимизации:", len(after))


projects = Project.objects.annotate(
    total=Count("tasks"),
    todo=Count("tasks", filter=Q(tasks__status="TODO")),
    progress=Count("tasks", filter=Q(tasks__status="PROGRESS")),
    done=Count("tasks", filter=Q(tasks__status="DONE"))
)

for project in projects:
    rate = (
        round(project.done * 100 / project.total, 2)
        if project.total else 0
    )
    print(
        project.name,
        "Всего:", project.total,
        "TODO:", project.todo,
        "PROGRESS:", project.progress,
        "DONE:", project.done,
        "Готовность:", rate, "%"
    )

print("\nEXPLAIN:")
print(
    Task.objects.filter(
        project_id=1,
        status="DONE"
    ).explain()
)