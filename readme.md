# Скринер Облигаций на базе ISS MOEX

Через запросы к бесплатному API Мосбиржи (ISS MOEX) собираю все облигации на бирже и некоторые их метрики:
- дата начала торгов
- дата погашения
- размеры купонов
- расчитанная мосбиржей доходность
- объемы торгов
.. и ряд других

Метрики сохраняю в SQLLite базу (простая, файловая, локальная). Для дальнейшего анализа. В коде есть несколько примеров
анализа и построений отчетов с использованием Pandas. Однако можно использовать любые инструменты для работы с SQL базами. 

### Это суперальфапревью версия ;)

Что-то или всё может не работать. 

По большому счету это код для личного использования, экспериментов и для съемки видео на канале https://www.youtube.com/c/AzzraelCode
Рекомендую посмотреть остальные мои видео в плейлисте ISS MOEX https://www.youtube.com/watch?v=lkrwSLpeN1I&list=PLWVnIRD69wY62qRnOw8EjaKyC8buYe1GH
  

## Как использовать

1. Создать SQLLite базу (файл) можно с использованием SQLLite Studio (или любой другой программы) с полями описанными в модели 
( или используй SQLAlchemy для создания таблицы из модели ;) ). И положить её в папку _db проекта.

2. Установить питон и зависимости
python -m pip install -r requirements.txt

3. В консоли (cmd) перейти в директорию установки и 
`python __main__.py` 
для получения списка доступных комманд 
