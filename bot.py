# -*- coding: utf-8 -*-
"""
@author: luxnlex
"""
import telebot # pip3 install PyTelegramBotAPI==2.2.3
import random
import json
import os,sys
import settings

bot = telebot.TeleBot(settings.token)

script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
word_dict = {}

class Dict:
    def __init__(self, word):
        self.word = word
        self.translate = None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.chat.id in settings.admin:
        bot.reply_to(message, '''Добро пожаловать в бот для изучения английского языка!
Список доступных команд: 
/add - добавить слово и перевод в словарь
/train - тренировка
/getChatId - получить ID чата
''')
    else:
        bot.reply_to(message, '''Свяжитесь с администратором (''' + settings.admin_mail + ''') для добавления в группу администраторов проекта!
Выполните команду /getChatId и сообщите результат администратору!''')

@bot.message_handler(commands=['getChatId','getchatid'])
def get_chat_id(message):
    bot.reply_to(message,message.chat.id)

@bot.message_handler(commands=['add'])
def get_add(message):
    if message.chat.id in settings.admin:
        try:
            msg = bot.reply_to(message, "English word?")
            bot.register_next_step_handler(msg, get_word)
        except:
            bot.reply_to(message, 'Ошибка при добавлении в словарь! Проверьте корректность введенных значений!')
    else:
        bot.reply_to(message, 'Вы не являетесь администратором!')

def get_word(message):
    try:
        chat_id = message.chat.id
        word = message.text
        dictionary = Dict(word)
        word_dict[chat_id] = dictionary
        msg = bot.reply_to(message, 'Translate?')
        bot.register_next_step_handler(msg, get_translate)
    except:
        bot.reply_to(message, 'Ошибка при добавлении в словарь! Введите слово без пробелов, цифр и специальных символов.')

def get_translate(message):
    try:
        chat_id = message.chat.id
        translate = message.text
        dictionary = word_dict[chat_id]
        dictionary.translate = translate
        w1 = dictionary.word.upper()
        w2 = dictionary.translate.upper()
        if (w1.isalpha() and w2.isalpha()) == True:
            bot.reply_to(message, 'Добавлено слово: ' + str(dictionary.word) + '\nИ перевод: ' + str(dictionary.translate))
            user_db_file = script_dir + '/' + str(message.chat.id) + '.json'
            
            if os.path.exists(user_db_file):
                content_in_file = json.load(open(user_db_file,'r'))
                content_in_file['word'].append(w1)
                content_in_file['translate'].append(w2)
                content_in_file['error_counter'].append(0)
                json.dump(content_in_file,open(user_db_file,'w'))
            else:
                data = {"word":[w1], "translate":[w2], "error_counter":[0]}
                json.dump(data,open(user_db_file,'w'))
                bot.reply_to(message, 'Файл словаря создан!')
        else:
            bot.send_message(chat_id, 'Ошибка при добавлении в словарь! Введите слово без пробелов, цифр и специальных символов.')
    except:
        bot.reply_to(message, 'oooops')
        
@bot.message_handler(commands=['train'])
def get_train(message):        
    if message.chat.id in settings.admin:
        user_db_file = script_dir + '/' + str(message.chat.id) + '.json'
        if os.path.exists(user_db_file):
            try:
                chat_id = message.chat.id
                content_in_file = json.load(open(user_db_file,'r'))
                random_item = random.SystemRandom().choice(content_in_file['word'])
                dictionary = Dict(random_item)
                word_dict[chat_id] = dictionary
                msg = bot.reply_to(message, 'Введите перевод слова: ' + str(random_item))
                bot.register_next_step_handler(msg, check_word)
            except:
                bot.reply_to(message, 'Словарь пуст! Для использования функционала тренировки сначала добавьте слова в словарь командой /add <word>')
        else:
            data = {"word":[], "translate":[], "error_counter":[]}
            json.dump(data,open(user_db_file,'w'))
            bot.reply_to(message, 'Файл словаря создан!')
    else:
        bot.reply_to(message, 'Вы не являетесь администратором!')
        
def check_word(message):
    if message.chat.id in settings.admin:
        try:
            user_db_file = script_dir + '/' + str(message.chat.id) + '.json'
            chat_id = message.chat.id
            translate = message.text
            dictionary = word_dict[chat_id]
            dictionary.translate = translate
            content_in_file = json.load(open(user_db_file,'r'))
            index_word = content_in_file['word'].index(dictionary.word)
            correct_translate = content_in_file['translate'][index_word]
            if str(correct_translate.upper()) == str(dictionary.translate.upper()):
                bot.reply_to(message, 'Вы угадали!')
            else:
                content_in_file['error_counter'][index_word] += 1
                json.dump(content_in_file,open(user_db_file,'w'))
                bot.reply_to(message, 'Неправильный ответ! Количество неправильных ответов для слова ' + str(dictionary.word) + ': ' + 
                str(content_in_file['error_counter'][index_word]) + '''!
Правильный ответ: ''' + str(correct_translate.upper()))
        except:
            bot.reply_to(message, 'oooops')

bot.polling()