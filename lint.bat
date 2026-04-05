@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   Запуск pylint для English Trainer
echo ========================================
echo.

if not exist "venv\Scripts\activate" (
    echo Ошибка: виртуальное окружение не найдено.
    echo Создайте его командой: python -m venv venv
    pause
    exit /b 1
)

call venv\Scripts\activate

pip show pylint >nul 2>&1
if errorlevel 1 (
    echo pylint не установлен.
    echo Установите его командой: pip install pylint pylint-django
    pause
    exit /b 1
)

echo Запуск анализа кода...
echo.

pylint --load-plugins=pylint_django trainer english_trainer manage.py --rcfile=trainer/.pylintrc.ini

echo.
echo Анализ завершён. Нажмите любую клавишу для выхода...
pause >nul