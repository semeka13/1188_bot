import csv
from datetime import datetime

import telebot

import config

knownUsers = []
userStep = {}


def get_user_step(uid):
    if uid in userStep:
        print(userStep[uid])
        return userStep[uid]
    else:
        knownUsers.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            try:
                print(str(m.from_user.username) + " [" + str(m.chat.id) + "]: " + m.text)
            except Exception:
                print("[" + str(m.chat.id) + "]: " + m.text)


bot = telebot.TeleBot(config.TOKEN)
bot.set_update_listener(listener)


@bot.message_handler(commands=["start"])
def start(message):
    userStep[message.from_user.id] = 0
    bot.send_message(message.from_user.id, "Здравствуйте!\n"
                                           "Вас приветствует бот, который может отправить вам базу компаний сайта www.1188.lv\n"
                                           "Возможности бота:\n"
                                           "/refresh - команда для обновления базы компаний\n"
                                           "/search - поиск компаний по фильтрам (город, категория)\n"
                                           "/view_categories - список категорий\n")


@bot.message_handler(commands=["refresh"])
def refresh(message):
    bot.send_message(message.from_user.id, "Данные обновляются. Это может занять максимум 20 минут.")
    # Обновление данных
    bot.send_message(message.from_user.id,
                     "Данные обновились. Воспользуйтесь функцией /search, чтобы скачать новую базу.")


@bot.message_handler(commands=["view_categories"])
def view_categories(message):
    text = "Cписок всех категорий компаний"
    bot.send_message(message.from_user.id, text)
    file = open("categories.xlsx")
    bot.send_document(message.from_user.id, file)


'''@bot.message_handler(commands=["view_cities"])
def view_categories(message):
    text = "Cписок всех городов"
    bot.send_message(message.from_user.id, text)
    file = open("cities.xlsx")
    bot.send_document(message.from_user.id, file)'''


@bot.message_handler(commands=["search"])
def search(message):
    bot.send_message(message.from_user.id,
                     "Чтобы начать поиск, отправьте сообщение, указав номера категорий из /view_categories и /view_cities.\n"
                     "Ваше сообщение должно быть в следующем формате:\n\n"
                     "№ категории, № категории, № категории ...\n"
                     "№ города, № города, № города ...")
    userStep[message.from_user.id] = 1


@bot.message_handler(func=lambda message: get_user_step(message.from_user.id) == 1)
def filtered_data(message):
    flag = False
    data = message.text.split("\n")
    if len(data) == 2:
        categories = list(i.strip() for i in data[0].split(","))
        cities = list(i.strip() for i in data[1].split(","))
        with open('1188_base.csv', 'r') as csvfile:
            with open(f'1188_lv_{message.from_user.id}.csv', "w") as file:
                reader = csv.reader(
                    csvfile, quoting=csv.QUOTE_ALL)
                writer = csv.writer(
                    file, quoting=csv.QUOTE_ALL)
                writer.writerow(
                    ['title', 'address', 'city', 'phone', 'email', 'description', 'homepage', 'branch', 'products'])

                for row in reader:
                    if all(category in config.categories for category in categories):
                        if "1" in categories and any(city in row[1] for city in cities):
                            flag = True
                            writer.writerow(row)
                        elif any(city in row[1] for city in cities) and any(
                                config.categories[category] == row[7] for category in categories):
                            flag = True
                            writer.writerow(row)
                    else:
                        bot.send_message(message.from_user.id, "Номера должны быть в промежутке от 1 до 385")

        file = open(f'1188_lv_{message.from_user.id}.csv')
        if file and flag:
            bot.send_message(message.from_user.id, "Ваш файл загружается.")
            bot.send_document(message.from_user.id, file)
        else:
            bot.send_message(message.from_user.id, "Ничего не найдено.\n"
                                                   "Попробуйте /search с другими фильтрами.")
    else:
        bot.send_message(message.from_user.id, "В вашем сообщении должно быть две строчки.")


try:
    print("BOT UP", str(datetime.now()).split(".")[0], sep="\t")
    bot.polling(none_stop=True)
except Exception as e:
    bot.stop_bot()
    print("BOT DOWN", str(datetime.now()).split(".")[0], sep="\t")
