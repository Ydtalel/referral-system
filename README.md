# Referral System API

## Описание

Это RESTful API для реферальной системы.   
Пользователи могут регистрироваться, создавать реферальные коды,  
делиться ими и регистрировать других пользователей через эти коды.

## Функциональные возможности
- Регистрация и аутентификация пользователей (JWT).
- Создание, удаление и получение реферальных кодов.
- Регистрация по реферальным кодам.
- Получение списка рефералов пользователя.
- Swagger UI для документации и тестирования.

## Стек технологий
- Django
- Django REST Framework
- JWT (JSON Web Token) для аутентификации
- Swagger для автодокументации API

## Установка и запуск

### 1. Клонирование репозитория
Склонируйте проект с GitHub:

```
git clone https://github.com/Ydtalel/referral-system.git
cd referral-system
```
### 2. Создание виртуального окружения
```
python -m venv .venv
source .venv/bin/activate  # Для Mac/Linux
.venv\Scripts\activate  # Для Windows
```
### 3. Установка зависимостей
`pip install -r requirements.txt`

Создайте .env фаил в корне проекта со следующим содержимым: 

DB_NAME=<your_db_name>

DB_USER=<your_db_user>

DB_PASSWORD=<your_db_password>

DB_HOST=<your_db_host>

DB_PORT=<your_db_port>

DEBUG=True

HUNTER_API_KEY=<your_hunter.io_api_key>
### 4. Применение миграций
`python manage.py makemigrations`

`python manage.py migrate`
### 5. Запуск сервера
`python manage.py runserver`
### 6. Доступ к Swagger UI

Перейдите по адресу http://localhost:8000/api/swagger/ для доступа к  
интерактивной документации Swagger UI, где можно тестировать API.

Для этого необходимо создать пользователя. 
Затем выполнить логин запрос от его имени.   
После чего будет доступен "access" токен,  
который можно указать в Authorize в формате Bearer <ваш токен>

Так же доступны примеры запросов в **refferals.postman_collection.json**