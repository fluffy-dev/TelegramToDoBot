from django.contrib import admin
from todos.models import Category, Task


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for the Category model."""
    list_display = ('id', 'name', 'user', 'created_at')
    search_fields = ('name', 'user__username')
    list_filter = ('user',)
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin configuration for the Task model."""
    list_display = ('id', 'title', 'user', 'due_date', 'is_completed', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    list_filter = ('is_completed', 'user', 'due_date')
    readonly_fields = ('id', 'created_at', 'updated_at')
    filter_horizontal = ('categories',)