import os
from threading import Lock, Thread
from config.settings import BOT_TOKEN

import telebot
from user.models import User


def run_telebot(lock: Lock):
    """
    Метод запускает экземпляр бота Телеграм
    Бот постоянно находится в режиме ожидания активации бота пользователем
    путем ввода предопределенных команд ("/start", "/help")
    В этом случае бот находит данного пользователя в базе данных
    по его username в Телеграм и записывает в поле id_telegram актуальный
    id пользователя в системе Телеграм, для последующий отправки уведомлений
    :param lock:
    :return:
    """
    bot = telebot.TeleBot(BOT_TOKEN)

    @bot.message_handler(commands=['start', 'help'])
    def send_message(message):
        bot.reply_to(
            message,
            'Привет, это бот трекера полезных привычек. '
            'Я буду уведомлять о всех твоих запланированных привычках',
        )
        lock.acquire()
        if message.from_user.username:
            if User.objects.filter(tele_user=message.from_user.username).exists():
                current_user = User.objects.get(tele_user=message.from_user.username)
                if not current_user.tele_id:
                    current_user.tele_id = message.from_user.id
                current_user.save()
        lock.release()

    bot.polling(none_stop=True, interval=0)


def startup():
    """
    Метод вызывается при инициализации приложения, создает и запускает поток,
    в котором выполняется код взаимодействия телеграм бота с пользователем
    :return: None
    """
    lock = Lock()
    tele_thread = Thread(target=run_telebot, args=(lock,), daemon=True)
    tele_thread.start()
