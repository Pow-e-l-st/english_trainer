"""Основная логика приложения (контроллеры)."""
import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Card, Assignment
from .forms import CardForm, AssignmentForm, RandomAssignmentForm, AnswerForm


def get_user_categories(user):
    """Возвращает список непустых категорий карточек пользователя."""
    categories = Card.objects.filter(created_by=user).values_list('category', flat=True).distinct()
    return [c for c in categories if c]


def home(request):
    """Главная страница: перенаправляет авторизованных на задания, иначе на логин."""
    if request.user.is_authenticated:
        return redirect('assignment_list')
    return redirect('login')


@login_required
def card_list(request):
    """Страница со списком карточек пользователя."""
    cards = Card.objects.filter(created_by=request.user).order_by('word')
    return render(request, 'cards/card_list.html', {'cards': cards})


@login_required
def card_create(request):
    """Создание новой карточки."""
    categories = get_user_categories(request.user)
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.created_by = request.user
            card.save()
            messages.success(request, "Карточка добавлена!")
            return redirect('card_list')
    else:
        form = CardForm()
    return render(request, 'cards/card_form.html', {
        'form': form,
        'title': 'Добавить карточку',
        'categories': categories
    })


@login_required
def card_edit(request, pk):
    """Редактирование существующей карточки."""
    card = get_object_or_404(Card, pk=pk, created_by=request.user)
    categories = get_user_categories(request.user)
    if request.method == 'POST':
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            messages.success(request, "Карточка обновлена!")
            return redirect('card_list')
    else:
        form = CardForm(instance=card)
    return render(request, 'cards/card_form.html', {
        'form': form,
        'title': 'Редактировать карточку',
        'categories': categories
    })


@login_required
def card_delete(request, pk):
    """Удаление карточки с подтверждением."""
    card = get_object_or_404(Card, pk=pk, created_by=request.user)
    if request.method == 'POST':
        card.delete()
        messages.success(request, "Карточка удалена!")
        return redirect('card_list')
    return render(request, 'cards/card_confirm_delete.html', {'card': card})


@login_required
def assignment_list(request):
    """Страница со списком заданий пользователя."""
    assignments = Assignment.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'assignments/assignment_list.html', {'assignments': assignments})


@login_required
def assignment_create(request):
    """Создание нового задания с возможностью фильтрации карточек по категории."""
    user_cards = Card.objects.filter(created_by=request.user)
    categories = get_user_categories(request.user)

    category_filter = request.GET.get('cat', '')
    name_value = request.GET.get('name', '')
    description_value = request.GET.get('description', '')
    selected_cards_ids = request.GET.getlist('cards', [])

    cards_queryset = user_cards
    if category_filter:
        cards_queryset = cards_queryset.filter(category=category_filter)

    if request.method == 'POST':
        form = AssignmentForm(request.POST, user=request.user)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            form.save_m2m()
            messages.success(request, "Задание создано!")
            return redirect('assignment_list')
    else:
        initial_data = {}
        if name_value:
            initial_data['name'] = name_value
        if description_value:
            initial_data['description'] = description_value
        if selected_cards_ids:
            initial_data['cards'] = [int(cid) for cid in selected_cards_ids]
        form = AssignmentForm(initial=initial_data, user=request.user)

    return render(request, 'assignments/assignment_form.html', {
        'form': form,
        'title': 'Создать задание',
        'categories': categories,
        'category_filter': category_filter,
        'cards': cards_queryset,
        'name_value': name_value,
        'description_value': description_value,
        'selected_cards_ids': selected_cards_ids,
    })


@login_required
def assignment_edit(request, pk):
    """Редактирование существующего задания."""
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    categories = get_user_categories(request.user)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Задание обновлено!")
            return redirect('assignment_list')
    else:
        form = AssignmentForm(instance=assignment, user=request.user)
    return render(request, 'assignments/assignment_form.html', {
        'form': form,
        'title': 'Редактировать задание',
        'categories': categories,
    })


@login_required
def assignment_delete(request, pk):
    """Удаление задания с подтверждением."""
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, "Задание удалено!")
        return redirect('assignment_list')
    return render(request, 'assignments/assignment_confirm_delete.html', {'assignment': assignment})


@login_required
def practice_assignment(request, pk, direction='en-ru'):
    """Запуск тренировки по выбранному заданию."""
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    card_ids = list(assignment.cards.values_list('id', flat=True))
    if not card_ids:
        messages.warning(request, "В задании нет карточек. Добавьте карточки.")
        return redirect('assignment_list')
    return _practice_cards(request, card_ids, direction, assignment.name)


@login_required
def practice_random(request):
    """Форма для создания случайного задания."""
    categories = get_user_categories(request.user)
    if request.method == 'POST':
        form = RandomAssignmentForm(request.POST)
        if form.is_valid():
            count = form.cleaned_data['count']
            category = form.cleaned_data['category']
            queryset = Card.objects.filter(created_by=request.user)
            if category:
                queryset = queryset.filter(category=category)
            cards = list(queryset)
            if len(cards) < count:
                messages.error(request, f"Недостаточно карточек. Доступно: {len(cards)}")
                return redirect('random_assignment')
            selected = random.sample(cards, count)
            card_ids = [c.id for c in selected]
            request.session['random_card_ids'] = card_ids
            return redirect('practice_random_session')
    else:
        form = RandomAssignmentForm()
    return render(request, 'random_assignment.html', {'form': form, 'categories': categories})


@login_required
def practice_random_session(request):
    """Обработчик случайного задания – чтение ID карточек из сессии."""
    card_ids = request.session.get('random_card_ids')
    if not card_ids:
        messages.warning(request, "Сначала создайте случайное задание.")
        return redirect('random_assignment')
    direction = request.GET.get('direction', 'en-ru')
    return _practice_cards(request, card_ids, direction, "Случайное задание")


def _practice_cards(request, card_ids, direction, title):
    """Вспомогательная функция для прохождения набора карточек."""
    # Инициализация сессии
    if ('practice_index' not in request.session or
            request.session.get('practice_card_ids') != card_ids):
        request.session['practice_card_ids'] = card_ids
        request.session['practice_index'] = 0
        request.session['practice_correct'] = 0
        request.session['practice_total'] = len(card_ids)

    index = request.session['practice_index']
    total = request.session['practice_total']
    correct = request.session['practice_correct']
    current_card_ids = request.session['practice_card_ids']

    if index >= total:
        # Завершение тренировки
        score = correct
        for key in ['practice_index', 'practice_card_ids', 'practice_correct', 'practice_total']:
            if key in request.session:
                del request.session[key]
        context = {'score': score, 'total': total, 'title': title}
        return render(request, 'assignments/practice_result.html', context)

    card = get_object_or_404(Card, id=current_card_ids[index])
    if direction == 'en-ru':
        prompt = card.word
        correct_answer = card.translation
    else:
        prompt = card.translation
        correct_answer = card.word

    form = AnswerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user_answer = form.cleaned_data['user_answer'].strip().lower()
        if user_answer == correct_answer.lower():
            request.session['practice_correct'] += 1
            messages.success(request, "✅ Верно!")
        else:
            messages.error(request, f"❌ Неверно. Правильно: {correct_answer}")
        request.session['practice_index'] += 1
        return redirect(request.path + f'?direction={direction}')

    context = {
        'prompt': prompt,
        'direction': direction,
        'form': form,
        'title': title,
        'current': index + 1,
        'total': total,
    }
    return render(request, 'assignments/practice.html', context)


class SignUpView(CreateView):
    """Представление для регистрации нового пользователя."""
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')