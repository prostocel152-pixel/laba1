from django.contrib.auth import get_user_model
from tasks.models import Membership, Task
from tasks.services import create_project, create_task

User = get_user_model()

akzhol = User.objects.create_user(
    username="akzhol", password="DemoPass12345!"
)
emir = User.objects.create_user(
    username="emir", password="DemoPass12345!"
)
bekzat = User.objects.create_user(
    username="bekzat", password="DemoPass12345!"
)

p1 = create_project(
    name="Интернет-магазин",
    owner=akzhol
)
p2 = create_project(
    name="Мобильное приложение",
    owner=emir
)

Membership.objects.create(
    user=bekzat,
    project=p1,
    role=Membership.Role.MEMBER
)
Membership.objects.create(
    user=bekzat,
    project=p2,
    role=Membership.Role.MEMBER
)

for i in range(1, 6):
    create_task(
        project=p1,
        assigned_to=bekzat,
        title=f"Задача магазина {i}"
    )
    create_task(
        project=p2,
        assigned_to=bekzat,
        title=f"Задача приложения {i}"
    )

print("Созданы 3 пользователя, 2 проекта, 10 задач")