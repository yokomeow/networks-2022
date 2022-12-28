**Full-stack веб приложение "Type Train"**
=========
-----
Приложение состоит из:
---------
### Frontend
+ HTML
+ CSS
+ JS
### Backend
+ API (Python Flask)
+ DB (MySQL 5.7)
+ Nginx

### Описание приложения
---
Приложение представляет собой сервис для тренировки слепой печати.
Основная идея приложения - нейросеть, подбирающая для пользователя слова с наиболее проблемными для него буквами.
При первом запуске необходимо напечатать несколько случайных слов, предлагаемых приложением, для обучения нейросети. После необходимого количества слов нейросеть начнет подбирать слова с проблемными буквами, продолжая отслеживать успехи пользователя.
Также сервис дает возможность посмотреть график попадания по каждой букве за все время.

### Запуск приложения
---
cd Type-Train  
docker-compose up -d

python3 staff/create_tables.py 
python3 staff/words.py
docker exec -it mysql_web /bin/bash
	mysql -u root -p tt
	insert into users (user_id, attempts) values (1, 0);