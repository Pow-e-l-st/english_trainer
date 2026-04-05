"""Формы для работы с карточками, заданиями и ответами."""
from django import forms
from .models import Card, Assignment


class CardForm(forms.ModelForm):
    """Форма создания/редактирования карточки."""
    class Meta:
        model = Card
        fields = ['word', 'translation', 'category']
        widgets = {
            'word': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'apple'}),
            'translation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'яблоко'}),
            'category': forms.TextInput(attrs={'class': 'form-control',
                                               'placeholder': 'Фрукты (необязательно)'}),
        }


class AssignmentForm(forms.ModelForm):
    """Форма создания/редактирования задания."""
    class Meta:
        model = Assignment
        fields = ['name', 'description', 'cards']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cards': forms.SelectMultiple(attrs={'class': 'form-control', 'size': 10}),
        }

    def __init__(self, *args, **kwargs):
        """Ограничиваем выбор карточек только карточками текущего пользователя."""
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['cards'].queryset = Card.objects.filter(created_by=user)


class RandomAssignmentForm(forms.Form):
    """Форма для создания случайного задания."""
    count = forms.IntegerField(
        label="Количество карточек",
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    category = forms.CharField(
        label="Категория (необязательно)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


class AnswerForm(forms.Form):
    """Форма для ввода ответа пользователя."""
    user_answer = forms.CharField(
        label="Ваш перевод",
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите перевод'})
    )