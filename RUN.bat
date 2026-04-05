@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   English Trainer - запуск приложения
echo ========================================
echo.

if not exist "venv\Scripts\activate" (
    echo Виртуальное окружение не найдено. Создаю...
    python -m venv venv
    if errorlevel 1 (
        echo Ошибка: не удалось создать виртуальное окружение. Установите Python.
        pause
        exit /b 1
    )
    echo Виртуальное окружение создано.
)

call venv\Scripts\activate

if exist "requirements.txt" (
    echo Установка зависимостей из requirements.txt...
    pip install -r requirements.txt
)

echo Применение миграций...
python manage.py migrate

python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'english_trainer.settings'); django.setup(); from django.contrib.auth.models import User; exit(0 if User.objects.filter(is_superuser=True).exists() else 1)" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Учётной записи администратора нет, создайте учётную запись.
    echo.
    python manage.py createsuperuser
) else (
    echo.
    set /p create="Уже есть учётная запись администратора. Создать новую? (y/N): "
    if /i "!create!"=="y" (
        echo.
        python manage.py createsuperuser
    )
)

echo.
echo Запуск сервера разработки...
echo Откройте в браузере: http://127.0.0.1:8000
echo Для остановки сервера нажмите Ctrl+C
echo.

python manage.py runserver

pause