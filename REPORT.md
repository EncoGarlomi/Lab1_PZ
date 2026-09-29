# Звіт до Lab1_PZ

## 1. Git-репозиторій

Створено окремий локальний репозиторій `Lab1_PZ`.

Використані гілки:

- `main` — основна гілка;
- `feature/tests-docs` — додаткова гілка для тестів і документації.

Гілку `feature/tests-docs` об'єднано з `main` merge-комітом.

Історія комітів:

```text
* e1daeaa Merge tests and documentation branch
|\\
| * 83848e4 Cover card payment revenue
| * eac96a1 Add generated API documentation
| * 1146154 Add unit tests and project instructions
|/
* 9d0aee6 Initial coffee machine project
```

## 2. Юніт-тести

Тести реалізовано у файлі `test_main.py` стандартними засобами Python `unittest`.
Перевіряються:

- витрата какао-бобів без витрати кавових зерен;
- готівкова оплата та розрахунок здачі;
- обмеження місткості запасів;
- інкасація виручки;
- карткова оплата без здачі.

Команда запуску:

```powershell
python -m unittest -v test_main.py
```

Результат:

```text
Ran 5 tests in 0.001s
OK
```

## 3. Автоматична документація

Документацію створено автоматично Python `pydoc` на основі docstring-ів модуля `main.py`.

Згенерований файл:

- `docs/main.html`

Команди генерації:

```powershell
python -m pydoc -w main
Move-Item -Force main.html docs/main.html
```

Інструкція також міститься у `docs/README.md`.
