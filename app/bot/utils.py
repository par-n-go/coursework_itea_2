import json

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from .config import CATEGORY_TAG, ADD_PRODUCT_TO_CART_TAG
from .keyboards import START_KB
from .texts import ADD_TO_CART


def check_message_match(message, text):
    return message.text == START_KB[text]


def check_call_tag_match(call, tag):
    return json.loads(call.data)['tag'] == tag


def get_callback_data(id_: str, tag: str):
    return json.dumps({
        'id': id_,
        'tag': tag,
    })


def generate_categories_kb(categories_qs):
    buttons = []
    kb = InlineKeyboardMarkup()
    for c in categories_qs:
        data = get_callback_data(str(c.id), CATEGORY_TAG)
        buttons.append(InlineKeyboardButton(c.title, callback_data=data))
    kb.add(*buttons)
    return kb


def generate_add_to_cart_button(id_: str):
    kb = InlineKeyboardMarkup()
    button = InlineKeyboardButton(ADD_TO_CART,
                                  callback_data=get_callback_data(id_, ADD_PRODUCT_TO_CART_TAG))
    kb.add(button)
    return kb
