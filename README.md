
# yatube
### Описание
Социальная сеть блоггеров. 
Этот сайт предназначен для публикации личных дневников. 
Пользователи смогут посещать чужие страницы, подписываться на авторов и комментировать их публикации.

### Стек
- Python 3.9
- Django 2.2.19
- Unittest

### Запуск проекта в dev-режиме
**Клонируйте репозиторий:**
```
git@github.com:Danilka234/yatube_social.git
```

**Установите и активируйте виртуальное окружение**
```
python -m venv venv
source venv/bin/activate
```

**Установите зависимости из файла requirements.txt**

```
pip install -r requirements.txt
```

**Выполните миграции**

```
python3 manage.py migrate
```

**В папке с файлом manage.py выполните команду:**

```
python3 manage.py runserver(Mac OS)
python manage.py runserver(Windows)
```

**Перейдите на страницу http://127.0.0.1:8000/ в любом браузере**

### Автор
Danil Yakushev
