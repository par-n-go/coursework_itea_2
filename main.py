from app.bot.bot import bot
from app.bot.config import WEBHOOK_URL
from flask import Flask, request, abort
from telebot.types import Update

app = Flask(__name__)


@app.route('/tg/webhook/', methods=['GET', 'POST'])
def handle_webhook():
    if request.content_type == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK'
    else:
        abort(403)


if __name__ == '__main__':
    from time import sleep

    bot.remove_webhook()
    sleep(1)
    bot.set_webhook(
        url=WEBHOOK_URL,
        certificate=open('webhook_cert.pem', 'r')
    )
    app.run(host='127.0.0.1', port=8000, debug=True)


