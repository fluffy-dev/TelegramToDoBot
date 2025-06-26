from django.urls import path, include

from todos.apis import CategoryApi, TaskApi, TaskDetailApi


category_patterns = [
    path('', CategoryApi.as_view(), name='list-create'),
]

task_patterns = [
    path('', TaskApi.as_view(), name='list-create'),
    path('<str:task_id>/', TaskDetailApi.as_view(), name='detail-update-destroy'),
]


urlpatterns = [
    path('categories/', include((category_patterns, 'categories'))),
    path('tasks/', include((task_patterns, 'tasks'))),
]