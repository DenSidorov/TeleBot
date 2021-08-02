import telebot
from extensions import APIException, Convertor, UserDB
from config import TOKEN, exchanges
import traceback

bot = telebot.TeleBot(TOKEN)

db = UserDB()


@bot.message_handler(commands=['start', 'help'])
def start(message: telebot.types.Message):
    text = r'''Чтобы выбрать валюты для конвертации введите команду: /set,
            По-умолчанию конвертация из USD в RUB.
            Отправьте сумму, чтобы произвести конвертацию:'''

    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['set'])
def set(message: telebot.types.Message):
    markup = telebot.types.InlineKeyboardMarkup()
    for vol, form in exchanges.items():
        buttom = telebot.types.InlineKeyboardButton(
            text=vol.capitalize(), callback_data=f'val1 {form}')
        markup.add(buttom)
    bot.send_message(chat_id=message.chat.id,
                     text='Выберите валюту из которой будем конвертировать', reply_markup=markup)

    markup = telebot.types.InlineKeyboardMarkup()
    for vol, form in exchanges.items():
        buttom = telebot.types.InlineKeyboardButton(
            text=vol.capitalize(), callback_data=f'val2 {form}')
        markup.add(buttom)
    bot.send_message(chat_id=message.chat.id,
                     text='Выберите валюту в которую будем конвертировать', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    t, st = call.data.split()
    user_id = call.message.chat.id
    if t == 'val1':
        db.change_from(user_id, st)
    if t == 'val2':
        db.change_to(user_id, st)
    pair = db.get_pair(user_id)
    bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                              text=f'Конвернтация из {pair[0]} в {pair[1]}')


@bot.message_handler(content_types=['text'])
def converter(message: telebot.types.Message):
    pair = db.get_pair(message.chat.id)
    values = [*pair, message.text.strip()]
    try:
        answer = Convertor.get_price(*values)
    except APIException as e:
        bot.reply_to(message, f"Ошибка в команде: /help\n{e}")
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        bot.reply_to(message, f"Неизвестная ошибка: /help\n{e}")
    else:
        text = f'Цена {values[2]} {values[0]} = {answer} {pair[1]}'
        bot.reply_to(message, text)


bot.polling()
