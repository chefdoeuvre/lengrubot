# -*- coding: utf-8 -*-
token = 'this is token for test_lebot'
admins = [
    87250032,
    227039625
]
levels = [
  "A2",
  "B1",
  "B2",
  "C1",
  "C2"
]
database_name = 'people.db'
default_cooldown = 2
default_autolangday = True
default_regnotify = True
threshold = 0.4
rules = ''' Hello!
Both languages are allowed.
Feel free to ask, if you do not understand something in a conversation.
Don't be rude.
No unwanted PM.

Only English chat (English practice for Russians):
@elish_practice
Native speakers are welcomed here. Please help us, like we help you. Thank you.

Оба языка разрешены.
Спрашивайте, если что-то непонятно.
Не будьте грубыми.
Старайтесь уместить мысль в одно сообщение.
У бота в группе есть режим "День определенного языка". Если он включен, Английский предпочтителен в четные дни, русский - в нечетные.
Бот будет уведомлять пользователей использующих неправильынй язык.

Специально для русских: материться можно, но только если этого требует контекст разговора.
#RULES

================
Bot added to chat.
write PM @lengrubot and press start to fill your profile. (or PM /start )
/me - for info about you
/info [nickname] - about anyone else.
/le - list of all registered native English speakers.
/lr - list of all registered native Russian speakers.
/today - info about "language days" mode
#bot_info
================
Group has a "mode of the day of the language". When it's enabled English is preferred on the even days and Russian on the odd days.
Bot "lebot" will notify users who will be using the wrong language.
'''
