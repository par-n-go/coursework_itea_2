import json
from .config import TOKEN, CATEGORY_TAG, ADD_PRODUCT_TO_CART_TAG
from .keyboards import START_KB
import app.bot.utils as bot_utils
from .texts import GREETINGS, PICK_CATEGORY
from ..models.models import Category, User, Product
from telebot import TeleBot
from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)

bot = TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    User.initial_create(message.chat.id, message.from_user.first_name)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [KeyboardButton(button) for button in START_KB.values()]
    kb.add(*buttons)
    bot.send_message(
        message.chat.id,
        GREETINGS,
        reply_markup=kb
    )


@bot.message_handler(func=lambda m: bot_utils.check_message_match(m, 'category'))
def show_categories(message):
    kb = bot_utils.generate_categories_kb(Category.get_root_categories())
    bot.send_message(
        message.chat.id,
        PICK_CATEGORY,
        reply_markup=kb
    )


@bot.callback_query_handler(func=lambda c: bot_utils.check_call_tag_match(c, CATEGORY_TAG))
def category(call):
    category = Category.objects.get(id=json.loads(call.data)['id'])

    if category.subcategories:
        kb = bot_utils.generate_categories_kb(category.subcategories)
        bot.edit_message_text(
            category.title,
            call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=kb
        )
    else:
        for product in category.get_products():
            bot.send_photo(
                call.message.chat.id,
                product.image.read(),
                caption='Описание',
                reply_markup=bot_utils.generate_add_to_cart_button(
                    id_=str(product.id)
                )
                #caption=product.get_formatted_text()

            )


@bot.callback_query_handler(func=lambda c: bot_utils.check_call_tag_match(c, ADD_PRODUCT_TO_CART_TAG))
def handle_add_to_cart(call):
    product_id = json.loads(call.data)['id']
    product = Product.objects.get(id=product_id)
    user = User.objects.get(telegram_id=call.message.chat.id)
    cart = user.get_cart()
    cart.add_product(product)
    bot.send_message(
        call.message.chat.id,
        f'Продукт {product.title} добавлен в корзину'
    )

