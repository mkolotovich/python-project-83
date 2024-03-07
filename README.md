# Python проект - "Анализатор страниц"
### Hexlet tests and linter status:
[![Actions Status](https://github.com/mkolotovich/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/mkolotovich/python-project-83/actions)
[![Actions Status](https://github.com/mkolotovich/python-project-50/actions/workflows/pyci.yml/badge.svg)](https://github.com/mkolotovich/python-project-50/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/e2a0526b6c87cf557c1b/maintainability)](https://codeclimate.com/github/mkolotovich/python-project-83/maintainability)

## Описание
Page Analyzer – это сайт, который анализирует указанные страницы на SEO-пригодность по аналогии с PageSpeed Insights:
[главная страница](https://cdn2.hexlet.io/derivations/image/original/eyJpZCI6IjhmOGQ0NDU4MTQzODM0MzAzZjVlYzFmYTQxMjU0YjhjLnBuZyIsInN0b3JhZ2UiOiJjYWNoZSJ9?signature=410b727cc3ab6caf1344391460b60f863c79b7116dbbcc8d05fd85209b8dc116)
[страница добавленных сайтов](https://cdn2.hexlet.io/derivations/image/original/eyJpZCI6IjRjOTY1OThiYTU1ZTdmNWUwMDhjNGE3ZjEwZmUzZTk4LnBuZyIsInN0b3JhZ2UiOiJjYWNoZSJ9?signature=aea2b053c45d546d7a231e3e87bac8eca22b8889b19879545b1afff56dbc6761)
[страница проверок сайта](https://cdn2.hexlet.io/derivations/image/original/eyJpZCI6IjcxYWJkMzRjM2ZmMTFmMDVlYzJmZTBlMDRkM2U3MGM5LnBuZyIsInN0b3JhZ2UiOiJjYWNoZSJ9?signature=78dc3ec23b54a0e7e222ed57ebff9cbcaf4d1ac2cf34a7a1c5e22c38c99b3183)

## Установка и запуск приложения 
1. Убедитесь, что у вас установлен Python версии 3.10 или выше. В противном случае установите Python версии 3.10 или выше.
2. Установите СУБД PostgreSQL если она у вас не установлена и создайте в ней БД. Создайте файл .env в котором пропишите переменную окружения DATABASE_URL которая задаёт подключение к вашей БД. Также создайте переменную окружения  SECRET_KEY и задайте ей значение.
3. Установите зависимости в систему и создайте таблицы в БД командой make build. Запустк приложения осуществляется командой make dev в терминале. Команды make build и make dev необходимо запускать из корневой директории проекта.

Деплой - https://python-project-83-khgp.onrender.com/