# Запуск проекта

- В репозитории фронта есть [баш скрипты](https://github.com/TARFASH/SpendSpl/tree/develop/src/utils/dev) для линукса они ещё не совсем готовые
- Корневая директория SpendSplif
  - ветка `feature/user`
- Открываем консоль
  - `docker-compose up`
- Открываем ещё одну консоль
  - `docker ps`
  - `docker exec -it <id контейнера spendsplif-backend> bash`
    - или `docker exec -it $SS_CONTAINER_ID sh -c "python manage.py makemigrations && python manage.py migrate"` чтобы пропустить шаги ниже
  - (не будет работать без предыдущего шага)
- Далее активируется консоль контейнера проекта (внутри докер контейнера), там прописываем:
  - `python manage.py makemigrations`
  - `python manage.py migrate`
  - также, эта консоль не должна быть постоянно открытой. Т.е. можно выполнить миграции и потом её спокойно закрывать.
- Готово
  - **http://127.0.0.1:8000/**

**Важно:** если в код были внесены изменения, нужно перебилдить контейнер при запуске командой `docker-compose up -d --build`

# Установка [Docker](https://www.docker.com/products/docker-desktop/)
На windows придётся установить wsl перед установкой docker = ввести в консоли команду **wsl --install**

На Linux и MacOS всё устанавливается без лишних манипуляций - просто скачать установщик с сайта

## Linux альтернативный вариант

- Используем дефолтный пакетный менеджер
  - (apt, dnf) `sudo <пакетный менеджер> install docker docker-compose`.
  - На арче это будет что-то вроде `sudo pacman -S docker docker-compose`. Вполне возможно что эта команда не правильная. Арчем я не пользуюсь.
