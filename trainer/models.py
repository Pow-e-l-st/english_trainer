"""Модели данных для приложения trainer."""
from django.db import models
from django.contrib.auth.models import User


class Card(models.Model):
    """Модель карточки: слово, перевод, категория, автор."""
    word = models.CharField(max_length=200, verbose_name="Слово")
    translation = models.CharField(max_length=200, verbose_name="Перевод")
    category = models.CharField(max_length=100, blank=True, verbose_name="Категория")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Создал")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Карточка"
        verbose_name_plural = "Карточки"

    def __str__(self):
        return f"{self.word} → {self.translation}"


class Assignment(models.Model):
    """Модель задания: набор карточек, автор."""
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    cards = models.ManyToManyField(Card, verbose_name="Карточки")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Создал")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Задание"
        verbose_name_plural = "Задания"

    def __str__(self):
        return self.name