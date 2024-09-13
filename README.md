## Проект **Foodgram**

**Foodgram** — это сервис для планирования питания и покупок с коллекцией рецептов. Приложение предоставляет возможность пользователям делиться рецептами, сохранять понравившиеся блюда в избранное и автоматически создавать списки покупок на основе выбранных рецептов. Вы также можете подписываться на любимых авторов.

![workflow](https://github.com/DinarM/foodgram/actions/workflows/main.yml)

Проект доступен по [этой ссылке](https://foodgram-dinar.hopto.org/)

API-документация проекта доступна [здесь](https://foodgram-dinar.hopto.org/api/docs/)

Документация описывает возможные запросы и ответы API, а также включает информацию о необходимых правах доступа для каждого запроса.

### Стек технологий:
- Python
- Django
- Django REST Framework
- Docker
- Gunicorn
- NGINX
- PostgreSQL
- CI/CD

### Как развернуть проект:

#### Локальный запуск с использованием Docker:

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/DinarM/foodgram.git
   ```

2. **Создайте файл `.env` в корневой директории, используя пример из `example.env`, и заполните его своими данными:**
   ```bash
   POSTGRES_DB=foodgram
   POSTGRES_USER=foodgram_user
   POSTGRES_PASSWORD=foodgram_password
   DB_NAME=foodgram
   SECRET_KEY=django-insecure-secret!key!example
   ALLOWED_HOSTS=example.hopto.org,1.1.1.1,localhost
   DEBUG=False
   USE_SQLITE=False
   ```

3. **Запустите контейнеры Docker:**
   ```bash
   docker-compose -f docker-compose-local.yml up -d
   ```

4. **Выполните миграции, соберите статику и создайте суперпользователя:**
   ```bash
   docker exec -it foodgram-backend python manage.py migrate
   docker exec -it foodgram-backend python manage.py collectstatic
   docker exec -it foodgram-backend python manage.py createsuperuser
   ```

5. **Заполните базу данных ингредиентами и тегами:**
   ```bash
   docker exec -it foodgram-backend python manage.py load_ingredients_data
   docker exec -it foodgram-backend python manage.py load_tags_data
   ```

6. **Проект будет доступен по адресу: [http://localhost](http://localhost)**

API-документация будет доступна по адресу: [http://localhost/api/docs/](http://localhost/api/docs/)

#### Развертывание на удаленном сервере:

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/DinarM/foodgram.git
   ```

2. **Установите Docker и Docker Compose на сервере:**
   ```bash
   sudo apt install curl
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo apt-get install docker-compose-plugin
   ```

3. **Скопируйте файлы `docker-compose.yml` и `nginx.conf` на сервер:**
   ```bash
   scp docker-compose.yml nginx.conf username@IP:/home/username/foodgram
   ```

4. **Создайте файл `.env` и настройте его по аналогии с `example.env`:**
   ```bash
   POSTGRES_DB=foodgram
   POSTGRES_USER=foodgram_user
   POSTGRES_PASSWORD=foodgram_password
   DB_NAME=foodgram
   SECRET_KEY=django-insecure-secret!key!example
   ALLOWED_HOSTS=example.hopto.org,1.1.1.1,localhost
   DEBUG=False
   USE_SQLITE=False
   ```

5. **Запустите Docker-контейнеры:**
   ```bash
   sudo docker compose up -d
   ```

6. **После успешной сборки выполните миграции и сбор статики:**
   ```bash
   sudo docker exec -it foodgram-backend python manage.py migrate
   sudo docker exec -it foodgram-backend python manage.py collectstatic
   ```

7. **Создайте суперпользователя:**
   ```bash
   sudo docker exec -it foodgram-backend python manage.py createsuperuser
   ```

8. **Заполните базу данных:**
   ```bash
   sudo docker exec -it foodgram-backend python manage.py load_ingredients_data
   sudo docker exec -it foodgram-backend python manage.py load_tags_data
   ```

9. **Остановка контейнеров:**
   ```bash
   sudo docker compose down -v # удаление контейнеров
   sudo docker compose stop    # остановка без удаления
   ```

### Запуск проекта без Docker:

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/DinarM/foodgram.git
   ```

2. **Создайте файл `.env` и настройте его:**
   ```bash
   POSTGRES_DB=foodgram
   POSTGRES_USER=foodgram_user
   POSTGRES_PASSWORD=foodgram_password
   DB_NAME=foodgram
   SECRET_KEY=django-insecure-secret!key!example
   ALLOWED_HOSTS=example.hopto.org,1.1.1.1,localhost
   DEBUG=False
   USE_SQLITE=True (обязательно указываем True для использования БД SQLite)
   ```

3. **Выполните миграции и сбор статики:**
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

4. **Создайте суперпользователя:**
   ```bash
   python manage.py createsuperuser
   ```

5. **Запустите сервер:**
   ```bash
   python manage.py runserver
   ```

6. **Заполните базу данных:**
   ```bash
   python manage.py load_ingredients_data
   python manage.py load_tags_data
   ```

7. **Проект будет доступен по адресу: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

API-документация будет доступна по адресу: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)

### Автор backend'а:
**Динар Мирсаитов**
