# Запуск проекта

- Корневая директория SpendSplif
- Открываем консоль
  - **docker-compose up**
- Открываем ещё одну консоль
  - **docker ps**
  - **docker exec -it <id контейнера spendsplif-backend> bash**
  - (не будет работать без предыдущего шага)
- Далее активируется консоль контейнера проекта, там прописываем:
  - **python manage.py makemigrations**
  - **python manage.py migrate**
- Готово
  - **http://127.0.0.1:8000/**

### Установка [Docker](https://www.docker.com/products/docker-desktop/)
На windows придётся установить wsl перед установкой docker = ввести в консоли команду **wsl --install**

На Linux и MacOS всё устанавливается без лишних манипуляций - просто скачать установщик с сайта