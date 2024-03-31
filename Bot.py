from enum import member
import telebot
from random import choice
from telebot import types
import os
import datetime
import urllib.request

os.environ['CHANNEL_USERNAME'] = '@cska_mo_rf'
os.environ['FILE_EXTENSION'] = 'jpg'
os.environ['CURRENT_FOLDER_NAME'] = 'MyLot1'
###Подключаем бота
TOKEN = '7100567356:AAE3k61dzZEi99QHSMStfxC0SU3HRPyPa_k'
bot = telebot.TeleBot(TOKEN)
###Создаем кнопки под клавиатурой
markup = types.ReplyKeyboardMarkup()
btn1 = types.KeyboardButton("Создать розыгрыш")
btn2 = types.KeyboardButton("Мои розыгрыши")
markup.row(btn1, btn2)
btn3 = types.KeyboardButton("Мой канал")
btn4 = types.KeyboardButton("Техническая поддержка")
markup.row(btn3, btn4)
###Получаем путь к актуальной директории
current_directory = os.path.dirname(os.path.realpath(__file__))

###Обработчик команды "Старт" 
@bot.message_handler(commands=['start'])
def start(message): 
    bot.send_message(message.chat.id, f"👋 Здравствуйте!\nДанный бот поможет Вам провести розыгрыш на канале, в чате или группе.\nГотовы создать новый розыгрыш?", reply_markup=markup)


###Смена канала для розыгрыша
@bot.message_handler(commands=['change_channel'])
def edit_channel(message):
    My_channel = os.environ.get('CHANNEL_USERNAME')
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Сменить канал на другой", callback_data='Change_channel')
    keyboard.add(btn1)
    bot.send_message(message.chat.id, f'Канал для розыгрыша: {My_channel}', reply_markup=keyboard)
def process_new_channel(message):
    chat_id = message.text
    bot_info = bot.get_me()
    bot_user_id = bot_info.id
    if '@' in chat_id:
        try: 
            chat_member = bot.get_chat_member(chat_id, bot_user_id)
            if chat_member.status == 'administrator':
                os.environ['CHANNEL_USERNAME'] = message.text 
                bot.send_message(message.chat.id, f"Канал успешно изменен на: {os.environ.get('CHANNEL_USERNAME')}.\nПора устраивать розыгрыш!", reply_markup=markup)
            else:
                bot.reply_to(message, 'Бот не является администратором канала.\nПожалуйста, назначьте его администратором и отправьте его имя ещё раз.')
                bot.register_next_step_handler(message, process_new_channel)
        except Exception:
            bot.reply_to(message, 'Бот не является администратором канала.\nПожалуйста, назначьте его администратором и отправьте его имя ещё раз.')
            bot.register_next_step_handler(message, process_new_channel)
    else:
        bot.send_message(message.chat.id, 'Неправльный формат!\nНужный формат: @channelname\n\nПожалуйста введите в нужном формате:')               
        bot.register_next_step_handler(message, process_new_channel)


###Прием файлов для розыгрыша и выбор кнопки для розыгрыша
def files_for_lot(message):
    try:
        folder_name = os.environ.get('CURRENT_FOLDER_NAME')
        file_id = message.photo[-1].file_id if message.photo else message.video.file_id if message.video else message.document.file_id
        file_info = bot.get_file(file_id)        
        file_path = file_info.file_path
        url = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
        file_extension = file_info.file_path.split('.')[-1]
        os.environ['FILE_EXTENSION'] = file_extension
        urllib.request.urlretrieve(url, f'./{folder_name}/file.{file_extension}')    
        description = str(message.caption) if message.caption else 'No_Caption'
        with open(f'./{folder_name}/description.txt', 'w') as description_file:
            description_file.write(description + '   ,')
        bot.send_message(message.chat.id, "✅ Медиафайл и описание сохранены!")
    except Exception:
        description = str(message.text)
        with open(f'./{folder_name}/description.txt', 'w') as description_file:
            description_file.write(description + '   ,')
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
    with open(f'./{folder_name}/description.txt', 'a') as description_file:
        description_file.write(f'{message.text}   ,')
    bot.send_message(message.chat.id, '✅ Текст кнопки сохранен')
    chose_channels_subscribe(message)


###Определяем каналы, на которые необходимо подписаться для участия в розыгрыше
def chose_channels_subscribe(message):
    keyboard2 = types.InlineKeyboardMarkup()
    knopka = types.InlineKeyboardButton(text="Оставить только мой канал", callback_data='Only_My_Channel')
    knopka2 = types.InlineKeyboardButton(text="Конкурс без подписок", callback_data='Without_Subscribe')
    knopka3 = types.InlineKeyboardButton(text="Добавить каналы", callback_data='Add_channels')
    keyboard2.add(knopka3)
    keyboard2.add(knopka)
    keyboard2.add(knopka2)
    bot.send_message(message.chat.id, f'📊 Выберите каналы, на которые пользователям нужно будет подписаться для участия в розыгрыше:\n\n⚠️ Если вы хотите чтобы участвовать в розыгрыше можно было с подпиской на Ваш канал ({os.environ["CHANNEL_USERNAME"]}) или без подписок на канал, нажмите одну из кнопок ниже:', reply_markup=keyboard2)


###Добавляеем ещё каналов для обязательной подписки
def add_more_subscribe_channels(message):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')
    chat_id = message.text
    bot_info = bot.get_me()
    bot_user_id = bot_info.id
    keyboard3 = types.InlineKeyboardMarkup()
    knopka3 = types.InlineKeyboardButton(text="Добавить ещё один канал", callback_data='Add_more_subscribe_channels')
    knopka4 = types.InlineKeyboardButton(text="Двигаемся дальше!", callback_data='Next_step')
    keyboard3.add(knopka3)
    keyboard3.add(knopka4)
    if '@' in chat_id:
        try: 
            chat_member = bot.get_chat_member(chat_id, bot_user_id)
            if chat_member.status == 'administrator': 
                with open(f'./{folder_name}/channels.txt', 'a') as channels_file:
                    channels_file.write(chat_id+",")
                bot.send_message(message.chat.id, f"✅ Канал успешно добавлен обязательным для участия в розыгрыше!\n\nЧтобы добавить ещё один канал оправьте его имя в формате @channel_name\nЧтобы окончить добавление каналов нажмите на кнопку ниже:\n\nНе забирайте у бота права администратора канала, иначе проверка подписки происходить не будет!", reply_markup=keyboard3)
            else:
                bot.reply_to(message, 'Бот не является администратором канала.\nПожалуйста, назначьте его администратором и отправьте его ещё раз:')
                bot.register_next_step_handler(message, add_more_subscribe_channels)
        except Exception:
            bot.reply_to(message, 'Бот не является администратором канала.\nПожалуйста, назначьте его администратором и отправьте его ещё раз:')
            bot.register_next_step_handler(message, add_more_subscribe_channels)
    else:
        bot.send_message(message.chat.id, 'Неправльный формат!\nНужный формат: @channelname\n\nПожалуйста введите в нужном формате:')               
        bot.register_next_step_handler(message, add_more_subscribe_channels)


###Определяем сколько победителей нужно выбрать боту
def how_much_winners(message):
    bot.send_message(message.chat.id, '🧮 Сколько победителей выбрать боту?\n\nВведите число:')
    bot.register_next_step_handler(message, how_much_winners2)
def how_much_winners2(message):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')
    with open(f'./{folder_name}/description.txt', 'a') as channels_file:
            channels_file.write(f'{message.text}:winner   ,')    
    bot.send_message(message.chat.id, '✅ Количество победителей сохранено')
    publish_channel(message)        


###Выбираем канал для публикации розыгрыша
def publish_channel(message):
    keyboard4 = types.InlineKeyboardMarkup()
    knopka4 = types.InlineKeyboardButton(text=f"{os.environ['CHANNEL_USERNAME']}", callback_data='Channel_for_publish')
    keyboard4.add(knopka4)
    bot.send_message(message.chat.id, '🗓 В каком канале публикуем розыгрыш?', reply_markup=keyboard4)


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
            with open(f'./{folder_name}/description.txt', 'a') as channels_file:
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
    with open(f'./{folder_name}/description.txt', 'r') as file:
        data = file.read()
    values = data.split('   ,')
    publication_date = values[4]
    if "RightNow" in publication_date:
        variable_time1 = datetime.datetime.now()
    else:
        variable_time1 = datetime.datetime.strptime(publication_date, "%Y-%m-%d %H:%M")
    try:
        variable_time2 = datetime.datetime.strptime(variable_value, "%Y-%m-%d %H:%M")
        if variable_time2 > current_time:
            if variable_time1 < variable_time2:
                with open(f'./{folder_name}/description.txt', 'a') as channels_file:
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
    with open(f'./{folder_name}/description.txt', 'a') as channels_file:
            channels_file.write(f'{message.text}  participants   ,')    
    bot.send_message(message.chat.id, '✅ Количество победителей сохранено')
    check_final_post(message)        



###Проверяем пост
def check_final_post(message):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')
    file_extension = os.environ.get('FILE_EXTENSION')
    image_path = f'./{folder_name}/file.{file_extension}'  # Укажите путь к изображению
    with open(f'./{folder_name}/description.txt', 'r') as file:
        data = file.read()
    values = data.split('   ,')
    text = values[0] 
    button_text = values[1]
    winners_value = values[2]
    winners_value1 = winners_value.split(':')
    winners_value2 = winners_value1[0]
    publication_channel = values[3]
    publication_date = values[4]
    if 'RightNow' in publication_date:
        publication_date = str('Сразу после окончания настройки')
    way_of_ending = values[5]
    if 'participants' in way_of_ending:
        way_of_ending1 = way_of_ending.split("  ")
        way_of_ending2 = str(f'по регистрации {way_of_ending1[0]} участников')
    else:
        way_of_ending1 = way_of_ending.split("  ")
        way_of_ending2 = str(f'в указанное ({way_of_ending1[0]}) время')
    with open(f'./{folder_name}/channels.txt', 'r') as channels:
        channels_for_subscribe = channels.read()
        if 'Without_Subscribe' in channels_for_subscribe:
            channels_for_subscribe2 = str('Без каналов, обязательных к подписке')
        else:
            channels_for_subscribe1 = channels_for_subscribe.split(',')
            channels_for_subscribe1.pop()
            channels_for_subscribe2 = '\n'.join(channels_for_subscribe1)
    photo = open(image_path, 'rb')
    keyboard4 = types.InlineKeyboardMarkup()
    knopka4 = types.InlineKeyboardButton(text=f"{button_text}", callback_data='I`m_in')
    keyboard4.add(knopka4)
    bot.send_photo(message.chat.id, photo, caption=text, reply_markup=keyboard4)
    keyboard5 = types.InlineKeyboardMarkup()
    knopka5 = types.InlineKeyboardButton(text="Сохранить розыгрыш", callback_data='Save_lot')
    knopka6 = types.InlineKeyboardButton(text="Отмена", callback_data='Cansel_sure')
    keyboard5.add(knopka5)
    keyboard5.add(knopka6)
    bot.send_message(message.chat.id, f'🧮 Внимательно перепроверьте розыгрыш\n\n🔚 Розыгрыш опубликуется:\n{publication_date}\n🔚 В канале:\n{publication_channel}\n\n🔚 Розыгрыш окончится {way_of_ending2}\n\n🏆 Количество победителей: {winners_value2}\n\n😎 Каналы, обязательные к подписке: {channels_for_subscribe2}', reply_markup=keyboard5)
    photo.close()


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
    bot.send_message(message.chat.id, 'Розыгрыш успешно удален!\n\nВы можете создать новый, используя кнопки под клавиатурой.', reply_markup=markup)

#Сохранение розыгрыша
def Save_lottery(message):
    bot.send_message(message.chat.id, '✅ Розыгрыш сохранен и готовится к публикации.\n\nДля вызова меню напишите /start')






###Отклики кнопок под сообщениями
@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    folder_name = os.environ.get('CURRENT_FOLDER_NAME')
    if callback.data == 'btn_ver1':
        with open(f'./{folder_name}/description.txt', 'a') as description_file:
            description_file.write("Участвую!   ,")
        bot.send_message(callback.message.chat.id, '✅ Текст кнопки сохранен')
        chose_channels_subscribe(callback.message)
    elif callback.data == 'btn_ver2':
        with open(f'./{folder_name}/description.txt', 'a') as description_file:
            description_file.write("Участвовать   ,")
        bot.send_message(callback.message.chat.id, '✅ Текст кнопки сохранен')
        chose_channels_subscribe(callback.message)    
    elif callback.data == 'btn_ver3':
        with open(f'./{folder_name}/description.txt', 'a') as description_file:
            description_file.write("Принять участие   ,")
        bot.send_message(callback.message.chat.id, '✅ Текст кнопки сохранен')
        chose_channels_subscribe(callback.message)
    elif callback.data == 'btn_ver4':
        bot.send_message(callback.message.chat.id, 'Введите текст для кнопки:')
        bot.register_next_step_handler(callback.message, add_button_text)
    elif callback.data == 'Add_channels':
        with open(f'./{folder_name}/channels.txt', 'w') as channels_file:
            channels_file.write(os.environ['CHANNEL_USERNAME']+',')    
        bot.send_message(callback.message.chat.id, '\n\nЧтобы добавить канал, нужно:\n1. Добавить бота (@{bot_info.username}) в ваш канал как администратора (это нужно, чтобы бот мог проверить подписан ли пользователь на канал)\n2. Отправить боту канал в формате @channelname.')
        bot.register_next_step_handler(callback.message, add_more_subscribe_channels)
    elif callback.data == 'Add_more_subscribe_channels':
        bot.send_message(callback.message.chat.id, '\n\nЧтобы добавить канал, нужно:\n1. Добавить бота (@{bot_info.username}) в ваш канал как администратора (это нужно, чтобы бот мог проверить подписан ли пользователь на канал)\n2. Отправить боту канал в формате @channelname.')
        bot.register_next_step_handler(callback.message, add_more_subscribe_channels)
    elif callback.data == 'Only_My_Channel':
        with open(f'./{folder_name}/channels.txt', 'w') as channels_file:
            channels_file.write(os.environ['CHANNEL_USERNAME'])    
        bot.send_message(callback.message.chat.id, '✅ Ваш выбор сохранен')
        how_much_winners(callback.message)
    elif callback.data == 'Without_Subscribe':
        with open(f'./{folder_name}/channels.txt', 'w') as channels_file:
            channels_file.write('Without_Subscribe')    
        bot.send_message(callback.message.chat.id, '✅ Ваш выбор сохранен')
        how_much_winners(callback.message)        
    elif callback.data == 'Next_step':    
        bot.send_message(callback.message.chat.id, '✅ Ваш выбор сохранен')
        how_much_winners(callback.message)                
    elif callback.data == 'Channel_for_publish':
        with open(f'./{folder_name}/description.txt', 'a') as channels_file:
            channels_file.write(f'{os.environ["CHANNEL_USERNAME"]}   ,')    
        bot.send_message(callback.message.chat.id, '✅ Ваш выбор сохранен')
        publish_time(callback.message)        
    elif callback.data == 'Time_right_now':
        with open(f'./{folder_name}/description.txt', 'a') as channels_file:
            channels_file.write('RightNow   ,')    
        bot.send_message(callback.message.chat.id, '✅ Время сохранено')
        end_lot_time(callback.message)        
    elif callback.data == 'Time_input':
        set_publish_time(callback.message)        
    elif callback.data == 'Change_channel':    
        bot.send_message(callback.message.chat.id, 'Если вы хотите установить другой канал для розыгрыша - сделайте этого бота админом канала и напишите имя нового канала в формате:\n\n@channelname')
        bot.register_next_step_handler(callback.message, process_new_channel)        
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
        bot.send_message(message.chat.id, f'Создание розыгрыша\n✉️ Отправьте текст для розыгрыша. Вы можете также отправить вместе с текстом картинку, видео или GIF, пользоваться разметкой.\n\n❗️ Вы можете использовать только 1 медиафайл')
        bot.register_next_step_handler(message, files_for_lot)
    elif message.text == "Мои розыгрыши":
        bot.send_message(message.chat.id, f'Мои роыгрыши')
    elif message.text == "Мой канал":    
        edit_channel(message)
    elif message.text == "Техническая поддержка":
        bot.send_message(message.chat.id, f'Поддержка')







"""
@bot.message_handler(commands=['join'])
def lottery(message):
    user = message.from_user
    text_file = open("member.txt", 'r')
    spisok = text_file.read()
    text_file.close()
    if check_subscription(user):
        if user.username in spisok:
            bot.send_message(message.chat.id, f"Вы уже участвуете в розыгрыше 🥳\nРезультаты будут опубликованы в группе @CSKA_mil\nЕсли это не первый розыгрыш от нашего сообщества в котором вы участвуете или вы хотите проверить успешна ли прошла регистрация - напишите /join ещё раз)")    
        else: 
            uchastnik = str(user.username)
            text_file = open("member.txt", 'a')
            if not uchastnik in spisok:
                text_file.write(uchastnik + ",")
            text_file.close()
            bot.send_message(message.chat.id, f"Вы добавлены в список участников розыгрыша 🥳\nРезультаты будут опубликованы в группе @CSKA_mil\nЕсли это не первый розыгрыш от нашего сообщества в котором вы участвуете или вы хотите проверить успешна ли прошла регистрация - напишите /join ещё раз)")
    else:
        bot.send_message(message.chat.id, f"Вы не подписаны на канал {CHANNEL_USERNAME} 😔.\nПожалуйста, подпишитесь, чтобы участвовать в розыгрыше и напишите /join еще раз.")

def check_subscription(user):
    user_id = user.id
    result = bot.get_chat_member(CHANNEL_USERNAME, user_id)
    if result.status == "left" or result.status == "kicked":
        return False
    return True
"""

# Запускаем бота
bot.polling()
