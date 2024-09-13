## Проект Foodgram
Foodgram — это удобный помощник в планировании покупок и приготовлении еды с коллекцией рецептов. Приложение позволяет делиться своими рецептами, сохранять понравившиеся в избранное и автоматически составлять список покупок на основе выбранных блюд. Также есть возможность подписываться на любимых кулинаров.

![workflow](https://github.com/DinarM/foodgram/actions/workflows/main.yml)

Проект доступен по [адресу](https://foodgram-dinar.hopto.org/)

Документация к API доступна [здесь](https://foodgram-dinar.hopto.org/api/docs/)

В документации представлены возможные запросы к API и формат предполагаемых ответов. Для каждого запроса указаны необходимые уровни доступа.

### Технологии:
Python, Django, Django Rest Framework, Docker, Gunicorn, NGINX, PostgreSQL, Continuous Integration, Continuous Deployment


### Развернуть проект:
- Клонировать репозиторий
- Установить на сервере Docker, Docker Compose
- Скопировать на сервер файлы docker-compose.yml, nginx.conf
- Создать и запустить контейнеры Docker:
  sudo docker compose up -d
- Выполнить миграции:
  sudo docker exec -it foodgram-backend python manage.py migrate
- Собрать статику:
  sudo docker exec -it foodgram-backend python manage.py collectstatic
- Заполнить базу данных с ингредиентами из файла ingredients.csv и тегами из файла tags.csv:
  sudo docker exec -it foodgram-backend python manage.py load_ingredients_data
  sudo docker exec -it foodgram-backend python manage.py load_tags_data


### Развернуть проект на удаленном сервере:

- Клонировать репозиторий:
```
https://github.com/DinarM/foodgram.git
```

- Установить на сервере Docker, Docker Compose:

```
sudo apt install curl                                   # установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      # скачать скрипт для установки
sh get-docker.sh                                        # запуск скрипта
sudo apt-get install docker-compose-plugin              # последняя версия docker compose
```

- Скопировать на сервер файлы docker-compose.yml, nginx.conf из папки infra (команды выполнять находясь в папке infra):

```
scp docker-compose.yml nginx.conf username@IP:/home/username/foodgram   # username - имя пользователя на сервере
                                                                        # IP - публичный IP сервера
```

- В корневой директории создать файл .env и заполнить своими данными по аналогии с example.env:
```
sudo nano .env
```

- Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:
```
SECRET_KEY              # секретный ключ Django проекта
DOCKER_PASSWORD         # пароль от Docker Hub
DOCKER_USERNAME         # логин Docker Hub
HOST                    # публичный IP сервера
USER                    # имя пользователя на сервере
PASSPHRASE              # *если ssh-ключ защищен паролем
SSH_KEY                 # приватный ssh-ключ
TELEGRAM_TO             # ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          # токен бота, посылающего сообщение
```

- Создать и запустить контейнеры Docker, выполнить команду на сервере
```
sudo docker compose up -d
```

- После успешной сборки выполнить миграции:
```
sudo docker exec -it foodgram-backend python manage.py migrate
```

- Создать суперпользователя:
```
sudo docker exec -it foodgram-backend python manage.py createsuperuser
```

- Собрать статику:
```
sudo docker exec -it foodgram-backend python manage.py collectstatic
```

- Заполнить базу данных с ингредиентами из файла ingredients.csv и тегами из файла tags.csv:
```
sudo docker exec -it foodgram-backend python manage.py load_ingredients_data
sudo docker exec -it foodgram-backend python manage.py load_tags_data
```

- Для остановки контейнеров Docker:
```
sudo docker compose down -v      # с их удалением
sudo docker compose stop         # без удаления
```


### Запуск проекта на локальной машине через Docker:

- Клонировать репозиторий:
```
https://github.com/DinarM/foodgram.git
```

- В корневой директории создать файл .env и заполнить своими данными по аналогии с example.env:
```
DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY='секретный ключ Django'
```

- Создать и запустить контейнеры Docker, последовательно выполнить команды по созданию миграций, сбору статики, 
созданию суперпользователя, как указано выше.
```
docker-compose -f docker-compose-local.yml up -d
```


- После запуска проект будут доступен по адресу: [http://localhost/](http://localhost/)


- Документация будет доступна по адресу: [http://localhost/api/docs/](http://localhost/api/docs/)


### Запуск проекта на локальной машине:

- Клонировать репозиторий:
```
https://github.com/DinarM/foodgram.git
```

- В корневой директории создать файл .env и заполнить своими данными по аналогии с example.env:
```
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
SECRET_KEY=django-insecure-secret!key!example
ALLOWED_HOSTS=example.hopto.org,1.1.1.1,localhost
DEBUG=False
USE_SQLITE=False (обязательно указываем False для использования БД SQLite)
```

- Выполнить миграции:
```
python manage.py migrate
```

- Создать суперпользователя:
```
python manage.py createsuperuser
``

- Запустить сервер:
```
python manage.py runserver
```

- Заполнить базу данных с ингредиентами из файла ingredients.csv и тегами из файла tags.csv:
```
python manage.py load_ingredients_data
python manage.py load_tags_data
```

- После запуска проект будут доступен по адресу: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)


- Документация будет доступна по адресу: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)


### Автор backend'а:

Динар Мирсаитов