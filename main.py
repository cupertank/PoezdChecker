from pytz import timezone as tz
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters
from requests import get
from bs4 import BeautifulSoup
from time import sleep
import os


def start(bot, updater):
    if updater.message.chat_id not in users:
        users.append(updater.message.chat_id)
        f = open('users.txt', 'w')
        f.write(repr(users))
        f.close()
    print(users)


users = eval(open('users.txt').readline())
file = get('https://www.tutu.ru/poezda/view_d.php?np=b1d5d9')
soup = BeautifulSoup(file.text.encode('utf-8'), 'html.parser')
date = soup.find('tbody').findAll('tr')
if os.environ.get('TOKEN') != None:
    TOKEN = os.environ.get('TOKEN')
else:
    print('NO TOKEN!!!')
    exit()
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher
bot = updater.bot
handlers = [
    CommandHandler('start', start),
    MessageHandler(Filters.text, start)
]
for i in handlers: dispatcher.add_handler(i)
updater.start_polling()
sleep(3)
i = 9
status = 0 #0 - едем, 1 - стоим
while i < 45:
    now = datetime.now(tz=tz('Europe/Moscow'))
    temp = date[i].findAll('td')
    if status == 0:
        prib = temp[3].text.strip()
        prib = [int(prib[0:2]), int(prib[3:5])]
        if prib[0] * 60 + prib[1] - now.hour * 60 - now.minute <= 1:
            text = '''*Приехали в:* _{0}_
*Стоим тутачки:* _{1}_

*Отъезжаем в:* _{2}_'''.format(temp[2].a.text.strip(), temp[4].text.strip(), temp[5].text.strip())
            for j in users:
                bot.send_message(chat_id=j,
                                 text=text,
                                 parse_mode='Markdown')
            status = 1
    elif status == 1:
        otprv = temp[5].text.strip()
        otprv = [int(otprv[0:2]), int(otprv[3:5])]
        if now.hour * 60 + now.minute - otprv[0] * 60 - otprv[1] >= 0:
            i += 1
            temp = date[i].findAll('td')
            text = '''*Уезжаем*

*Следующая:* _{0}_
*Приезжаем в:* _{1}_'''.format(temp[2].a.text.strip(), temp[3].text.strip())
            for j in users:
                bot.send_message(chat_id=j,
                                 text=text,
                                 parse_mode='Markdown')
            status = 0
    sleep(60)
