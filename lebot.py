# -*- coding: utf-8 -*-
import telebot

import random
import config
import time
import re
from datetime import datetime,timedelta

from SQLighter import SQLighter
import messages as msgs

global reg_notify
reg_notify = config.default_regnotify
global english_only
english_only = False
global russian_only
russian_only = False
global auto_langday
auto_langday = config.default_autolangday
global cooldown_nexttime
cooldown_nexttime = datetime.now()
global cooldown # in minutes
cooldown = config.default_cooldown


def isRussianDay():
    """Проверка "русский" ли сегодня день"""
    global russian_only
    global auto_langday
    return (auto_langday and int(datetime.now().day)%2 != 0) or russian_only

def isEnglishDay():
    """Проверка "английский" ли сегодня день"""
    global english_only
    global auto_langday
    return (auto_langday and int(datetime.now().day)%2 == 0) or english_only

def ratioOfRussian(txt):
    """ Доля кириллицы ко всем буквам в тексте. """
    tlc = len(re.findall('[а-яА-Я]', txt))
    alc = len(re.findall('[а-яА-Яa-zA-Z]', txt))
    return tlc/alc if alc > 0 else 0

def ratioOfEnglish(txt):
    """ Доля латиницы ко всем буквам в тексте. """
    tlc = len(re.findall('[a-zA-Z]', txt))
    alc = len(re.findall('[а-яА-Яa-zA-Z]', txt))
    return tlc/alc if alc > 0 else 0

def adminonly(func):
    """Декоратор, для команд работающих только из под админа."""
    def wrapper(message):
        if message.from_user.id in config.admins:
            func(message)
        else:
            print("Acess from {} denied".format(message.from_user.id))
    return wrapper

bot = telebot.TeleBot(config.token)

# command
# /info [username]  -- info about one username
# /list             -- list all username with info (потом, в этйо команде особо нет необходимости)
# /me               -- list info about me
# запрос инфы для нового пользователя и добавление в БД
# вывод инфы
# /list инфа о юзерах в базе
# /debug 1 инфа по базе по номеру записи

markuplang = telebot.types.InlineKeyboardMarkup()
markuplevel = telebot.types.InlineKeyboardMarkup()
markupgmt = telebot.types.InlineKeyboardMarkup()
markupregister = telebot.types.InlineKeyboardMarkup()
#create buttons for eng ru
markuplang.row(
    telebot.types.InlineKeyboardButton("English", callback_data="lang=English"),
    telebot.types.InlineKeyboardButton("Russian", callback_data="lang=Russian")
)
# create buttons for lang level
markuplevel.add(
    *[telebot.types.InlineKeyboardButton(str(i), callback_data=("level={}".format(i))) for i in config.levels]
)
#create buttons for UTC
for j in range(-14,12,8):
    markupgmt.row(*[telebot.types.InlineKeyboardButton(str(i), callback_data="utc="+str(i)) for i in range(j,13,1)])

#create button for register
markupregister.add (
    telebot.types.InlineKeyboardButton("Registration", url='http://t.me/lengrubot')
)


def WhoIsHere(message,lang):
    db_worker = SQLighter(config.database_name)
    Everyone = db_worker.ListLang(lang)
    db_worker.close()
    response = 'List of all registered '+lang+' native speakers \nUsers count: '+ str(len(Everyone))+"\n"
    for line in Everyone:
        if line[1] is None:
            time = "Unknown"
        else:
            time = str((datetime.utcnow() + timedelta(hours=int(line[1]))).strftime("%H:%M"))
        #print("=============== "+str(line[0]))
        try:
            user = bot.get_chat_member(message.chat.id,str(line[0])).user
            if user.first_name and user.last_name:
                fullname = "{} {}".format(user.first_name, user.last_name)
            elif user.first_name:
                fullname = user.first_name
            elif user.last_name:
                fullname = user.last_name
            elif user.username:
                fullname = user.username
            else:
                fullname = "unknown"
            response = response+'['+time+'] '+fullname+'\n'
        except:
            pass
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['le'])
def send_message(message):
    WhoIsHere(message,'English')

@bot.message_handler(commands=['lr'])
def send_message(message):
    WhoIsHere(message,'Russian')

@bot.message_handler(commands=['list'])
@adminonly
def send_message(message):
    db_worker = SQLighter(config.database_name)
    Everyone = db_worker.ListAll()
    db_worker.close()
    response = 'User count: '+ str(len(Everyone))+"\n"
    for line in Everyone:
        response = response+str(line)+"\n"
    bot.send_message(message.from_user.id, response)

@bot.message_handler(commands=['start'])
def test_message(message):
    bot.send_message(message.from_user.id, "Choose your native (main) language", reply_markup = markuplang)

@bot.message_handler(commands=['rules'])
def send_message(message):
        bot.send_message(message.chat.id,config.rules)

@bot.message_handler(commands=['me'])
def send_messages_me(message):
    db_worker = SQLighter(config.database_name)
    if db_worker.UserExists(message.from_user.id,message.from_user.username) == 0 and reg_notify is True:
            bot.send_message(
                chat_id=message.chat.id,
                text=msgs.register,
                reply_markup = markupregister,
                reply_to_message_id = message.message_id
            )
            return
    db_worker.UserExists(message.from_user.id, message.from_user.username)
    user_id, user_username, user_lang, user_level, user_UTC = db_worker.WhoAmI(message.from_user.id)
    db_worker.close()
    if user_UTC is None:
        user_time = "Unknown"
    else:
        user_time = str((datetime.utcnow() + timedelta(hours=user_UTC)).strftime("%H:%M"))
    if user_level is None:
        user_level = "Unknown"
   # else:
    #    user_level = langlevel(user_level)
#    if user_username == "None":
    ufn = message.from_user.first_name
    uln = message.from_user.last_name
    if ufn is not None: user_username = ufn
    if uln is not None: user_username = user_username+" "+uln
    #user_username = str(message.from_user.first_name) + " "+ str(message.from_user.last_name)
#    else:
#        user_username = "@"+user_username
    if user_lang == 'English': other_lang = 'Russian'
    else: other_lang = 'English'
    response = str(user_username)+' is '+str(user_lang)+' native speaker. '+other_lang+' level is '+str(user_level)+'. Current time: '+user_time
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['info'])
def send_messages(message):
    username = message.text[6:len(message.text)]
    if username == '' or username == "lengrubot":
       send_messages_me(message)
       return
    if len(username) > 50: return
    if username.startswith("@"): username = username[1:len(message.text)]
    db_worker = SQLighter(config.database_name)
    if db_worker.UserExistsInfo(username) != 0:
        user_id, user_username, user_lang, user_level, user_UTC = db_worker.Whois(username)
        #user_time = datetime.utcnow() + timedelta(hours=user_UTC)
        if user_UTC is None:
            user_time = "Unknown"
        else:
            user_time = str((datetime.utcnow() + timedelta(hours=user_UTC)).strftime("%H:%M"))
        if user_level is None:
            user_level = "Unknown"
        #else:
        #    user_level = langlevel(user_level)
        if user_lang == 'English': other_lang = 'Russian'
        else: other_lang = 'English'
        ufn = bot.get_chat_member(message.chat.id,user_id).user.first_name
        uln = bot.get_chat_member(message.chat.id,user_id).user.last_name
        if ufn is not None: user_username = ufn
        if uln is not None: user_username = user_username+" "+uln
        response = str(user_username)+' is '+str(user_lang)+' native speaker. '+other_lang+' level is '+str(user_level)+'. Current time: '+user_time
    else:
        response = username+ " is wrong username or user does not have username."
    db_worker.close()
    bot.send_message(message.chat.id, str(response))

@bot.callback_query_handler(func=lambda call:True)
def callback_answer(callback_query: telebot.types.CallbackQuery): #И отвечаем на него
    bot.answer_callback_query(
        callback_query.id,
        text='Choosed '+callback_query.data,
        show_alert=False
    )
    if (callback_query.data).startswith("lang=") == True:
        bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="Choose your knowledge level of other language",
            reply_markup = markuplevel
        )
        #adduserlanguage if userexists
        db_worker = SQLighter(config.database_name)
        db_worker.UserExists(callback_query.from_user.id,callback_query.from_user.username)
        db_worker.UpdateUserInfo(callback_query.from_user.id,'lang',callback_query.data[5:])
        db_worker.close()
    if (callback_query.data).startswith("level=") == True:
        bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="Choose your timezone (+3 for Moscow, for example)",
            reply_markup = markupgmt
        )
        #adduserlevel
        db_worker = SQLighter(config.database_name)
        db_worker.UpdateUserInfo(callback_query.from_user.id,'level',callback_query.data[6:])
        db_worker.close()
    if (callback_query.data).startswith("utc=") == True:
        bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="Thank you! You can try /me command here or in the group."
        )
        #adduserUTC
        db_worker = SQLighter(config.database_name)
        db_worker.UpdateUserInfo(callback_query.from_user.id,'UTC',callback_query.data[4:])
        db_worker.close()

@bot.message_handler(commands=['russianonly'])
@adminonly
def sendreg_message(message):
    global russian_only
    russian_only = not russian_only
    bot.send_message(message.chat.id,"Russian only mode is "+str(russian_only))

@bot.message_handler(commands=['englishonly'])
@adminonly
def sendreg_message(message):
    global english_only
    english_only = not english_only
    bot.send_message(message.chat.id,"English only mode is "+str(english_only))

@bot.message_handler(commands=['reg'])
@adminonly
def sendreg_message(message):
    global reg_notify
    reg_notify = not reg_notify
    bot.send_message(message.chat.id,"Notify about registration is "+str(reg_notify))

@bot.message_handler(commands=['autolangday'])
@adminonly
def sendreg_message(message):
    global auto_langday
    auto_langday = not auto_langday
    bot.send_message(message.chat.id,"Autolangday is "+str(auto_langday))

@bot.message_handler(commands=['today'])
def sendreg_message(message):
    timenow = (datetime.now()).strftime("%H:%M")
    if isEnglishDay():
        bot.send_message(
            chat_id = message.chat.id,
            text = msgs.day_english + '\nServer time: '+ timenow,
            reply_to_message_id = message.message_id
        )
    elif isRussianDay():
        bot.send_message(
            chat_id = message.chat.id,
            text =  msgs.day_russian + '\nServer time: '+timenow,
            reply_to_message_id = message.message_id
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text= msgs.day_none,
            reply_to_message_id = message.message_id
        )

@bot.message_handler(commands=['cooldown'])
@adminonly
def sendreg_message(message):
    global cooldown
    global cooldown_nexttime
    if len(message.text) > 10: cooldown = int(message.text[10:len(message.text)])
    bot.send_message(message.chat.id,"Cooldown = "+str(cooldown)+" minutes\n cooldown_nexttime = "+ cooldown_nexttime.strftime("%H:%M") + "\n datetime now = "+ datetime.now().strftime("%H:%M"))

@bot.message_handler(commands=['reset_cooldown'])
@adminonly
def reset_cooldown(message):
    global cooldown_nexttime
    cooldown_nexttime = datetime.now()
    bot.send_message(message.chat.id, "Cooldown's been reseted")

@bot.message_handler(content_types=["text"])
def checkall(message):
    global reg_notify
    global cooldown
    global cooldown_nexttime
    db_worker = SQLighter(config.database_name)
    if db_worker.UserExists(message.from_user.id,message.from_user.username) == 0 and reg_notify:
        bot.send_message(
            chat_id=message.chat.id,
            text=msgs.register,
            reply_markup = markupregister,
            reply_to_message_id = message.message_id
        )
    db_worker.close()
    if datetime.now() > cooldown_nexttime and len(message.text) > 5:
        if isEnglishDay():
            ru_ratio = ratioOfRussian(message.text)
            if ru_ratio > config.threshold:
                bot.send_message(
                    message.chat.id,
                    msgs.violation_english.format(ru_ratio),
                    reply_to_message_id = message.message_id
                )
                cooldown_nexttime = datetime.now() + timedelta(minutes=cooldown)
        elif isRussianDay():
            en_ratio = ratioOfEnglish(message.text)
            if en_ratio > config.threshold:
                bot.send_message(
                    message.chat.id,
                    msgs.violation_russian.format(en_ratio),
                    reply_to_message_id = message.message_id
                )
                cooldown_nexttime = datetime.now() + timedelta(minutes=cooldown)

if __name__ == '__main__':
    bot.polling(none_stop=True)
