# -*- coding: utf-8 -*-
from SQLighter import SQLighter
import random
import threading
import config
import telebot
import time
import re
from datetime import datetime,timedelta

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

# this not using anymore
def langlevel(level):
   result = '['+('#'*level) + ('-' *(5-level))+']'
   return results

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
            ufn = bot.get_chat_member(message.chat.id,str(line[0])).user.first_name
            if ufn is not None: fullname=ufn
            uln = bot.get_chat_member(message.chat.id,str(line[0])).user.last_name
            if uln is not None: fullname=fullname+' '+uln
        except:
            fullname = bot.get_chat_member(message.chat.id,str(line[0])).user.username
            pass
        response = response+'['+time+'] '+fullname+'\n'
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['le'])
def send_message(message):
    WhoIsHere(message,'English')

@bot.message_handler(commands=['lr'])
def send_message(message):
    WhoIsHere(message,'Russian')

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
        bot.send_message(message.chat.id,config.rules)


@bot.message_handler(commands=['me'])
def send_messages_me(message):	
    db_worker = SQLighter(config.database_name)
    if db_worker.UserExists(message.from_user.id,message.from_user.username) == 0 and reg_notify is True:
            bot.send_message(
                chat_id=message.chat.id, 
                text="We would like to know what is your native language, please make a registration via our Bot.", 
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
def sendreg_message(message):      
    global russian_only
    if message.from_user.id == 87250032:
        if russian_only is False: 
            russian_only = True 
        else: 
            russian_only = False
        bot.send_message(message.chat.id,"Russian only mode is "+str(russian_only))

@bot.message_handler(commands=['englishonly'])
def sendreg_message(message):      
    global english_only
    if message.from_user.id == 87250032:
        if english_only is False: 
            english_only = True 
        else: 
            english_only = False
        bot.send_message(message.chat.id,"English only mode is "+str(english_only))

@bot.message_handler(commands=['reg'])
def sendreg_message(message):      
    global reg_notify
    if message.from_user.id == 87250032:
        if reg_notify is False: 
            reg_notify = True 
        else: 
            reg_notify = False
        bot.send_message(message.chat.id,"Notify about registration is "+str(reg_notify))

@bot.message_handler(commands=['autolangday'])
def sendreg_message(message):      
    global auto_langday
    if message.from_user.id == 87250032:
        if auto_langday is False: 
            auto_langday = True 
        else: 
            auto_langday = False
        bot.send_message(message.chat.id,"Autolangday is "+str(auto_langday))

@bot.message_handler(commands=['today'])
def sendreg_message(message):      
    global english_only
    global russian_only
    timenow = (datetime.now()).strftime("%H:%M")
    if int(datetime.now().day)%2 == 0 or english_only is True:
        bot.send_message(
            chat_id = message.chat.id,
            text = 'Today is "English" day or english_only is enabled.\nСегодня день английского языка или этот режим был включен принудительно.\nServer time: '+timenow,
            reply_to_message_id = message.message_id
            )
    elif int(datetime.now().day)%2 != 0 or russian_only is True:
        bot.send_message(
            chat_id = message.chat.id,
            text = 'Today is "Russian" day or russian_only is enabled.\nСегодня день русского языка или этот режим был включен принудительно.\nServer time: '+timenow,
            reply_to_message_id = message.message_id
            )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text='autolangday is disabled.',
            reply_to_message_id = message.message_id
            )

@bot.message_handler(commands=['cooldown'])
def sendreg_message(message):      
    global cooldown
    global cooldown_nexttime
    if message.from_user.id == 87250032:
        if len(message.text) > 10: cooldown = int(message.text[10:len(message.text)])
        bot.send_message(message.chat.id,"Cooldown = "+str(cooldown)+" minutes\n cooldown_nexttime = "+ cooldown_nexttime.strftime("%H:%M") + "\n datetime now = "+ datetime.now().strftime("%H:%M"))


@bot.message_handler(content_types=["text"])
def checkall(message): 
    global reg_notify
    global english_only
    global russian_only
    global auto_langday
    global cooldown
    global cooldown_nexttime
    db_worker = SQLighter(config.database_name)
    if db_worker.UserExists(message.from_user.id,message.from_user.username) == 0 and reg_notify is True:
            bot.send_message(
                chat_id=message.chat.id, 
                text="We would like to know what is your native language, please make a registration via our Bot.", 
                reply_markup = markupregister,
                reply_to_message_id = message.message_id 
                )
    db_worker.close()
    if ((auto_langday is True and int(datetime.now().day)%2 == 0) or english_only is True) and (datetime.now() > cooldown_nexttime):
        ru_letters = round((len(re.findall('[а-яА-Я]', message.text)))/len(message.text),2)
        if  ru_letters > 0.4:
             bot.send_message(message.chat.id,"Hey! Today is English only day! ( " +str(ru_letters*100)+'% of Russian letters in the message.)',reply_to_message_id = message.message_id ) 
             cooldown_nexttime = datetime.now() + timedelta(minutes=cooldown)
    elif (russian_only is True or (auto_langday is True and int(datetime.now().day)%2 != 0))  and (datetime.now() > cooldown_nexttime):
        en_letters = round((len(re.findall('[a-zA-Z]', message.text)))/len(message.text),2)
        if  en_letters > 0.4:
             bot.send_message(message.chat.id,"Эй! Сегодня день русского языка! ( " +str(en_letters*100)+'% английских букв в сообщении.)',reply_to_message_id = message.message_id )
             cooldown_nexttime = datetime.now() + timedelta(minutes=cooldown)

if __name__ == '__main__':
    random.seed()
    bot.polling(none_stop=True)