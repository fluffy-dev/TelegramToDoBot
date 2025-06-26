from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404

from todos.models import Category, Task
from todos import services, selectors


class CategoryApi(APIView):
    """API for managing categories."""
    permission_classes = (IsAuthenticated,)

    class InputSerializer(serializers.Serializer):
        """Serializer for creating/updating a category."""
        name = serializers.CharField(max_length=100)

    class OutputSerializer(serializers.ModelSerializer):
        """Serializer for displaying a category."""
        class Meta:
            model = Category
            fields = ('id', 'name', 'created_at', 'updated_at')

    def get(self, request):
        """Retrieve a list of categories for the authenticated user."""
        categories = selectors.category_list_for_user(user=request.user)
        data = self.OutputSerializer(categories, many=True).data
        return Response(data)

    def post(self, request):
        """Create a new category for the authenticated user."""
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        category = services.category_create(
            user=request.user, **serializer.validated_data
        )

        data = self.OutputSerializer(category).data
        return Response(data, status=status.HTTP_201_CREATED)


class TaskApi(APIView):
    """API for managing tasks."""
    permission_classes = (IsAuthenticated,)

    class InputSerializer(serializers.Serializer):
        """Serializer for creating/updating a task."""
        title = serializers.CharField(max_length=255)
        description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        # Указываем форматы, которые мы принимаем.
        # '%Y-%m-%dT%H:%M:%S.%fZ' - формат с миллисекундами, который отдает DRF
        # '%Y-%m-%dT%H:%M:%SZ' - формат без миллисекунд
        # '%Y-%m-%d %H:%M' - формат для ввода из диалога бота
        due_date = serializers.DateTimeField(
            input_formats=['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M']
        )
        is_completed = serializers.BooleanField(required=False)
        categories = serializers.PrimaryKeyRelatedField(
            queryset=Category.objects.all(),
            many=True,
            required=False
        )

    class OutputSerializer(serializers.ModelSerializer):
        """Serializer for displaying a task."""
        categories = CategoryApi.OutputSerializer(many=True, read_only=True)

        class Meta:
            model = Task
            fields = (
                'id',
                'title',
                'description',
                'due_date',
                'is_completed',
                'created_at',
                'updated_at',
                'categories'
            )

    def get(self, request):
        """Retrieve a list of tasks for the authenticated user."""
        tasks = selectors.task_list_for_user(user=request.user)
        data = self.OutputSerializer(tasks, many=True).data
        return Response(data)

    def post(self, request):
        """Create a new task for the authenticated user."""
        serializer = self.InputSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        task = services.task_create(
            user=request.user, **serializer.validated_data
        )
        data = self.OutputSerializer(task).data
        return Response(data, status=status.HTTP_201_CREATED)


class TaskDetailApi(APIView):
    """API for a single task."""
    permission_classes = (IsAuthenticated,)

    def get_task(self, user, task_id):
        """Helper to get a task ensuring it belongs to the user."""
        return get_object_or_404(Task, id=task_id, user=user)

    def get(self, request, task_id: str):
        """Retrieve a single task."""
        task = self.get_task(request.user, task_id)
        data = TaskApi.OutputSerializer(task).data
        return Response(data)

    def put(self, request, task_id: str):
        """Update a single task."""
        task = self.get_task(request.user, task_id)
        serializer = TaskApi.InputSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        updated_task = services.task_update(task=task, data=serializer.validated_data)
        data = TaskApi.OutputSerializer(updated_task).data
        return Response(data)

    def delete(self, request, task_id: str):
        """Delete a single task."""
        task = self.get_task(request.user, task_id)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, task_id: str):
        """Partially update a single task."""
        task = self.get_task(request.user, task_id)
        # partial=True говорит сериализатору, что мы обновляем только часть полей
        serializer = TaskApi.InputSerializer(
            instance=task, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        updated_task = services.task_update(task=task, data=serializer.validated_data)
        data = TaskApi.OutputSerializer(updated_task).data
        return Response(data)