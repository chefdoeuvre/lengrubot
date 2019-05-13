# -*- coding: utf-8 -*-
from SQLighter import SQLighter
import random
import threading
import config
import telebot
import time
from datetime import datetime,timedelta

def langlevel(level):
   result = '['+('#'*level) + ('-' *(5-level))+']'
   return result

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
#create buttons for eng ru
markuplang.row(
    telebot.types.InlineKeyboardButton("English", callback_data="lang=English"),
    telebot.types.InlineKeyboardButton("Russian", callback_data="lang=Russian")
    )
# create buttons for lang level    
markuplevel.add(
    #*[telebot.types.InlineKeyboardButton(str(i), callback_data="level="+str(i)) for i in range(0,6,1)]
    telebot.types.InlineKeyboardButton("A2", callback_data="level=A2"),
    telebot.types.InlineKeyboardButton("B1", callback_data="level=B1"),
    telebot.types.InlineKeyboardButton("B2", callback_data="level=B2"),
    telebot.types.InlineKeyboardButton("C1", callback_data="level=C1"),
    telebot.types.InlineKeyboardButton("C2", callback_data="level=C2")
    )
#create buttons for UTC
for j in range(-14,12,8):
    markupgmt.row(*[telebot.types.InlineKeyboardButton(str(i), callback_data="utc="+str(i)) for i in range(j,13,1)])

@bot.message_handler(commands=['list'])
def send_message(message):
    if message.from_user.id == 87250032:
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
        rules = ''' Hello!
Both languages are allowed.
Feel free to ask, if you do not understand something in a conversation.
Don't be rude

Only English chat (English practice for Russians): 
@elish_practice
Native speakers are welcomed here. Please help us, like we help you. Thank you.

Оба языка разрешены.
Спрашивайте, если что-то непонятно.
Не будьте грубыми.
Старайтесь уместить мысль в одно сообщение.

Специально для русских: материться можно, но только если этого требует контекст разговора.
#RULES

================
Bot added to chat. 
write PM @lengrubot and press start to fill your profile. (or PM /start )
/me - for info about you
/info [nickname] - about anyone else.
#bot_info
================
'''
        bot.send_message(message.chat.id,rules)


@bot.message_handler(commands=['me'])
def send_messages(message):	
    db_worker = SQLighter(config.database_name)
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
    if user_username == "None":
        user_username = str(message.from_user.first_name) + " "+ str(message.from_user.last_name)
    else:
        user_username = "@"+user_username
    if user_lang == 'English': other_lang = 'Russian' 
    else: other_lang = 'English' 
    response = str(user_username)+' is '+str(user_lang)+' native speaker. '+other_lang+' level is '+str(user_level)+'. Current time: '+user_time
    bot.send_message(message.chat.id, response) 

@bot.message_handler(commands=['info'])
def send_messages(message):
    username = message.text[6:len(message.text)]
    if username.startswith("@"): username = username[1:len(message.text)] 
    db_worker = SQLighter(config.database_name)
    if db_worker.UserExists(message.from_user.id, username) != 0:
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
        response = '@'+str(user_username)+' is '+str(user_lang)+' native speaker. '+other_lang+' level is '+str(user_level)+'. Current time: '+user_time
    else:
        response = 'User '+username+ " does not exists."        
    db_worker.close()
    
    bot.send_message(message.chat.id, response)

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
            text="Type your knowledge level of other language", 
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
            text="Thank you! You can try '/me' command."
            )  
        #adduserUTC
        db_worker = SQLighter(config.database_name)
        db_worker.UpdateUserInfo(callback_query.from_user.id,'UTC',callback_query.data[4:])
        db_worker.close()
    

if __name__ == '__main__':
    random.seed()
    bot.polling(none_stop=True)