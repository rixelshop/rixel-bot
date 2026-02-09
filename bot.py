import telebot
from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
import os

TOKEN = "8365055039:AAEbijAn0d0liOHr0NOzsnVKIJUZ6-MeoZ0"
ADMIN_ID = 8525002075  # O'zingizning Telegram ID

bot = telebot.TeleBot(TOKEN)

user_data = {}


# ================= MAIN MENU =================

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton("Tungi Led chiroq"),
        KeyboardButton("Sumkachali sovg'a")
    )
    markup.add(
        KeyboardButton("Kitob o'qish uchun led"),
        KeyboardButton("Sayyora projector")
    )
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Assalomu alaykum Rixelning rasmiy botiga xush kelibsiz!\nKerakli bo'limni tanlang:",
        reply_markup=main_menu()
    )


# ================= PRODUCT FUNCTION =================

def send_product(message, product_name, images, text):

    for img in images:
        with open(img, "rb") as photo:
            bot.send_photo(message.chat.id, photo)

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            "🛒 Buyurtma berish",
            callback_data=f"order|{product_name}"
        )
    )

    bot.send_message(message.chat.id, text, reply_markup=markup)


# ================= ORDER START =================

@bot.callback_query_handler(func=lambda call: call.data.startswith("order|"))
def start_order(call):

    product_name = call.data.split("|")[1]

    user_data[call.message.chat.id] = {
        "step": "name",
        "product": product_name
    }

    bot.send_message(call.message.chat.id, "👤 Ismingizni kiriting:")


# ================= CONTACT HANDLER =================

@bot.message_handler(content_types=['contact'])
def contact_handler(message):

    chat_id = message.chat.id

    if chat_id in user_data and user_data[chat_id]["step"] == "phone":
        user_data[chat_id]["phone"] = message.contact.phone_number
        user_data[chat_id]["step"] = "address"

        back_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        back_markup.add(KeyboardButton("⬅️ Ortga"))

        bot.send_message(chat_id, "📍 Manzilingizni kiriting:", reply_markup=back_markup)


# ================= TEXT HANDLER =================

@bot.message_handler(content_types=['text'])
def handle_text(message):

    chat_id = message.chat.id

    # ===== BACK BUTTON =====
    if message.text == "⬅️ Ortga":
        bot.send_message(chat_id, "Asosiy menyu:", reply_markup=main_menu())
        return

    # ===== ORDER STEPS =====
    if chat_id in user_data:

        if user_data[chat_id]["step"] == "name":
            user_data[chat_id]["name"] = message.text
            user_data[chat_id]["step"] = "phone"

            contact_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            contact_btn = KeyboardButton("📞 Raqamni yuborish", request_contact=True)
            contact_markup.add(contact_btn)

            bot.send_message(chat_id, "📞 Telefon raqamingizni yuboring:", reply_markup=contact_markup)
            return

        elif user_data[chat_id]["step"] == "phone":
            user_data[chat_id]["phone"] = message.text
            user_data[chat_id]["step"] = "address"

            back_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            back_markup.add(KeyboardButton("⬅️ Ortga"))

            bot.send_message(chat_id, "📍 Manzilingizni kiriting:", reply_markup=back_markup)
            return

        elif user_data[chat_id]["step"] == "address":
            user_data[chat_id]["address"] = message.text

            order_text = f"""
🛒 YANGI BUYURTMA

📦 Mahsulot: {user_data[chat_id]['product']}
👤 Ism: {user_data[chat_id]['name']}
📞 Telefon: {user_data[chat_id]['phone']}
📍 Manzil: {user_data[chat_id]['address']}
"""

            bot.send_message(ADMIN_ID, order_text)
            bot.send_message(chat_id, "✅ Buyurtmangiz qabul qilindi!", reply_markup=main_menu())

            del user_data[chat_id]
            return

    # ===== PRODUCTS =====

    if message.text == "Tungi Led chiroq":
        text = """✨ RANGLI LED LAMPA
🔥 NARXI: 95 000 so‘m 🔥"""
        send_product(message, "Tungi Led chiroq", ["tungi1.jpg", "tungi2.jpg"], text)

    elif message.text == "Sumkachali sovg'a":
        text = """✨ SUMKACHALI LAMPA
🔥 NARXI: 85 000 so‘m 🔥"""
        send_product(message, "Sumkachali sovg'a", ["sumka1.jpg", "sumka2.jpg", "sumka3.jpg"], text)

    elif message.text == "Kitob o'qish uchun led":
        text = """📖 KITOB LED
🔥 NARXI: 65 000 so‘m 🔥"""
        send_product(message, "Kitob o'qish uchun led", ["kitob1.jpg", "kitob2.jpg"], text)

    elif message.text == "Sayyora projector":
        text = """🪐 SAYYORA PROYEKTORI
🔥 NARXI: 90 000 so‘m 🔥"""
        send_product(message, "Sayyora projector", ["sayyora1.jpg", "sayyora2.jpg"], text)


print("Bot ishlayapti...")
bot.polling()
