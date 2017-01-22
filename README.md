# IP_Checker
Checks diesel forum and it's topics

https://ipupper.net.kg/ch

Сервис для проверки соблюдений правил на форуме diesel.elcat.kg

После 01.01.2017 года было введено новое правило, запрещающее поднятие (up) темы в коммерческих разделах чаще одного раза в сутки (раньше было разрешено раз в час)

Данный сервис сканирует форум раздел коммерции и сохраняет все темы и сообщения в нем.
Сначала было реализовано с потоками, однако количество запросов на форум ограничивается самим форумом. 

Собранные данные дальше будут использоваться другим сервисом (ipupper.net.kg) который будет отдавать список авторов тем нарушивших правила и их темы.
Так же будет реализован API на стороне ipupper.net.kg для отдачи этих данных

python 2.7
parsel 1.1
