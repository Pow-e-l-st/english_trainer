"""Настройка административной панели."""
from django.contrib import admin
from .models import Card, Assignment


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    """Отображение карточек в админке."""
    list_display = ('word', 'translation', 'category', 'created_by', 'created_at')
    list_filter = ('category', 'created_by')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """Отображение заданий в админке."""
    list_display = ('name', 'created_by', 'created_at')
    filter_horizontal = ('cards',)