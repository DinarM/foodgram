## Проект Foodgram
Foodgram — это удобный помощник в планировании покупок и приготовлении еды с коллекцией рецептов. Приложение позволяет делиться своими рецептами, сохранять понравившиеся в избранное и автоматически составлять список покупок на основе выбранных блюд. Также есть возможность подписываться на любимых кулинаров.

### Развернуть проект:
- Клонировать репозиторий
- Установить на сервере Docker, Docker Compose
- Скопировать на сервер файлы docker-compose.yml, nginx.conf
- Создать и запустить контейнеры Docker:
  sudo docker compose up -d
- Выполнить миграции:
  sudo docker compose exec backend python manage.py migrate
- Собрать статику:
  sudo docker compose exec backend python manage.py collectstatic
- Заполнить базу данных с ингредиентами из файла ingredients.csv и тегами из файла tags.csv:
  sudo docker exec -it foodgram-backend python manage.py load_ingredients_data
  sudo docker exec -it foodgram-backend python manage.py load_tags_data
