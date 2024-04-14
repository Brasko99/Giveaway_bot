import telebot
from telebot import types
import os
import random
import datetime
import time
import urllib.request
import threading
import re
import pickle


os.environ['FILE_EXTENSION'] = 'jpg'
os.environ['CURRENT_FOLDER_NAME'] = 'MyLot3'
os.environ['CHAT_ID'] = '1234567899'
###Подключаем бота
TOKEN = '7100567356:AAE3k61dzZEi99QHSMStfxC0SU3HRPyPa_k'
bot = telebot.TeleBot(TOKEN)
###Создаем кнопки под клавиатурой
markup = types.ReplyKeyboardMarkup()
btn1 = types.KeyboardButton("Создать розыгрыш")
btn2 = types.KeyboardButton("Мои розыгрыши")
markup.row(btn1, btn2)
btn3 = types.KeyboardButton("Мои каналы")
btn4 = types.KeyboardButton("Техническая поддержка")
markup.row(btn3, btn4)
###Получаем путь к актуальной директории
current_directory1 = os.path.dirname(os.path.realpath(__file__))
# Добавляем к нему папку LOTS
current_directory = os.path.join(current_directory1, "LOTS")
###Создаем папку LOTS если её нет
if not os.path.exists('LOTS'):
    os.mkdir('LOTS')
###Создаем файл MyChannels если его нет
filename = "MyChannels.txt"
if not os.path.exists(filename):
    with open(filename, 'w', encoding='utf-8'):
        pass      
###Подгружаем список админов    
with open(f'./admins.txt', 'r') as file:
    lines = [line.strip() for line in file]
    admins = [int(line) for line in lines]


@bot.message_handler(func=lambda message: message.from_user.id not in admins)
def handle_message(message):
    bot.reply_to(message, "Извините, вы не имеете доступа к этому боту.")


###Обработчик команды "Старт" 
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"👋 Здравствуйте!\nДанный бот поможет Вам провести розыгрыш на канале, в чате или группе.\nГотовы создать новый розыгрыш?\n\nДля настройки списка админов напишите /admins", reply_markup=markup)


###Добавление/удаление администраторов
@bot.message_handler(commands=["admins"])
def admin_main(message):
    bot.send_message(message.chat.id, '🍕 Выберите функцию:\n\n/new_admin - добавить администратора\n/delete_admin - убрать администратора\n/show_admins - показать всех администраторов')


###Добавить администратора
@bot.message_handler(commands=["new_admin"])
def new_admin(message):
    bot.send_message(message.chat.id, 'Чтобы добавить администратора Вам понадобится его ID.\nЕсли человек, которого вы ходите добавить, не знает свой ID - перешите ему сообщение ниже.\nЧтобы добавить человека в список админов отправьте мне его ID\n◽️ Пример:\n\n1275473197.')
    bot.send_message(message.chat.id, 'Чтобы узнать свой Telegram ID, вам необходимо обратиться к боту, который может отобразить ваш идентификатор. Например, вы можете воспользоваться ботом `userinfobot`.\n\nВот как это сделать:\n\n1. Откройте Telegram и найдите бота `userinfobot`, либо [нажмите здесь](https://t.me/userinfobot), чтобы перейти к нему напрямую.\n2. Нажмите кнопку "Start" или отправьте боту любое сообщение.\n3. Бот `userinfobot` предоставит вам информацию о вашем Telegram ID, а также другие данные, такие как ваше имя пользователя и имя.')
    bot.register_next_step_handler(message, process_admin_id)
def process_admin_id(message):
    admin_id = message.text.strip()
    # Проверяем, является ли введенное значение целым числом и имеет ли длину 10 цифр
    if not is_valid_admin_id(admin_id):
        bot.send_message(message.chat.id, 'Неправильный формат ID. Пожалуйста, введите корректный Telegram ID, состоящий из 10 цифр.')
        return new_admin(message)
    # Проверяем, существует ли файл с администраторами
    if not os.path.exists('admins.txt'):
        with open('admins.txt', 'w'):  # Создаем файл, если его нет
            pass
    # Проверяем, добавлен ли уже этот администратор
    with open('admins.txt', 'r', encoding='utf-8') as file:
        if admin_id in file.read():
            bot.send_message(message.chat.id, f'Администратор с ID {admin_id} уже есть в списке.')
            return
    # Если администратора еще нет в списке, добавляем его
    with open('admins.txt', 'a', encoding='utf-8') as file:
        file.write(f"{admin_id}\n")
    bot.send_message(message.chat.id, f'Администратор с ID {admin_id} добавлен в список.')
def is_valid_admin_id(admin_id):
    return admin_id.isdigit() and len(admin_id) == 10


###Удалить администратора из списка
@bot.message_handler(commands=["delete_admin"])
def delete_admin(message):
    bot.send_message(message.chat.id, 'Чтобы удалить администратора Вам понадобится его ID.\nВы можете скопировать его из списка /showadmins и оптправить мне.\n◽️ Пример:\n\n1275473197.')
    bot.register_next_step_handler(message, delete_admin2)
def delete_admin2(message):
    del_admin = message.text.strip()
    # Проверяем, является ли введенное значение целым числом и имеет ли длину 10 цифр
    if not is_valid_admin_id(del_admin):
        bot.send_message(message.chat.id, 'Неправильный формат ID. Пожалуйста, введите корректный Telegram ID, состоящий из 10 цифр.')
        return delete_admin(message)
    # Проверяем, существует ли файл с администраторами
    if not os.path.exists('admins.txt'):
        bot.send_message(message.chat.id, 'Список администраторов пуст.')
        return
    with open('admins.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    # Проверяем, существует ли администратор с таким ID
    if del_admin not in [line.strip() for line in lines]:
        bot.send_message(message.chat.id, f'Администратора с ID {del_admin} нет в списке.')
        return
    # Удаляем администратора с указанным ID из списка
    with open('admins.txt', 'w', encoding='utf-8') as file:
        for line in lines:
            if line.strip() != del_admin:
                file.write(line)
    bot.send_message(message.chat.id, f'Администратор с ID {del_admin} удален из списка.')
def is_valid_admin_id(admin_id):
    return admin_id.isdigit() and len(admin_id) == 10


###Показать список администраторов
@bot.message_handler(commands=["show_admins"])
def show_admins(message):
    with open('admins.txt', 'r', encoding='utf-8') as file:
        bot.send_message(message.chat.id, f"🍕 Список администраторов:\n\n{', '.join([line.strip() for line in file])}\n\n/admins - назад")
    admin_main(message)


###Список сохраненных розыгрышей и действия с ними
@bot.message_handler(commands=['My_Lots'])
def My_lots(message):
    folders = [folder for folder in os.listdir(current_directory) if os.path.isdir(os.path.join(current_directory, folder))]
    if len(folders) == 0:
        bot.send_message(message.chat.id, "У вас нет сохраненных розыгрышей. Чтобы добавить розыгрыш нажмите соответствующую кнопку под клавиатурой.", reply_markup=markup)
    else:
        spisok = "Список Ваших розыгрышей:\n\n"
        for folder in folders:
            with open(f'./LOTS/{folder}/message_data.pkl', 'rb') as file:
                text = pickle.load(file)
            spisok += '▫️' + folder + ': "' + text[:30] + '..."\n\n'
        keyboard = types.InlineKeyboardMarkup()
        knopka = types.InlineKeyboardButton(text="Открыть параметры розыгрыша", callback_data='Open_Lot')
        knopka2 = types.InlineKeyboardButton(text="Удалить розыгрыш", callback_data='Delete_Lot')
        keyboard.add(knopka)
        keyboard.add(knopka2)
        bot.send_message(message.chat.id, spisok, reply_markup=keyboard)
def Open_lot(message):
    os.environ['CURRENT_FOLDER_NAME'] = message.text
    lot = message.text
    with open(f'./LOTS/{lot}/description.txt', 'r') as description_file:
        data = description_file.read()
    values = data.split('   ,')
    publication_date = values[3]
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    if "RightNow" in publication_date:
        status = f'Опубликовано'  
    elif current_time < publication_date:
        status = f'\nБудет опубликовано {publication_date}'
    else:
        status = f'Опубликовано'
    winners_value = values[1]
    winners_value1 = winners_value.split(':')
    winners_value2 = winners_value1[0]    
    way_of_ending = values[4]
    if 'participants' in way_of_ending:
        way_of_ending1 = way_of_ending.split("  ")
        way_of_ending2 = str(f'\nПо регистрации {way_of_ending1[0]} участников')
    else:
        way_of_ending1 = way_of_ending.split("  ")
        way_of_ending2 = str(f'\nВ указанное ({way_of_ending1[0]}) время')    
    keyboard = types.InlineKeyboardMarkup()
    knopka = types.InlineKeyboardButton(text="Завершить розыгрыш", callback_data='Finish_Lot')
    knopka1 = types.InlineKeyboardButton(text="Удалить розыгрыш", callback_data='Cansel_sure')
    knopka2 = types.InlineKeyboardButton(text="Назад", callback_data='Back_to_My_Lots')
    keyboard.add(knopka)
    keyboard.add(knopka1)
    keyboard.add(knopka2)
    with open(f'./LOTS/{lot}/members.txt', 'r') as members_file:
        members = members_file.read()    
    members_count = members.count('@')    
    if status == "Опубликовано":
        with open(f'./LOTS/{lot}/link.txt', 'r') as link_file:
            link = link_file.read()
        status = status + f"\nСообщение с розыгрышем:\n{link}"
    bot.send_message(message.chat.id, f'◽️ Статус: {status}\n◽️ Количество участников: {members_count}\n◽️ Количество победителей: {winners_value2}\n◽️ Завершится: {way_of_ending2}', reply_markup=keyboard)
def Delete_Lot(message):
    lot = message.text
    try:
        path = f"{current_directory}/{lot}"
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(path)
        bot.send_message(message.chat.id, 'Розыгрыш успешно удален!\n\nВы можете создать новый, используя кнопки под клавиатурой.', reply_markup=markup)
    except Exception:
        bot.send_message(message.chat.id, 'Такого розыгрыша нет или название введено неправильно.\nПопробуйте ещё раз. Пример названия:\n\nMyLot1')
        bot.register_next_step_handler(message, Delete_Lot)
def finish_lot_now(message):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')
    with open(f'./LOTS/{folder_name}/members.txt', 'r') as members_file:
        members = members_file.read()
    with open(f'./LOTS/{folder_name}/description.txt', 'r',  encoding='utf-8') as description_file:
        data = description_file.read()
    with open(f'./LOTS/{folder_name}/link.txt', 'r') as link_file:
        link = link_file.read()
    values = data.split('   ,')
    winners_value = values[1]
    winners = int(winners_value.split(':')[0])  
    members_list = members.split(',')
    members_list = members_list[:-1]
    winners_list = random.sample(members_list, winners)
    link_data = link.split('/')
    chat_id = str('@' + link_data[3])
    message_id = link_data[4]
    try:
        bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
        text = ''
        keyboard = types.InlineKeyboardMarkup()
        knopka = types.InlineKeyboardButton(text="Опубликую сам", callback_data='Publish_results_by_user')
        knopka1 = types.InlineKeyboardButton(text="Опубликовать ботом", callback_data='Publish_results_by_bot')
        keyboard.add(knopka)
        keyboard.add(knopka1)
        for winner in winners_list:
            text += winner + '\n' 
        bot.send_message(message.chat.id, f'Cписок победителей:\n\n{text}\nКнопка регистрации в конкурсе была удалена из под сообщения о розыгрыше. Выберите вариант публикации результата кнопкой ниже:', reply_markup=keyboard)    
    except Exception:
        text = ''
        keyboard = types.InlineKeyboardMarkup()
        knopka = types.InlineKeyboardButton(text="Опубликую сам", callback_data='Publish_results_by_user')
        knopka1 = types.InlineKeyboardButton(text="Опубликовать ботом", callback_data='Publish_results_by_bot')
        keyboard.add(knopka)
        keyboard.add(knopka1)
        for winner in winners_list:
            text += winner + '\n' 
        bot.send_message(message.chat.id, f'Cписок победителей:\n\n{text}\nКнопка регистрации в конкурсе была удалена из под сообщения о розыгрыше. Выберите вариант публикации результата кнопкой ниже:', reply_markup=keyboard)


###Настройка публикации от имени бота
def Publish_results_by_bot(message):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')    
    try:
        file_id = message.photo[-1].file_id if message.photo else message.video.file_id if message.video else message.document.file_id
        file_info = bot.get_file(file_id)        
        file_path = file_info.file_path
        url = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
        file_extension = file_info.file_path.split('.')[-1]
        os.environ['FILE_EXTENSION'] = file_extension
        urllib.request.urlretrieve(url, f'./LOTS/{folder_name}/Finish_file.{file_extension}')    
        description = str(message.caption) if message.caption else 'No_Caption'
        with open(f'./LOTS/{folder_name}/Finish_message_data.pkl', 'wb') as file:
            pickle.dump(description, file)
        bot.send_message(message.chat.id, "✅ Медиафайл и описание сохранены!")
    except Exception:
        description = str(message.text)
        with open(f'./LOTS/{folder_name}/Finish_message_data.pkl', 'wb') as file:
            pickle.dump(description, file)
        bot.send_message(message.chat.id, "✅ Текст сохранен!")
    keyboard = types.InlineKeyboardMarkup()
    knopka2 = types.InlineKeyboardButton(text="Опубликовать в канале/каналах из списка", callback_data='Finish_Channel_for_publish_from_list')
    knopka = types.InlineKeyboardButton(text="Добавить канал в список", callback_data='Finish_Add_channel_to_list')
    keyboard.add(knopka)
    with open(f'./MyChannels.txt', 'r') as description_file:
        data = description_file.read()
        if not data:
            bot.send_message(message.chat.id, "У вас нет добавленных каналов.\nЧтобы добавить канал нажмите нопку ниже и следуйте инструкции", reply_markup=keyboard)
        else:
            keyboard.add(knopka2)
            channels = data.split(",")
            spisok = ""
            if len(channels) == 1:
                spisok = channels[0].rstrip(',')
            else:
                for channel in channels:
                    spisok = spisok + channel + "\n"
            bot.send_message(message.chat.id, f'В каком канале публикуем результаты?\nВот список ваших каналов:\n{spisok}', reply_markup=keyboard)
def Finish_Channel_for_publish_from_list(message):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')    
    chat_list = message.text
    with open(f'./LOTS/{folder_name}/Finish_description.txt', 'w', encoding='utf-8') as channels_file:
        channels_file.write(f'{chat_list}   ,')    
        bot.send_message(message.chat.id, '✅ Ваш выбор сохранен')
        Finish_publish_time(message)
def Finish_Add_channel_to_list(message):
    chat_id = message.text
    bot_info = bot.get_me()
    bot_user_id = bot_info.id
    keyboard = types.InlineKeyboardMarkup()
    knopka = types.InlineKeyboardButton(text="Добавить ещё один канал", callback_data='Finish_Add_channel_to_list')
    knopka2 = types.InlineKeyboardButton(text="Назад к списку", callback_data='Finish_Back_to_list')
    keyboard.add(knopka)
    keyboard.add(knopka2)
    if '@' in chat_id:
        try: 
            chat_member = bot.get_chat_member(chat_id, bot_user_id)
            if chat_member.status == 'administrator':
                with open(f'./MyChannels.txt', 'a', encoding='utf-8') as description_file:
                    description_file.write(chat_id+",")
                bot.send_message(message.chat.id, f"Канал успешно добавлен в список ваших каналов!", reply_markup=keyboard)
            else:
                bot.reply_to(message, 'Бот не является администратором канала.\nПожалуйста, назначьте его администратором и отправьте его имя ещё раз.')
                bot.register_next_step_handler(message, Add_channel_to_list)
        except Exception:
            bot.reply_to(message, 'Бот не является администратором канала.\nПожалуйста, назначьте его администратором и отправьте его имя ещё раз.')
            bot.register_next_step_handler(message, Add_channel_to_list)
    else:
        bot.send_message(message.chat.id, 'Неправльный формат!\nНужный формат: @channelname\n\nПожалуйста введите в нужном формате:')               
        bot.register_next_step_handler(message, Add_channel_to_list)
def Finish_back_to_list(message):
    keyboard = types.InlineKeyboardMarkup()
    knopka2 = types.InlineKeyboardButton(text="Опубликовать в канале/каналах из списка", callback_data='Finish_Channel_for_publish_from_list')
    knopka = types.InlineKeyboardButton(text="Добавить канал в список", callback_data='Finish_Add_channel_to_list')
    keyboard.add(knopka)
    with open(f'./MyChannels.txt', 'r') as description_file:
        data = description_file.read()
        if not data:
            bot.send_message(message.chat.id, "У вас нет добавленных каналов.\nЧтобы добавить канал нажмите нопку ниже и следуйте инструкции", reply_markup=keyboard)
        else:
            keyboard.add(knopka2)
            channels = data.split(",")
            spisok = ""
            if len(channels) == 1:
                spisok = channels[0].rstrip(',')
            else:
                for channel in channels:
                    spisok = spisok + channel + "\n"
            bot.send_message(message.chat.id, f'В каком канале публикуем розыгрыш?\nВот список ваших каналов:\n{spisok}', reply_markup=keyboard)


###Настройка времения публикации итогов от бота
def Finish_publish_time(message):
    keyboard5 = types.InlineKeyboardMarkup()
    knopka5 = types.InlineKeyboardButton(text="Прямо сейчас", callback_data='Finish_time_right_now')
    knopka6 = types.InlineKeyboardButton(text="Запланировать время публикации", callback_data='Finish_time_input')
    keyboard5.add(knopka5)
    keyboard5.add(knopka6)
    bot.send_message(message.chat.id, '⏰ Когда нужно опубликовать результаты?', reply_markup=keyboard5)
def Finish_set_publish_time(message):
    bot.send_message(message.chat.id, '⏰ Когда нужно опубликовать результаты? (Укажите время в формате дд.мм.гг чч:мм)\n\nБот живет по времени (GMT+3) Москва, Россия')
    now = datetime.datetime.now()
    ten_minutes = now + datetime.timedelta(minutes=10)
    one_hour = now + datetime.timedelta(hours=1)
    one_day = now + datetime.timedelta(days=1)
    one_week = now + datetime.timedelta(weeks=1)
    date_format = "%Y-%m-%d"
    time_format = "%H:%M"
    ten_minutes_formatted = ten_minutes.strftime(f"{date_format} {time_format}")
    one_hour_formatted = one_hour.strftime(f"{date_format} {time_format}")
    one_day_formatted = one_day.strftime(f"{date_format} {time_format}")
    one_week_formatted = one_week.strftime(f"{date_format} {time_format}")
    bot.send_message(message.chat.id, f'Примеры:\n\n{ten_minutes_formatted} - через 10 минут\n{one_hour_formatted} - через час\n{one_day_formatted} - через день\n{one_week_formatted} - через неделю')
    bot.register_next_step_handler(message, Finish_set_publish_time2)
def Finish_set_publish_time2(message):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')
    variable_value = message.text
    current_time = datetime.datetime.now()
    try:
        variable_time = datetime.datetime.strptime(variable_value, "%Y-%m-%d %H:%M")
        if variable_time > current_time:
            with open(f'./LOTS/{folder_name}/Finish_description.txt', 'a', encoding='utf-8') as channels_file:
                channels_file.write(f'{message.text}   ,')    
            bot.send_message(message.chat.id, '✅ Время сохранено')
            Finish_check_final_post(message)
        else:
            bot.send_message(message.chat.id, "❗️ Вы ввели время, которое уже прошло.\n\nВнимательно осмотрите пример и попробуйте ещё раз")
            Finish_set_publish_time(message)
    except Exception:
        bot.send_message(message.chat.id, "❗️ Вы ввели неправильный формат времени.\n\nВнимательно осмотрите пример и попробуйте ещё раз.")
        Finish_set_publish_time(message)


###Проверка публикации итогов от бота
def Finish_check_final_post(message):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')
    with open(f'./LOTS/{folder_name}/Finish_description.txt', 'r') as file:
        data = file.read()
    values = data.split('   ,')
    with open(f'./LOTS/{folder_name}/Finish_message_data.pkl', 'rb') as file:
        text = pickle.load(file)
    publication_channel = values[0]
    publication_date =  values[1]
    if 'RightNow' in publication_date:
        publication_date = str('Сразу после окончания настройки')
    file_extension = os.environ.get('FILE_EXTENSION')
    try:
        image_path = f'./LOTS/{folder_name}/Finish_file.{file_extension}'  # Укажите путь к изображению
        photo = open(image_path, 'rb')
        bot.send_photo(message.chat.id, photo, caption=text)
        photo.close()
    except Exception:
        bot.send_message(message.chat.id, f"{text}")
    keyboard5 = types.InlineKeyboardMarkup()
    knopka5 = types.InlineKeyboardButton(text="Подтвердить пост", callback_data='Finish_save_post')
    knopka6 = types.InlineKeyboardButton(text="Отмена", callback_data='Finish_cansel_sure')
    keyboard5.add(knopka5)
    keyboard5.add(knopka6)
    bot.send_message(message.chat.id, f'🧮 Внимательно перепроверьте пост\n\n🔚 Результаты опубликуются:\n{publication_date}\n🔚 В канале:\n{publication_channel}', reply_markup=keyboard5)


###Сохранить и опубликовать пост от бота
def Finish_save_post(message):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')
    with open(f'./LOTS/{folder_name}/Finish_description.txt', 'r') as file:
        data = file.read()
    values = data.split('   ,')
    publication_date =  values[1]
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    HM_users = 9999999
    if "RightNow" in publication_date:
        now = datetime.datetime.now()
        publication_date = now + datetime.timedelta(minutes=1)
        current_time = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
        delay = (publication_date - current_time).total_seconds()
        thread = threading.Thread(target=Finish_send_message_to_time, args=(delay, HM_users,))
        thread.start()
        status = f'будет  опубликован в течение минуты'  
    elif current_time < publication_date:
        current_time = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
        publication_date = publication_date + ':00'
        publication_date = datetime.datetime.strptime(publication_date, "%Y-%m-%d %H:%M:%S")
        delay = (publication_date - current_time).total_seconds()
        thread = threading.Thread(target=Finish_send_message_to_time, args=(delay, HM_users,))
        thread.start()
        status = f'будет опубликован {publication_date}'
    else:
        status = 'Не опубликован. Обратитесь в поддержку!'
    bot.send_message(message.chat.id, f'✅ Пост сохранен и {status}.\n\nДля вызова меню напишите /start')


#Уточнение удаления поста
def Finish_cancel_sure(message):
    keyboard = types.InlineKeyboardMarkup()
    knopka = types.InlineKeyboardButton(text="Вернуться к розыгрышу", callback_data='Finish_back_to_post')
    knopka2 = types.InlineKeyboardButton(text="Удалить пост", callback_data='Finish_cansel')
    keyboard.add(knopka)
    keyboard.add(knopka2)
    bot.send_message(message.chat.id, 'Вы уверены что хотите удалить созданный пост?', reply_markup=keyboard)


#Удаление поста
def Finish_cancel(message):
    path = f"{current_directory}/{os.environ.get('CURRENT_FOLDER_NAME')}"
    try:
        files = os.listdir(path)
        for file in files:
            file_path = os.path.join(path, file)
            os.remove(file_path)
        My_lots(message)
    except Exception:
        My_lots(message)

    
    
    
    
    
    path = f"{current_directory}/{os.environ.get('CURRENT_FOLDER_NAME')}"
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(path)
    bot.send_message(message.chat.id, 'Розыгрыш успешно удален!\n\nВы можете создать новый, используя кнопки под клавиатурой.', reply_markup=markup)


###Публикация поста
def Finish_send_message_to_time(delay, HM_users):
    time.sleep(delay)
    HM = HM_users
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')
    with open(f'./LOTS/{folder_name}/Finish_description.txt', 'r',  encoding='utf-8') as file:
        data = file.read()
    with open(f'./LOTS/{folder_name}/Finish_message_data.pkl', 'rb') as file:
        text = pickle.load(file) 
    file_extension = os.environ.get('FILE_EXTENSION')
    matches = re.findall(r'@[\w]+', data)
    channels = matches
    if len(channels) == 1:
        channel = matches[0]
        try:
            channel = channel.strip()
            image_path = f'./LOTS/{folder_name}/Finish_file.{file_extension}'  # Укажите путь к изображению
            photo = open(image_path, 'rb')
            bot.send_photo(channel, photo, caption=text)
            photo.close()
        except Exception:
            bot.send_message(channel, f"{text}")
    else:
        for channel in channels:
            try:
                image_path = f'./LOTS/{folder_name}/Finish_file.{file_extension}'  # Укажите путь к изображению
                photo = open(image_path, 'rb')
                bot.send_photo(channel, photo, caption=text)
                photo.close()        
            except Exception:
                bot.send_message(channel, f"{text}")


###Список добавленных каналов
@bot.message_handler(commands=['My_channels'])
def My_channels_list(message):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Добавить канал", callback_data='Add_channel_to_list')
    keyboard.add(btn1)
    with open(f'./MyChannels.txt', 'r') as description_file:
        data = description_file.read()
        if not data:
            bot.send_message(message.chat.id, "У вас нет добавленных каналов.\nЧтобы добавить канал нажмите нопку ниже и следуйте инструкции", reply_markup=keyboard)
        else:
            channels = data.split(",")
            spisok = ""
            if len(channels) == 1:
                spisok = channels[0].rstrip(',')
            else:
                for channel in channels:
                    spisok = spisok + channel + "\n"
            bot.send_message(message.chat.id, f"Список ваших каналов:\n{spisok}Чтобы добавить канал нажмите нопку ниже и следуйте инструкции", reply_markup=keyboard)
def add_new_channel(message):
    chat_id = message.text
    bot_info = bot.get_me()
    bot_user_id = bot_info.id
    if '@' in chat_id:
        try: 
            chat_member = bot.get_chat_member(chat_id, bot_user_id)
            if chat_member.status == 'administrator':
                with open(f'./MyChannels.txt', 'a', encoding='utf-8') as description_file:
                    description_file.write(chat_id+",")
                bot.send_message(message.chat.id, f"Канал успешно добавлен в список ваших каналов!\nПора устраивать розыгрыш!", reply_markup=markup)
            else:
                bot.reply_to(message, 'Бот не является администратором канала.\nПожалуйста, назначьте его администратором и отправьте его имя ещё раз.')
                bot.register_next_step_handler(message, add_new_channel)
        except Exception:
            bot.reply_to(message, 'Бот не является администратором канала.\nПожалуйста, назначьте его администратором и отправьте его имя ещё раз.')
            bot.register_next_step_handler(message, add_new_channel)
    else:
        bot.send_message(message.chat.id, 'Неправльный формат!\nНужный формат: @channelname\n\nПожалуйста введите в нужном формате:')               
        bot.register_next_step_handler(message, add_new_channel)


###Прием файлов для розыгрыша и выбор кнопки для розыгрыша
def files_for_lot(message):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')    
    try:
        file_id = message.photo[-1].file_id if message.photo else message.video.file_id if message.video else message.document.file_id
        file_info = bot.get_file(file_id)        
        file_path = file_info.file_path
        url = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
        file_extension = file_info.file_path.split('.')[-1]
        os.environ['FILE_EXTENSION'] = file_extension
        urllib.request.urlretrieve(url, f'./LOTS/{folder_name}/file.{file_extension}')    
        description = str(message.caption) if message.caption else 'No_Caption'
        with open(f'./LOTS/{folder_name}/message_data.pkl', 'wb') as file:
            pickle.dump(description, file)
        bot.send_message(message.chat.id, "✅ Медиафайл и описание сохранены!")
    except Exception:
        description = str(message.text)
        with open(f'./LOTS/{folder_name}/message_data.pkl', 'wb') as file:
            pickle.dump(description, file)
        # Отправка подтверждающего сообщения
        bot.send_message(message.chat.id, "✅ Текст сохранен!")
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Участвую!", callback_data='btn_ver1')
    btn2 = types.InlineKeyboardButton(text="Участвовать", callback_data='btn_ver2')
    btn3 = types.InlineKeyboardButton(text="Принять участие", callback_data='btn_ver3')
    btn4 = types.InlineKeyboardButton(text="Написать свой вариант", callback_data='btn_ver4')
    keyboard.add(btn1)
    keyboard.add(btn2)
    keyboard.add(btn3)
    keyboard.add(btn4)    
    bot.send_message(message.chat.id, '📰 Выберите один из вариантов кнопки для участия в розыгрыше:', reply_markup=keyboard)


###Добавлем кнопку с текстом из сообщения
def add_button_text(message):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')
    with open(f'./LOTS/{folder_name}/description.txt', 'w', encoding='utf-8') as description_file:
        description_file.write(f'{message.text}   ,')
    bot.send_message(message.chat.id, '✅ Текст кнопки сохранен')
    chose_channels_subscribe(message)


###Определяем каналы, на которые необходимо подписаться для участия в розыгрыше
def chose_channels_subscribe(message): 
    keyboard = types.InlineKeyboardMarkup()
    knopka2 = types.InlineKeyboardButton(text="Конкурс без подписок", callback_data='Without_Subscribe')
    knopka3 = types.InlineKeyboardButton(text="Добавить каналы", callback_data='Add_channels')
    keyboard.add(knopka3)
    keyboard.add(knopka2)
    with open(f'./MyChannels.txt', 'r') as description_file:
        data = description_file.read()
        if not data:
            bot.send_message(message.chat.id, "У вас нет добавленных каналов.\nЧтобы добавить канал нажмите нопку ниже и следуйте инструкции", reply_markup=keyboard)
        else:
            keyboard2 = types.InlineKeyboardMarkup()
            knopka = types.InlineKeyboardButton(text="Выбрать из списка", callback_data='Channel_for_subscribe_from_list')
            knopka2 = types.InlineKeyboardButton(text="Конкурс без подписок", callback_data='Without_Subscribe')
            knopka3 = types.InlineKeyboardButton(text="Добавить каналы", callback_data='Add_channels')
            keyboard2.add(knopka)
            keyboard2.add(knopka3)
            keyboard2.add(knopka2)
            channels = data.split(",")
            spisok = ""
            if len(channels) == 1:
                spisok = channels[0].rstrip(',')
            else:
                for channel in channels:
                    spisok = spisok + channel + "\n"
                bot.send_message(message.chat.id, f'📊 Список Ваших каналов:\n\n{spisok}Выберите каналы, подписка на которые будет обязательной для участия в конкурсе:', reply_markup=keyboard2)
def add_more_subscribe_channels(message):
    chat_id = message.text
    bot_info = bot.get_me()
    bot_user_id = bot_info.id
    keyboard = types.InlineKeyboardMarkup()
    knopka = types.InlineKeyboardButton(text="Добавить ещё один канал", callback_data='Add_channels')
    knopka2 = types.InlineKeyboardButton(text="Назад к списку", callback_data='Back_to_list1')
    keyboard.add(knopka)
    keyboard.add(knopka2)
    if '@' in chat_id:
        try: 
            chat_member = bot.get_chat_member(chat_id, bot_user_id)
            if chat_member.status == 'administrator':
                with open(f'./MyChannels.txt', 'a', encoding='utf-8') as description_file:
                    description_file.write(chat_id+",")
                bot.send_message(message.chat.id, f"Канал успешно добавлен в список ваших каналов!", reply_markup=keyboard)
            else:
                bot.reply_to(message, 'Бот не является администратором канала.\nПожалуйста, назначьте его администратором и отправьте его имя ещё раз.')
                bot.register_next_step_handler(message, add_more_subscribe_channels)
        except Exception:
            bot.reply_to(message, 'Бот не является администратором канала.\nПожалуйста, назначьте его администратором и отправьте его имя ещё раз.')
            bot.register_next_step_handler(message, add_more_subscribe_channels)
    else:
        bot.send_message(message.chat.id, 'Неправльный формат!\nНужный формат: @channelname\n\nПожалуйста введите в нужном формате:')               
        bot.register_next_step_handler(message, add_more_subscribe_channels)
def chose_from_list(message):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')    
    chat_list = message.text
    with open(f'./LOTS/{folder_name}/channels.txt', 'w', encoding='utf-8') as channels_file:
        channels_file.write(f'{chat_list}   ,')    
        bot.send_message(message.chat.id, '✅ Ваш выбор сохранен')
        how_much_winners(message)


###Определяем сколько победителей нужно выбрать боту
def how_much_winners(message):
    bot.send_message(message.chat.id, '🧮 Сколько победителей выбрать боту?\n\nВведите число:')
    bot.register_next_step_handler(message, how_much_winners2)
def how_much_winners2(message):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')
    with open(f'./LOTS/{folder_name}/description.txt', 'a', encoding='utf-8') as channels_file:
            channels_file.write(f'{message.text}:winner   ,')    
    bot.send_message(message.chat.id, '✅ Количество победителей сохранено')
    publish_channel(message)        


###Выбираем канал для публикации розыгрыша
def publish_channel(message):
    keyboard = types.InlineKeyboardMarkup()
    knopka2 = types.InlineKeyboardButton(text="Опубликовать в канале/каналах из списка", callback_data='Channel_for_publish_from_list')
    knopka = types.InlineKeyboardButton(text="Добавить канал в список", callback_data='Add_channel_to_list1')
    keyboard.add(knopka)
    with open(f'./MyChannels.txt', 'r') as description_file:
        data = description_file.read()
        if not data:
            bot.send_message(message.chat.id, "У вас нет добавленных каналов.\nЧтобы добавить канал нажмите нопку ниже и следуйте инструкции", reply_markup=keyboard)
        else:
            keyboard.add(knopka2)
            channels = data.split(",")
            spisok = ""
            if len(channels) == 1:
                spisok = channels[0].rstrip(',')
            else:
                for channel in channels:
                    spisok = spisok + channel + "\n"
            bot.send_message(message.chat.id, f'🗓 В каком канале публикуем розыгрыш?\nВот список ваших каналов:\n{spisok}', reply_markup=keyboard)
def Channel_for_publish_from_list(message):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')    
    chat_list = message.text
    with open(f'./LOTS/{folder_name}/description.txt', 'a', encoding='utf-8') as channels_file:
        channels_file.write(f'{chat_list}   ,')    
        bot.send_message(message.chat.id, '✅ Ваш выбор сохранен')
        publish_time(message)
def Add_channel_to_list(message):
    chat_id = message.text
    bot_info = bot.get_me()
    bot_user_id = bot_info.id
    keyboard = types.InlineKeyboardMarkup()
    knopka = types.InlineKeyboardButton(text="Добавить ещё один канал", callback_data='Add_channel_to_list1')
    knopka2 = types.InlineKeyboardButton(text="Назад к списку", callback_data='Back_to_list')
    keyboard.add(knopka)
    keyboard.add(knopka2)
    if '@' in chat_id:
        try: 
            chat_member = bot.get_chat_member(chat_id, bot_user_id)
            if chat_member.status == 'administrator':
                with open(f'./MyChannels.txt', 'a', encoding='utf-8') as description_file:
                    description_file.write(chat_id+",")
                bot.send_message(message.chat.id, f"Канал успешно добавлен в список ваших каналов!", reply_markup=keyboard)
            else:
                bot.reply_to(message, 'Бот не является администратором канала.\nПожалуйста, назначьте его администратором и отправьте его имя ещё раз.')
                bot.register_next_step_handler(message, Add_channel_to_list)
        except Exception:
            bot.reply_to(message, 'Бот не является администратором канала.\nПожалуйста, назначьте его администратором и отправьте его имя ещё раз.')
            bot.register_next_step_handler(message, Add_channel_to_list)
    else:
        bot.send_message(message.chat.id, 'Неправльный формат!\nНужный формат: @channelname\n\nПожалуйста введите в нужном формате:')               
        bot.register_next_step_handler(message, Add_channel_to_list)


###Выбираем время публикации
def publish_time(message):
    keyboard5 = types.InlineKeyboardMarkup()
    knopka5 = types.InlineKeyboardButton(text="Прямо сейчас", callback_data='Time_right_now')
    knopka6 = types.InlineKeyboardButton(text="Запланировать время публикации", callback_data='Time_input')
    keyboard5.add(knopka5)
    keyboard5.add(knopka6)
    bot.send_message(message.chat.id, '⏰ Когда нужно опубликовать розыгрыш?', reply_markup=keyboard5)
def set_publish_time(message):
    bot.send_message(message.chat.id, '⏰ Когда нужно опубликовать розыгрыш? (Укажите время в формате дд.мм.гг чч:мм)\n\nБот живет по времени (GMT+3) Москва, Россия')
    now = datetime.datetime.now()
    ten_minutes = now + datetime.timedelta(minutes=10)
    one_hour = now + datetime.timedelta(hours=1)
    one_day = now + datetime.timedelta(days=1)
    one_week = now + datetime.timedelta(weeks=1)
    date_format = "%Y-%m-%d"
    time_format = "%H:%M"
    ten_minutes_formatted = ten_minutes.strftime(f"{date_format} {time_format}")
    one_hour_formatted = one_hour.strftime(f"{date_format} {time_format}")
    one_day_formatted = one_day.strftime(f"{date_format} {time_format}")
    one_week_formatted = one_week.strftime(f"{date_format} {time_format}")
    bot.send_message(message.chat.id, f'Примеры:\n\n{ten_minutes_formatted} - через 10 минут\n{one_hour_formatted} - через час\n{one_day_formatted} - через день\n{one_week_formatted} - через неделю')
    bot.register_next_step_handler(message, set_publish_time2)
def set_publish_time2(message):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')
    variable_value = message.text
    current_time = datetime.datetime.now()
    try:
        variable_time = datetime.datetime.strptime(variable_value, "%Y-%m-%d %H:%M")
        if variable_time > current_time:
            with open(f'./LOTS/{folder_name}/description.txt', 'a', encoding='utf-8') as channels_file:
                channels_file.write(f'{message.text}   ,')    
            bot.send_message(message.chat.id, '✅ Время сохранено')
            end_lot_time(message)
        else:
            bot.send_message(message.chat.id, "❗️ Вы ввели время, которое уже прошло.\n\nВнимательно осмотрите пример и попробуйте ещё раз")
            set_publish_time(message)
    except Exception:
        bot.send_message(message.chat.id, "❗️ Вы ввели неправильный формат времени.\n\nВнимательно осмотрите пример и попробуйте ещё раз.")
        set_publish_time(message)


###Выбираем способ окончания розыгрыша
def end_lot_time(message):
    keyboard5 = types.InlineKeyboardMarkup()
    knopka5 = types.InlineKeyboardButton(text="По времени", callback_data='By_the_time')
    knopka6 = types.InlineKeyboardButton(text="По количеству участников", callback_data='By_pass_count')
    keyboard5.add(knopka5)
    keyboard5.add(knopka6)
    bot.send_message(message.chat.id, '⏰ Как завершить розыгрыш?', reply_markup=keyboard5)
def end_lot_time_by_the_time(message):
    bot.send_message(message.chat.id, '⏰ Когда нужно завершить розыгрыш? (Укажите время в формате дд.мм.гг чч:мм)\n\nБот живет по времени (GMT+3) Москва, Россия')
    now = datetime.datetime.now()
    ten_minutes = now + datetime.timedelta(minutes=10)
    one_hour = now + datetime.timedelta(hours=1)
    one_day = now + datetime.timedelta(days=1)
    one_week = now + datetime.timedelta(weeks=1)
    date_format = "%Y-%m-%d"
    time_format = "%H:%M"
    ten_minutes_formatted = ten_minutes.strftime(f"{date_format} {time_format}")
    one_hour_formatted = one_hour.strftime(f"{date_format} {time_format}")
    one_day_formatted = one_day.strftime(f"{date_format} {time_format}")
    one_week_formatted = one_week.strftime(f"{date_format} {time_format}")
    bot.send_message(message.chat.id, f'Примеры:\n\n{ten_minutes_formatted} - через 10 минут\n{one_hour_formatted} - через час\n{one_day_formatted} - через день\n{one_week_formatted} - через неделю')
    bot.register_next_step_handler(message, end_lot_time_by_the_time2)
def end_lot_time_by_the_time2(message):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')
    variable_value = message.text
    current_time = datetime.datetime.now()
    with open(f'./LOTS/{folder_name}/description.txt', 'r',  encoding='utf-8') as file:
        data = file.read()
    values = data.split('   ,')
    publication_date = values[3]
    if "RightNow" in publication_date:
        variable_time1 = datetime.datetime.now()
    else:
        variable_time1 = datetime.datetime.strptime(publication_date, "%Y-%m-%d %H:%M")
    try:
        variable_time2 = datetime.datetime.strptime(variable_value, "%Y-%m-%d %H:%M")
        if variable_time2 > current_time:
            if variable_time1 < variable_time2:
                with open(f'./LOTS/{folder_name}/description.txt', 'a', encoding='utf-8') as channels_file:
                    channels_file.write(f'{message.text}  time   ,')    
                bot.send_message(message.chat.id, '✅ Время сохранено')
                check_final_post(message)
            else:
                bot.send_message(message.chat.id, "❗️ Вы ввели время завершения розыгрыша, которое проведет розыгрыш раньше, чем он опубликуется.\n\nВнимательно осмотрите пример и попробуйте ещё раз")
                end_lot_time_by_the_time(message)    
        else:
            bot.send_message(message.chat.id, "❗️ Вы ввели время, которое уже прошло.\n\nВнимательно осмотрите пример и попробуйте ещё раз")
            end_lot_time_by_the_time(message)
    except Exception:
        bot.send_message(message.chat.id, "❗️ Вы ввели неправильный формат времени.\n\nВнимательно осмотрите пример и попробуйте ещё раз.")
        end_lot_time_by_the_time(message)
def end_lot_time_by_pass_count(message):
    bot.send_message(message.chat.id, '🧮 Сколько должно быть участников для завершения розыгрыша?\n\nВведите число:')
    bot.register_next_step_handler(message, end_lot_time_by_pass_count2)
def end_lot_time_by_pass_count2(message):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')
    os.environ['CHAT_ID'] = str(message.chat.id)
    with open(f'./LOTS/{folder_name}/description.txt', 'a', encoding='utf-8') as channels_file:
            channels_file.write(f'{message.text}  participants   ,')    
    bot.send_message(message.chat.id, '✅ Количество участников сохранено')
    check_final_post(message)        


###Проверяем пост
def check_final_post(message):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')
    with open(f'./LOTS/{folder_name}/description.txt', 'r',  encoding='utf-8') as file:
        data = file.read()
    values = data.split('   ,')
    with open(f'./LOTS/{folder_name}/message_data.pkl', 'rb') as file:
        text = pickle.load(file)
    button_text = values[0]
    winners_value = values[1]
    winners_value1 = winners_value.split(':')
    winners_value2 = winners_value1[0]
    publication_channel = values[2]
    publication_date = values[3]
    if 'RightNow' in publication_date:
        publication_date = str('Сразу после окончания настройки')
    way_of_ending = values[4]
    if 'participants' in way_of_ending:
        way_of_ending1 = way_of_ending.split("  ")
        way_of_ending2 = str(f'по регистрации {way_of_ending1[0]} участников')
    else:
        way_of_ending1 = way_of_ending.split("  ")
        way_of_ending2 = str(f'в указанное ({way_of_ending1[0]}) время')
    with open(f'./LOTS/{folder_name}/channels.txt', 'r') as channels:
        channels_for_subscribe = channels.read()
        if 'Without_Subscribe' in channels_for_subscribe:
            channels_for_subscribe2 = str('Без каналов, обязательных к подписке')
        else:
            channels_for_subscribe1 = channels_for_subscribe.split(',')
            if channels_for_subscribe1[-1] == '':  # Проверяем, что последний элемент пустой
                channels_for_subscribe1.pop()  # Удаляем последний элемент только если он пустой
            channels_for_subscribe2 = '\n'.join(channels_for_subscribe1)
    keyboard4 = types.InlineKeyboardMarkup()
    knopka4 = types.InlineKeyboardButton(text=f"{button_text}", callback_data='I`m_in')
    keyboard4.add(knopka4)
    file_extension = os.environ.get('FILE_EXTENSION')
    try:
        image_path = f'./LOTS/{folder_name}/file.{file_extension}'  # Укажите путь к изображению
        photo = open(image_path, 'rb')
        bot.send_photo(message.chat.id, photo, caption=text, reply_markup=keyboard4)
        photo.close()
    except Exception:
        bot.send_message(message.chat.id, f"{text}", reply_markup=keyboard4)
    keyboard5 = types.InlineKeyboardMarkup()
    knopka5 = types.InlineKeyboardButton(text="Сохранить розыгрыш", callback_data='Save_lot')
    knopka6 = types.InlineKeyboardButton(text="Отмена", callback_data='Cansel_sure')
    keyboard5.add(knopka5)
    keyboard5.add(knopka6)
    bot.send_message(message.chat.id, f'🧮 Внимательно перепроверьте розыгрыш\n\n🔚 Розыгрыш опубликуется:\n{publication_date}\n🔚 В канале:\n{publication_channel}\n\n🔚 Розыгрыш окончится {way_of_ending2}\n\n🏆 Количество победителей: {winners_value2}\n\n😎 Каналы, обязательные к подписке: {channels_for_subscribe2}', reply_markup=keyboard5)


#Уточнение удаления розыгрыша
def Cancel_lot_sure(message):
    keyboard = types.InlineKeyboardMarkup()
    knopka = types.InlineKeyboardButton(text="Вернуться к розыгрышу", callback_data='Back_to_lot')
    knopka2 = types.InlineKeyboardButton(text="Удалить розыгрыш", callback_data='Cansel')
    keyboard.add(knopka)
    keyboard.add(knopka2)
    bot.send_message(message.chat.id, 'Вы уверены что хотите удалить созданный розыгрыш?', reply_markup=keyboard)


#Удаление розыгрыша
def Cancel_lot(message):
    path = f"{current_directory}/{os.environ.get('CURRENT_FOLDER_NAME')}"
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(path)
    bot.send_message(message.chat.id, 'Розыгрыш успешно удален!\n\nВы можете создать новый, используя кнопки под клавиатурой.', reply_markup=markup)


#Сохранение розыгрыша
def Save_lottery(message):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')
    with open(f'./LOTS/{folder_name}/description.txt', 'r',  encoding='utf-8') as file:
        data = file.read()
    values = data.split('   ,')
    with open(f'./LOTS/{folder_name}/message_data.pkl', 'rb') as file:
        text = pickle.load(file)
    publication_date = values[3]
    way_of_ending = values[4]
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if 'participants' in way_of_ending:
        way_of_ending1 = way_of_ending.split("  ")
        HM_users = (int(way_of_ending1[0])+1)
        if "RightNow" in publication_date:
            now = datetime.datetime.now()
            publication_date = now + datetime.timedelta(minutes=1)
            current_time = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
            delay = (publication_date - current_time).total_seconds()
            thread = threading.Thread(target=Send_message_to_time, args=(delay, HM_users,))
            thread.start()
            status = f'будет  опубликован в течение минуты'  
        elif current_time < publication_date:
            current_time = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
            publication_date = publication_date + ':00'
            publication_date = datetime.datetime.strptime(publication_date, "%Y-%m-%d %H:%M:%S")
            delay = (publication_date - current_time).total_seconds()
            thread = threading.Thread(target=Send_message_to_time, args=(delay, HM_users,))
            thread.start()
            status = f'будет опубликован {publication_date}'
        else:
            status = 'Не опубликован. Обратитесь в поддержку!'
    else:
        HM_users = "9999999"
        if "RightNow" in publication_date:
            now = datetime.datetime.now()
            publication_date = now + datetime.timedelta(minutes=1)
            current_time = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
            delay = (publication_date - current_time).total_seconds()
            thread = threading.Thread(target=Send_message_to_time, args=(delay, HM_users,))
            thread.start()
            status = f'будет  опубликован в течение минуты'  
        elif current_time < publication_date:
            current_time = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
            publication_date = publication_date + ':00'
            publication_date = datetime.datetime.strptime(publication_date, "%Y-%m-%d %H:%M:%S")
            delay = (publication_date - current_time).total_seconds()
            thread = threading.Thread(target=Send_message_to_time, args=(delay, HM_users,))
            thread.start()
            status = f'будет опубликован {publication_date}'
        else:
            status = 'Не опубликован. Обратитесь в поддержку!'
        current_time = datetime.datetime.now()
        way_of_ending1 = way_of_ending.split("  time")
        way_of_ending1 = way_of_ending1[0] + ':00'
        way_of_ending = datetime.datetime.strptime(way_of_ending1, "%Y-%m-%d %H:%M:%S")
        delay = (way_of_ending - current_time).total_seconds()
        thread1 = threading.Thread(target=finish_lot_by_the_time_alarm, args=(delay, message, text,))
        thread1.start()    
    bot.send_message(message.chat.id, f'✅ Розыгрыш сохранен и {status}.\n\nДля вызова меню напишите /start')


###Сообщение о том что пора завершать конкурс по времени
def finish_lot_by_the_time_alarm(delay, message, text):
    if delay > 18000:
        time.sleep(delay - 18000)
        bot.send_message(message.chat.id, f'Через 6 часов настанет время оканчивать розыгрыш "{text[:30]}"\nПерейдите в раздел "Мои розыгрыши", выберите розыгрыш и нажмите "Окончить".', reply_markup=markup)
    else:    
        time.sleep(delay)
        bot.send_message(message.chat.id, f'Настало время оканчивать розыгрыш "{text[:30]}"\nПерейдите в раздел "Мои розыгрыши", выберите розыгрыш и нажмите "Окончить".', reply_markup=markup)


###Выложить пост
def Send_message_to_time(delay, HM_users):
    time.sleep(delay)
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')
    with open(f'./LOTS/{folder_name}/description.txt', 'r',  encoding='utf-8') as file:
        data = file.read()
    values = data.split('   ,')
    with open(f'./LOTS/{folder_name}/message_data.pkl', 'rb') as file:
        text = pickle.load(file)
    button_text = values[0]        
    keyboard = types.InlineKeyboardMarkup()
    callback_dataa = f"Registration_on_lot:{HM_users}"
    knopka = types.InlineKeyboardButton(text=f"{button_text}", callback_data=callback_dataa)
    keyboard.add(knopka)
    file_extension = os.environ.get('FILE_EXTENSION')
    publication_channels = values[2]
    channels = publication_channels.split(", ")
    if len(channels) == 1:
        channel = channels[0]
        try:
            image_path = f'./LOTS/{folder_name}/file.{file_extension}'  # Укажите путь к изображению
            photo = open(image_path, 'rb')
            sent_message = bot.send_photo(channel, photo, caption=text, reply_markup=keyboard)
            photo.close()
            message_link = f"https://t.me/{sent_message.chat.username}/{sent_message.message_id}"
            with open(f'./LOTS/{folder_name}/link.txt', 'a', encoding='utf-8') as link_file:
                link_file.write(message_link)    
        except Exception:
            sent_message = bot.send_message(channel, f"{text}", reply_markup=keyboard)
            message_link = f"https://t.me/{sent_message.chat.username}/{sent_message.message_id}"
            with open(f'./LOTS/{folder_name}/link.txt', 'a', encoding='utf-8') as link_file:
                link_file.write(message_link)    
    
    else:
        for channel in channels:
            try:
                image_path = f'./LOTS/{folder_name}/file.{file_extension}'  # Укажите путь к изображению
                photo = open(image_path, 'rb')
                sent_message = bot.send_photo(channel, photo, caption=text, reply_markup=keyboard)
                photo.close()
                message_link = f"https://t.me/{sent_message.chat.username}/{sent_message.message_id}"
                with open(f'./LOTS/{folder_name}/link.txt', 'a', encoding='utf-8') as link_file:
                    link_file.write(message_link)        
            except Exception:
                sent_message = bot.send_message(channel, f"{text}", reply_markup=keyboard)
                message_link = f"https://t.me/{sent_message.chat.username}/{sent_message.message_id}"
                with open(f'./LOTS/{folder_name}/link.txt', 'a', encoding='utf-8') as link_file:
                    link_file.write(message_link)    
        

###Проверяем подписан ли участник на указанные каналы
def check_subscription(user, channel):
    user_id = user.id
    result = bot.get_chat_member(channel, user_id)
    if result.status == "left" or result.status == "kicked":
        return False
    return True



###Отклики кнопок под сообщениями
@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')
    if callback.data == 'btn_ver1':
        with open(f'./LOTS/{folder_name}/description.txt', 'w', encoding='utf-8') as description_file:
            description_file.write("Участвую!   ,")
        bot.send_message(callback.message.chat.id, '✅ Текст кнопки сохранен')
        chose_channels_subscribe(callback.message)
    elif callback.data == 'btn_ver2':
        with open(f'./LOTS/{folder_name}/description.txt', 'w', encoding='utf-8') as description_file:
            description_file.write("Участвовать   ,")
        bot.send_message(callback.message.chat.id, '✅ Текст кнопки сохранен')
        chose_channels_subscribe(callback.message)    
    elif callback.data == 'btn_ver3':
        with open(f'./LOTS/{folder_name}/description.txt', 'w', encoding='utf-8') as description_file:
            description_file.write("Принять участие   ,")
        bot.send_message(callback.message.chat.id, '✅ Текст кнопки сохранен')
        chose_channels_subscribe(callback.message)
    elif callback.data == 'btn_ver4':
        bot.send_message(callback.message.chat.id, 'Введите текст для кнопки:\n\nКнопки не поддерживают смайлы и эмодзи!')
        bot.register_next_step_handler(callback.message, add_button_text)
    elif callback.data == 'Add_channels':    
        bot.send_message(callback.message.chat.id, '\n\nЧтобы добавить канал, нужно:\n1. Добавить бота (@{bot_info.username}) в ваш канал как администратора (Это нужно, чтобы бот мог проверить подписан ли пользователь на канал)\n2. Отправить боту канал в формате @channelname.')
        bot.register_next_step_handler(callback.message, add_more_subscribe_channels)
    elif callback.data == 'Add_more_subscribe_channels':
        bot.send_message(callback.message.chat.id, '\n\nЧтобы добавить канал, нужно:\n1. Добавить бота (@{bot_info.username}) в ваш канал как администратора (это нужно, чтобы бот мог проверить подписан ли пользователь на канал)\n2. Отправить боту канал в формате @channelname.')
        bot.register_next_step_handler(callback.message, add_more_subscribe_channels)
    elif callback.data == 'Without_Subscribe':
        with open(f'./LOTS/{folder_name}/channels.txt', 'w', encoding='utf-8') as channels_file:
            channels_file.write('Without_Subscribe')    
        bot.send_message(callback.message.chat.id, '✅ Ваш выбор сохранен')
        how_much_winners(callback.message)        
    elif callback.data == 'Next_step':    
        bot.send_message(callback.message.chat.id, '✅ Ваш выбор сохранен')
        how_much_winners(callback.message)                
    elif callback.data == 'Channel_for_publish_from_list':
        bot.send_message(callback.message.chat.id, 'Отправьте мне название канала как в списке. Если хотите опубликовать в нескольких - отправьте через запятую. Пример:\n\n@channel1, @channel2')
        bot.register_next_step_handler(callback.message, Channel_for_publish_from_list)
    elif callback.data == 'Channel_for_subscribe_from_list':
        bot.send_message(callback.message.chat.id, 'Отправьте мне название канала как в списке. Если хотите опубликовать в нескольких - отправьте через запятую. Пример:\n\n@channel1, @channel2')
        bot.register_next_step_handler(callback.message, chose_from_list)
    elif callback.data == 'Add_channel_to_list1':
        bot.send_message(callback.message.chat.id, 'Чтобы добавить канал в список:\n1. Cделайте этого бота администратором канала\n2. Напишите имя нового канала в формате:\n\n@channelname')
        bot.register_next_step_handler(callback.message, Add_channel_to_list)
    elif callback.data == 'Time_right_now':
        with open(f'./LOTS/{folder_name}/description.txt', 'a', encoding='utf-8') as channels_file:
            channels_file.write('RightNow   ,')    
        bot.send_message(callback.message.chat.id, '✅ Время сохранено')
        end_lot_time(callback.message)        
    elif callback.data == 'Time_input':
        set_publish_time(callback.message)        
    elif callback.data == 'Add_channel_to_list':    
        bot.send_message(callback.message.chat.id, 'Чтобы добавить канал в список:\n1. Cделайте этого бота администратором канала\n2. Напишите имя нового канала в формате:\n\n@channelname')
        bot.register_next_step_handler(callback.message, add_new_channel)        
    elif callback.data == 'By_the_time':
        end_lot_time_by_the_time(callback.message)        
    elif callback.data == 'By_pass_count':    
        end_lot_time_by_pass_count(callback.message)        
    elif callback.data == 'Cansel_sure':    
        Cancel_lot_sure(callback.message)        
    elif callback.data == 'Cansel':    
        Cancel_lot(callback.message)        
    elif callback.data == 'Save_lot':    
        Save_lottery(callback.message)
    elif callback.data == 'Back_to_lot':    
        check_final_post(callback.message)    
    elif callback.data == 'Open_Lot':    
        bot.send_message(callback.message.chat.id, "Какой розыгрыш открыть?\nНапишите название из списка, например:\n\nMyLot1")
        bot.register_next_step_handler(callback.message, Open_lot)   
    elif callback.data == 'Back_to_My_Lots':    
        My_lots(callback.message)    
    elif callback.data == 'Back_to_list':    
        publish_channel(callback.message)    
    elif callback.data == 'Back_to_list1':    
        chose_channels_subscribe(callback.message)
    elif callback.data.startswith("Registration_on_lot:"):
        data_parts = callback.data.split(":")  
        HM_users = int(data_parts[1])
        owner = os.environ.get('CHAT_ID')
        owner = int(owner)
        user = callback.from_user
        folder_name = os.environ.get('CURRENT_FOLDER_NAME')
        with open(f'./LOTS/{folder_name}/members.txt', 'r') as text_file:
            spisok = text_file.read().split(',')
            users_count = len(spisok)    
            if users_count == HM_users or users_count > HM_users:
                bot.send_message(chat_id=owner, text='Набрано нужное количество участников!\nЧтобы завершить розыгрыш перейдите в раздел "Мои розыгрыши", выберите нужный розыгрыш и нажмите кнопку "Завершить"')
        text_file.close()
        uchastnik = str("@" + user.username)
        with open(f'./LOTS/{folder_name}/channels.txt', 'r') as channels:
            channels_for_subscribe = channels.read()
            if 'Without_Subscribe' in channels_for_subscribe:
                if uchastnik in spisok:
                    message = "Вы уже участвуете в розыгрыше 🥳\nРезультаты будут опубликованы в группе @CSKA_mil"
                else:
                    with open(f'./LOTS/{folder_name}/members.txt', 'a', encoding='utf-8') as text_file:
                        text_file.write(uchastnik + ",")
                    text_file.close()
                    message = "Вы добавлены в список участников розыгрыша 🥳\nРезультаты будут опубликованы в группе @CSKA_mil"
            else:
                not_subscribed_channels = []
                channels_for_subscribe1 = re.findall(r'@[\w]+', channels_for_subscribe)
                for channel in channels_for_subscribe1:
                    user_id = user.id
                    subscribed = bot.get_chat_member(channel, user_id).status
                    if subscribed not in ['member', 'creator', 'administrator']:
                        not_subscribed_channels.append(channel)
                if not_subscribed_channels:
                    message = f"Вы не подписаны на канал: {', '.join(not_subscribed_channels)}\nПожалуйста, подпишитесь, чтобы участвовать в розыгрыше!"
                else:
                    for_save = str(uchastnik)
                    if for_save in spisok:
                        message = "Вы уже участвуете в розыгрыше 🥳\nРезультаты будут опубликованы в группе @CSKA_mil"    
                    else: 
                        with open(f'./LOTS/{folder_name}/members.txt', 'a', encoding='utf-8') as text_file:
                            text_file.write(for_save + ",")
                        text_file.close()
                        message = "Вы добавлены в список участников розыгрыша 🥳\nРезультаты будут опубликованы в группе @CSKA_mil"
        bot.answer_callback_query(callback_query_id=callback.id, text=message, show_alert=True)
    elif callback.data == 'Delete_Lot':
        bot.send_message(callback.message.chat.id, "Напишите название розыгрыша, который вы хотите удалить.\nНапример:\n\nMyLot1")
        bot.register_next_step_handler(callback.message, Delete_Lot)
    elif callback.data == 'Finish_Lot':
        finish_lot_now(callback.message)
    elif callback.data == 'Publish_results_by_bot':
        bot.send_message(callback.message.chat.id, 'Пожалуйста отправьте мне картнику с описанием или просто текст для окончания розыгрыша. Я опубликую их после вашего подтверждения.')
        bot.register_next_step_handler(callback.message, Publish_results_by_bot)
    elif callback.data == 'Publish_results_by_user':
        bot.send_message(callback.message.chat.id, 'Отлично!\nВстретимся на следующем розыгрыше😋')
    elif callback.data == 'Finish_Channel_for_publish_from_list':
        bot.send_message(callback.message.chat.id, 'Отправьте мне название канала как в списке. Если хотите опубликовать в нескольких - отправьте через запятую. Пример:\n\n@channel1, @channel2')
        bot.register_next_step_handler(callback.message, Finish_Channel_for_publish_from_list)
    elif callback.data == 'Finish_Add_channel_to_list':
        bot.send_message(callback.message.chat.id, 'Чтобы добавить канал в список:\n1. Cделайте этого бота администратором канала\n2. Напишите имя нового канала в формате:\n\n@channelname')
        bot.register_next_step_handler(callback.message, Finish_Add_channel_to_list)
    elif callback.data == 'Finish_Back_to_list':
        Finish_back_to_list(callback.message)
    elif callback.data == 'Finish_time_right_now':
        with open(f'./LOTS/{folder_name}/Finish_description.txt', 'a', encoding='utf-8') as channels_file:
            channels_file.write('RightNow   ,')    
        bot.send_message(callback.message.chat.id, '✅ Время сохранено')
        Finish_check_final_post(callback.message)        
    elif callback.data == 'Finish_time_input':
        Finish_set_publish_time(callback.message)
    elif callback.data == 'Finish_save_post':    
        Finish_save_post(callback.message)
    elif callback.data == 'Finish_cansel_sure':    
        Finish_cancel_sure(callback.message)        
    elif callback.data == 'Finish_cansel':    
        Finish_cancel(callback.message)        
    elif callback.data == 'Finish_back_to_post':    
        Finish_check_final_post(callback.message)        






###Отклик на кнопки под клавиатурой
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "Создать розыгрыш":
        # Переменная для хранения самого большого числа после "MyLot"
        max_number = 0
        # Проверяем наличие папок и находим самое большое число
        for item in os.listdir(current_directory):
            if os.path.isdir(os.path.join(current_directory, item)) and item.startswith("MyLot"):
                try:
                    number = int(item.replace("MyLot", ""))
                    if number > max_number:
                        max_number = number
                except ValueError:
                    pass
        # Создаем новую папку "MyLot" с увеличенным номером
        new_folder_name = f"MyLot{max_number + 1}"
        os.makedirs(os.path.join(current_directory, new_folder_name), exist_ok=True)
        os.environ['CURRENT_FOLDER_NAME'] = new_folder_name
        file_path = f"./LOTS/{new_folder_name}/members.txt"
        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                pass
        file_path = f"./LOTS/{new_folder_name}/link.txt"
        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                pass    
        bot.send_message(message.chat.id, f'Создание розыгрыша\n✉️ Отправьте текст для розыгрыша. Вы можете также отправить вместе с текстом картинку, видео или GIF, пользоваться разметкой.\n\n❗️ Вы можете использовать только 1 медиафайл')
        bot.register_next_step_handler(message, files_for_lot)
    elif message.text == "Мои розыгрыши":
        My_lots(message)
    elif message.text == "Мои каналы":    
        My_channels_list(message)
    elif message.text == "Техническая поддержка":
        bot.send_message(message.chat.id, f'ℹ️ Если возникли трудности, прочитайте инструкцию по работе с ботом. Инструкция - *ссылка*\n\n⚙️ Если полностью прочитали инструкцию и остались вопросы, пишите @air_hood_rich (ответ не моментальный, а по возможности)')


# Запускаем бота
bot.polling()
