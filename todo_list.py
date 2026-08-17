# import sys здесь нужен для вызова функции sys.exit() в пункте меню «0 — Выход».
import sys
# Подклюаем модуль для взаимодействия с операционной системой - файлами, папками и др.
import os
# Подключаем модуль для работы с форматом JSON (JavaScript Object Notation)
import json
# Подключаем модуль для сохранения формата csv
import csv
# Импорт модуля для задержки перед выходом
import time
# Импортируем класс datetime из модуля datetime для работы с датами и временем
from datetime import datetime

def load_tasks():
    """
    Загрузка списка задач
    """
    # Если файла нет - возвращается пустой список
    if not os.path.exists(tasks_file_name):
        return []
    # Т.к. в проверяемом условии выше есть return, при отсутствии файла код ниже не выполняется.

    # Дополнительная функция проверки сделанная ИИ по заданию
    handle_json_file("read")
    # Пробуем прочитать файл:
    try:
        # Открытие файла в режиме чтения "r" с кодировкой utf-8
        # (Присвоение открытого файлового объекта переменной f):
        # (При использовании with файл автоматически  закрывается после выхода из блока (даже при ошибке)
        with open(tasks_file_name, "r", encoding="utf-8") as f:
            # Загрузка (чтение) содержимого файла (читает и парсит JSON)
            data = json.load(f)

            # Дополнительная проверка типа
            if not isinstance(data, list):
                print("Ошибка: формат tasks.json некорректен.")
                return []

            return data
    except json.JSONDecodeError:
        print("Ошибка чтения JSON")
        return []

def save_tasks(tasks_list):
    """
    Запись списка задач
    """
    # Механизм №1 — основное сохранение (проверка ИИ)
    # Вызов функции, написанной ChatGPT по заданию
    result = handle_json_file("write", tasks_list)

    if result:
        print("Данные успешно сохранены.")
        return True

    # Механизм №2 — резервное сохранение - ранее написанное
    print("Основное сохранение не удалось - скрипт, разработанный ИИ выявил ошибку.")

    try:
        backup_file = "tasks_backup.json"
        # Открытие файла в режиме записи "w" с кодировкой utf-8
        # (Присвоение открытого файлового объекта переменной f):
        # (При использовании with файл автоматически  закрывается после выхода из блока (даже при ошибке)
        # Данная команда преобразует объект в JSON-строку и записывает её в файл f)
        # tasks_list - сохраняемый объект
        # ident=4 - форматирование JSON - 4 отступа на каждый уровень вложенности
        # (без этого параметра запишет в одну строку)
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(
                tasks_list,
                f,
                indent=4,
                ensure_ascii=False
            )
        print(f"Данные сохранены в резервный файл {backup_file}.")
        return True
    except (PermissionError, OSError) as error:
        print(f"Ошибка резервного сохранения: {error}")
        return False
        
def add_task(
    task_name,
    task_description="",
    task_target_date=None,
    task_priority="низкий",
    task_completed=False,
    task_completed_date=None
):
    """
    Добавление новой задачи.
    Параметры:
        - task_name: название задачи
        - task_description: описание задачи
        - task_target_date: срок выполнения задачи
        - task_priority: приоритет задачи
    """
    # Определяем требуеый по порядку номер ID
    # Находится самая большая цифра среди существующих ID и к ней прибавляется 1
    # ([task["id"] for task in tasks_list - списковое включение
    # - проходит по списку словарей tasks_list и собирает все значения по ключу "id" в отдельный список)
    # default=0 - параметр на случай, если список tasks_list пуст - не будет ошибки просто вернётся 0

    tasks_list = load_tasks()
    
    task_id = max(
        [task.get("id", 0) for task in tasks_list],
        default=0
    ) + 1

    # Создаётся словарь задачи
    task_new = {
        "id": task_id,
        "name": task_name,
        "description": task_description,
        "target_date": task_target_date,
        "priority": task_priority,
        "completed": task_completed,
        "completed_date": task_completed_date,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    tasks_list.append(task_new)
    
    if save_tasks(tasks_list):
        print(f"Задача {task_id} добавлена ({task_name})")
    else:
        print(f"Ошибка: задача {task_id} не была сохранена.")

    
def filter_tasks(tasks_status_filter=None, tasks_priority_filter=None):
    """
    Показывает список задач в соответствии с параметрами фильтра
    Варианты фильтрации: "Все", active - , completed - 
    tasks_status_filter:
        None       - "Все задачи"
        "active"   - "Только активные"
        "completed" - "Только выполненные"
    priority:
        None       - "Любой приоритет"
        "высокий"
        "средний"
        "низкий"
    По умолчанию "None" - нет установленного фильтра.
    """
    # Загрузка актуального списка задач
    tasks_list = load_tasks()

    # Обработка случая, если список задач окажется пустым
    # Если список пустой - передаётся значение False
    if not tasks_list:
        print(f"Список задач пуст")
        return
        
    # Производится проверка по статусус completed (булево поле) - завершена задача или нет, False или True
    if tasks_status_filter == "active":
        tasks_list = [task for task in tasks_list if not task.get("completed", False)]
    elif tasks_status_filter == "completed":
        tasks_list = [task for task in tasks_list if task.get("completed", False)]
    # Если фильтр не найден, а задачи есть - следовательно, сохранённым остаётся третий вариант - Все задачи

    # Фильтрация по приоритету
    if tasks_priority_filter is not None:
        tasks_list = [
            task for task in tasks_list
            if task.get("priority") == tasks_priority_filter
        ]
        
    # Если фильтр применён и задач не найдено по такому фильтру
    if not tasks_list:
        print(f"Нет задач с такими параметрами")
        return

    # Если задачи найдены - выводим их
    for task in tasks_list:
        print(
            f"\n#{task.get('id', '?')} | "
            f"{task.get('name', 'Без названия')} | "
            f"Приоритет: {task.get('priority', '?')} | "
            f"Дата: {task.get('target_date', '?')}"
        )
        
        if task.get("description"):
            print(f"{task['description']}")
        print(f"Создана: {task.get('created_at','незвестно')}")
    # Разделитель после списка
    print("\n" + "-" * 40)

def sort_tasks(sort_by="deadline"):
    """
    Сортирует задачи при просмотре.

    sort_by:
        "deadline" - по сроку выполнения
        "priority" - по приоритету
        "status"   - активные перед выполненными
    """

    tasks_list = load_tasks()

    if not tasks_list:
        print("Список задач пуст")
        return

    # Сортировка по сроку выполнения
    if sort_by == "deadline":
        # Задачи без срока выполнения отправляем в конец
        tasks_list.sort(
            key=lambda task: (
                task.get("target_date") is None,
                datetime.strptime(task["target_date"], "%d.%m.%Y")
                if task.get("target_date")
                else datetime.max
            )
        )
    # Сортировка по приоритету:
    # высокий -> средний -> низкий
    elif sort_by == "priority":
        priority_order = {
            "высокий": 1,
            "средний": 2,
            "низкий": 3
        }

        tasks_list.sort(
            key=lambda task: priority_order.get(
                task.get("priority"), 99
            )
        )
    # Сортировка по статусу:
    # активные -> выполненные
    elif sort_by == "status":
        tasks_list.sort(
            key=lambda task: task.get("completed", False)
        )

    else:
        print("Неизвестный вариант сортировки")
        return
    # Вывод отсортированного списка
    for task in tasks_list:
        status = "Выполнена" if task.get("completed", False) else "Активна"

        print(
            f"\n#{task.get('id', '?')} | "
            f"{task.get('name', 'Без названия')} | "
            f"Приоритет: {task.get('priority', '?')} | "
            f"Срок: {task.get('target_date') or 'не указан'} | "
            f"Статус: {status}"
        )

        if task.get("description"):
            print(f"Описание: {task['description']}")
    print("\n" + "-" * 50)
    
    
def change_task_status(task_id):
    """
    Отмечает задачу с указанным ID как выполненную.
    Добавляет временную метку завершения.
    """
    tasks_list = load_tasks()
     
    for task in tasks_list:
        if task.get("id") == task_id:
            if task.get("completed", False):
                print(f"Задача #{task_id} уже выполнена ранее.")
                return
             
            task["completed"] = True
            task["completed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if save_tasks(tasks_list):
                print(f"Задача #{task_id} «{task['name']}» выполнена.")
            else:
                print(f"Ошибка: изменения задачи #{task_id} не удалось сохранить.")
            return
     
    print(f"Задача с ID {task_id} не найдена.")
    

def delete_task(task_id):
    """
    Удаляет задачу с указанным ID из списка.
    """
    tasks_list = load_tasks()
    initial_count = len(tasks_list)

    # Ищем задачу, чтобы показать её название
    task_to_delete = None
    for task in tasks_list:
        if task.get("id") == task_id:
            task_to_delete = task
            break
    
    if not task_to_delete:
        print(f"Задача с ID {task_id} не найдена.")
        return        
    # Показываем информацию о задаче если она найдена
    print(f"Вы собираетесь удалить задачу:")
    print(f"  #{task_to_delete['id']} | {task_to_delete.get('name', 'Без названия')}")    
    # Запрашиваем подтверждение
    confirm = input("Удалить? (y/n): ").strip().lower()
    if confirm != 'y' and confirm != 'yes':
        print("Удаление отменено.")
        return

    # Вызываем дополнительную отдельную функцию подтверждения ИИ
    if not confirm_deletion(
        f"#{task_to_delete['id']} | "
        f"{task_to_delete.get('name', 'Без названия')}"
    ):
        print("Не пройдена проверка ИИ. Удаление отменено.")
        return        
    # Создаём новый список без удаляемой задачи
    tasks_list = [task for task in tasks_list if task.get("id") != task_id]
     
    # Проверяем, изменилась ли длина списка
    if len(tasks_list) < initial_count:
        if save_tasks(tasks_list):
            print(f"Задача #{task_id} успешно удалена.")
        else:
            print(f"Ошибка: удаление задачи #{task_id} не удалось сохранить.")
    else:
        print(f"Задача с ID {task_id} не найдена.")


def export_tasks(file_format):
    """
    Экспортирует список задач в TXT или CSV файл.

    file_format:
        "txt" - текстовый файл
        "csv" - CSV-файл
    """
    tasks_list = load_tasks()

    if not tasks_list:
        print("Список задач пуст. Экспортировать нечего.")
        return

    # Экспорт в TXT
    if file_format == "txt":
        file_name = "tasks.txt"

        with open(file_name, "w", encoding="utf-8") as f:
            for task in tasks_list:
                status = "Выполнена" if task.get("completed", False) else "Активна"

                f.write(f"ID: {task.get('id', '?')}\n")
                f.write(f"Название: {task.get('name', 'Без названия')}\n")
                f.write(f"Описание: {task.get('description', '')}\n")
                f.write(f"Срок выполнения: {task.get('target_date') or 'Не указан'}\n")
                f.write(f"Приоритет: {task.get('priority', 'Не указан')}\n")
                f.write(f"Статус: {status}\n")
                f.write(f"Дата выполнения: {task.get('completed_date') or 'Не выполнена'}\n")
                f.write("-" * 50 + "\n")

        print(f"Задачи успешно экспортированы в файл {file_name}")

    # Экспорт в CSV
    elif file_format == "csv":
        file_name = "tasks.csv"

        with open(file_name, "w", encoding="utf-8-sig", newline="") as f:
            fieldnames = [
                "id",
                "name",
                "description",
                "target_date",
                "priority",
                "completed",
                "completed_date"
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)

            # Записываем заголовки таблицы
            writer.writeheader()

            # Записываем задачи
            for task in tasks_list:
                writer.writerow({
                    "id": task.get("id", ""),
                    "name": task.get("name", ""),
                    "description": task.get("description", ""),
                    "target_date": task.get("target_date", ""),
                    "priority": task.get("priority", ""),
                    "completed": "Да" if task.get("completed", False) else "Нет",
                    "completed_date": task.get("completed_date", "")
                })

        print(f"Задачи успешно экспортированы в файл {file_name}")
    else:
        print("Ошибка: неизвестный формат файла.")
        
        
def search_tasks(keyword):
    """
    Поиск задач по ключевому слову в названии.
    Поиск не зависит от регистра букв.
    """

    tasks_list = load_tasks()

    if not tasks_list:
        print("Список задач пуст.")
        return

    # Убираем лишние пробелы
    keyword = keyword.strip()

    if not keyword:
        print("Ключевое слово не может быть пустым!")
        return

    # Ищем ключевое слово в названии задачи
    found_tasks = [
        task for task in tasks_list
        if keyword.lower() in task.get("name", "").lower()
    ]
    # Если ничего не найдено
    if not found_tasks:
        print(f"Задачи с ключевым словом «{keyword}» не найдены.")
        return

    print(f"\nНайдено задач: {len(found_tasks)}")
    print("-" * 50)

    # Вывод найденных задач
    for task in found_tasks:

        status = "Выполнена" if task.get("completed", False) else "Активна"

        print(
            f"\n#{task.get('id', '?')} | "
            f"{task.get('name', 'Без названия')} | "
            f"Приоритет: {task.get('priority', '?')} | "
            f"Срок: {task.get('target_date') or 'Не указан'} | "
            f"Статус: {status}"
        )

        if task.get("description"):
            print(f"Описание: {task['description']}")
    print("\n" + "-" * 50)
    

# Функция проверки введённого времени, сгенерированная при помощи ChatGPT
def validate_task_date(date_string):
    """
    Проверяет корректность введённой даты.

    Дата должна:
    - быть в формате ДД.ММ.ГГГГ;
    - существовать в календаре;
    - не быть прошедшей.

    Возвращает:
        корректную дату в формате ДД.ММ.ГГГГ,
        если проверка пройдена;
        None, если дата некорректна.
    """
    try:
        # Преобразуем строку в дату
        task_date = datetime.strptime(
            date_string,
            "%d.%m.%Y"
        ).date()

    except ValueError:
        print(
            "Ошибка: дата должна быть введена "
            "в формате ДД.ММ.ГГГГ!"
        )
        return None

    # Получаем сегодняшнюю дату
    today = datetime.now().date()

    # Сравниваем введённую дату с текущей
    if task_date < today:
        print("Ошибка: дата выполнения не может быть прошедшей!")
        return None
    return date_string


# Функция обработки ошибок при чтении/записи JSON-файла (отсутствие файла, повреждённые данные, права доступа), сгенерированная при помощи ChatGPT
def handle_json_file(mode, data=None):
    """
    Обработка чтения и записи JSON-файла.
    mode:
        "read"  - чтение файла
        "write" - запись файла
    data:
        данные для записи в JSON.
    Возвращает:
        при чтении — список задач;
        при записи — True/False.
    """

    # ---------- ЧТЕНИЕ ----------
    if mode == "read":

        # Файл отсутствует
        if not os.path.exists(tasks_file_name):
            print("Файл tasks.json не найден. Создаётся пустой список задач.")
            return []

        try:
            with open(tasks_file_name, "r", encoding="utf-8") as f:
                tasks = json.load(f)

            # Проверяем структуру данных
            if not isinstance(tasks, list):
                print("Ошибка: данные в tasks.json должны быть списком.")
                return []

            return tasks

        except json.JSONDecodeError:
            print("Ошибка: файл tasks.json повреждён или содержит некорректный JSON.")
            return []

        except PermissionError:
            print("Ошибка: нет прав доступа для чтения tasks.json.")
            return []

        except OSError as error:
            print(f"Ошибка при чтении tasks.json: {error}")
            return []

    # ---------- ЗАПИСЬ ----------
    elif mode == "write":

        try:
            with open(tasks_file_name, "w", encoding="utf-8") as f:
                json.dump(
                    data,
                    f,
                    indent=4,
                    ensure_ascii=False
                )
            return True
        except PermissionError:
            print("Ошибка: нет прав доступа для записи tasks.json.")
            return False
        except OSError as error:
            print(f"Ошибка при записи tasks.json: {error}")
            return False
    else:
        print("Ошибка: неизвестный режим работы с JSON.")
        return False

    
# Функция реализации подтверждения при удалении задачи, сгенерированная при помощи ChatGPT
def confirm_deletion(task_name):
    """
    Запрашивает у пользователя подтверждение удаления задачи.

    Возвращает:
        True  — если пользователь подтвердил удаление;
        False — если пользователь отменил удаление.
    """
    print(f"\nВы собираетесь удалить задачу:")
    print(f"  {task_name}")

    while True:
        confirm = input(
            "Дополнительная проверка ИИ. Вы действительно хотите удалить задачу? (y/n): "
        ).strip().lower()

        if confirm in ("y", "yes"):
            return True

        if confirm in ("n", "no"):
            return False

        print("Ошибка: введите y (да) или n (нет).")

    
def main_menu():
    """
    Главное консольное меню
    """
    
    while True:
        print("\n" + "=" * 50)
        print("Консольный менеджер задач (To-Do list)")
        print("=" * 50)
        print("Что делаем сегодня? (Введите соответствующее число)")
        print("1 Добавить новую задачу")
        print("2 Показать список задач")
        print("3 Отфильтровать задачи по статусу выполнения")
        print("4 Отфильтровать задачи по приоритету")
        print("5 Отметить задачу выполненной")
        print("6 Удалить задачу из списка")
        print("7 Сортировать список задач")
        print("8 Экспортировать список задач в текстовый файл или csv")
        print("9 Поиск задач по ключевому слову в названии")
        print("0 Выход")
        print("=" * 50)
         
        choice = input("\n Выберите действие (0-9): ").strip()
         
        if choice == "1":
            print("\nДобавление новой задачи")
            print("-" * 30)
            task_name = input("Название задачи: ").strip()
            
            # Валидация пользовательского ввода - название задачи не может быть пустым
            if not task_name:
                print("Название задачи не может быть пустым!")
                continue
             
            task_description = input("Описание (Enter для пропуска): ").strip()

            # Валидация пользовательского ввода - дата срока выполнения должна быть в формате ДД.ММ.ГГГГ и не может быть прошедшей
            while True:
                task_target_date = input(
                    "Планируемая дата выполнения задачи "
                    "в формате ДД.ММ.ГГГГ (Enter для пропуска): "
                ).strip() or None

                # Если значение не введено
                if not task_target_date:
                    task_target_date = None
                    break

                # Функция проверки введённого времени, сгенрерированная при помощи ChatGPT
                # Вызываем функцию проверки даты
                if validate_task_date(task_target_date):
                    break
                    
                # Проверка, то дата - не прошедшая
                try:
                    task_target_date_time = datetime.strptime(task_target_date, "%d.%m.%Y").date()

                    if task_target_date_time < datetime.now().date():
                        print("Ошибка: дата планируемого выполнения не может быть прошедшей!")
                        continue
                    break

                except ValueError:
                    print("Ошибка: дата срока выполнения должна быть в формате ДД.ММ.ГГГГ!")

            # Приоритет должен выбираться из списка (высокий, средний, низкий)
            while True:
                print("\nВыберите приоритет:")
                print("  1 - Высокий")
                print("  2 - Средний")
                print("  3 - Низкий")
                task_priority_choice = input("Приоритет (1-3): ").strip()
             
                task_priority_map = {"1": "высокий", "2": "средний", "3": "низкий"}

                # Валидация пользовательского ввода - приоритет должен выбираться из списка
                if task_priority_choice in task_priority_map:
                    task_priority = task_priority_map[task_priority_choice]
                    break
                
                print("Ошибка: выберите приоритет 1, 2 или 3!")
             
            add_task(task_name, task_description, task_target_date, task_priority)
         
        elif choice == "2":
            print("\nОтображение всех задач:")
            print("-" * 30)
            filter_tasks()
         
        elif choice == "3":
            print("\nФильтрация задач по статусу выполнения:")
            print("  1 - Активные задачи")
            print("  2 - Выполненные задачи")
            print("-" * 30)
            status_choice = input("Выберите (1-2): ").strip()

            task_status_map = {"1": "active", "2": "completed"}
            task_status = task_status_map.get(status_choice)

            if status_choice not in task_status_map:
                print("Неверный выбор!")
                continue

            # Применяем фильтр
            print("\nРезультат фильтрации:")
            print("-" * 30)

            filter_tasks(tasks_status_filter=task_status)
         
        elif choice == "4":
            print("\nФильтрация задач по приоритету:")
            print("  1 - Высокий")
            print("  2 - Средний")
            print("  3 - Низкий")
            priority_choice = input("Выберите (1-3): ").strip()
             
            task_priority_map = {"1": "высокий", "2": "средний", "3": "низкий"}
            task_priority = task_priority_map.get(priority_choice)

            if priority_choice not in task_priority_map:
                print("Неверный выбор!")
                continue

            # Применяем фильтр
            print("\nРезультат фильтрации:")
            print("-" * 30)

            filter_tasks(tasks_priority_filter=task_priority)
         
        elif choice == "5":
            filter_tasks(tasks_status_filter="active")
            try:
                task_id = int(input("\nВведите ID задачи, чтобы отметить её выполненной: "))
                change_task_status(task_id)
            except ValueError:
                print("ID должен быть числом!")
         
        elif choice == "6":
            filter_tasks()
            try:
                task_id = int(input("\nВведите ID задачи для удаления: "))
                delete_task(task_id)
            except ValueError:
                print("ID должен быть числом!")
         
        elif choice == "7":
            print("\nСортировка списка задач по сроку выпонения, приоритету или статусу:")
            print("-" * 30)
            print("1 - По сроку выполнения")
            print("2 - По приоритету")
            print("3 - По статусу")
    
            sort_choice = input("Выберите вариант сортировки (1-3): ").strip()

            sort_map = {
                "1": "deadline",
                "2": "priority",
                "3": "status"
            }

            sort_by = sort_map.get(sort_choice)

            if sort_by is None:
                print("Неверный выбор!")
                continue

            print("\nРезультат сортировки:")
            print("-" * 30)
            sort_tasks(sort_by)
         
        elif choice == "8":
            print("\nЭкспорт списка задач в текстовый файл или CSV:")
            print("-" * 30)
            print("1 - Экспорт в текстовый файл (.txt)")
            print("2 - Экспорт в CSV-файл (.csv)")

            export_choice = input("Выберите формат (1-2): ").strip()

            if export_choice == "1":
                export_tasks("txt")

            elif export_choice == "2":
                export_tasks("csv")

            else:
                print("Неверный выбор!")
         
        elif choice == "9":
            print("\nПоиск задач по ключевому слову в названии:")
            print("-" * 30)
            keyword = input(
                "Введите ключевое слово для поиска в названии: "
            ).strip()

            search_tasks(keyword)
         
        elif choice == "0":
            print("\nПрограмма закрывается. До встречи.")
            time.sleep(5)
            sys.exit()
         
        else:
            print("Некорректный ввод. Выберите число от 0 до 9.")

        input("\nНажмите Enter для возврата в главное меню...")

# Имя файла для сохранения списка задач:
tasks_file_name = "tasks.json"
# Загружаем список задач
tasks_list = load_tasks()

if __name__ == "__main__":
    # __name__ — это специальная встроенная переменная в Python.
    # Её значение зависит от того, как выполняется код:
    # Если файл запускается напрямую (например, python my_script.py),
    # Python присваивает __name__ значение "__main__".
    # Если файл импортируется как модуль в другой файл (например, import my_script),
    # то __name__ становится равным имени модуля (например, "my_script").
    # Таким образом конструкция if __name__ == "__main__": позволяет разделить выполняемый код и импортируемый код. Если файл импортируется, код внутри этого блока не выполняется.
    # Если этот файл импортируется из другого скрипта (import tasks_manager),
    # то __name__ будет равно "tasks_manager", и блок с main_menu() не выполнится.
    # Так возможно использовать функции этого скрипта в других программах без запуска меню.
    
    # Запуск главного меню
    main_menu()