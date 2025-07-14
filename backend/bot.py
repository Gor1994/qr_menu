import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton,WebAppInfo, InputMediaPhoto, InputMediaVideo, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from pymongo import MongoClient
from urllib.parse import quote, unquote
import traceback
import aiohttp
from telegram import InputFile
from io import BytesIO
from bson import ObjectId

MONGO_URI = 'mongodb+srv://karapetyangor94:oKfGj2pbXhruOJ0F@cluster1.ullp5.mongodb.net/nts-company?retryWrites=true&w=majority'
client = MongoClient(MONGO_URI)
db = client['nts-company']
gallery=db["bot_content"]
# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)



main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("🛍 КУПИТЬ")],
        [KeyboardButton("📂 КАТАЛОГ"), KeyboardButton("🖼 ГАЛЕРЕЯ")],
        [KeyboardButton("ℹ️ О КОМПАНИИ"), KeyboardButton("⭐ ОТЗЫВЫ")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

gallery_main_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("📦 Видео-распаковки", callback_data="gallery_unpack")],
    [InlineKeyboardButton("🎥 Видеообзоры", callback_data="gallery_reviews")],
    [InlineKeyboardButton("📸 Фотографии", callback_data="gallery_photos")]
])

def parse_callback_data(data):
    parts = data.split("_", 2)
    return parts[0], parts[1], parts[2] if len(parts) == 3 else None
    # returns (type, brand_or_branch, model_or_brand)

def normalize(s):
    return s.strip().lower().replace(" ", "").replace("-", "").replace("_", "")

# def get_buy_button(brand):
#     is_iphone = normalize(brand) == "apple"
#     target = "iphone" if is_iphone else "android"
#     return InlineKeyboardMarkup([
#         [InlineKeyboardButton("🛍 КУПИТЬ", web_app=WebAppInfo(url=f"https://nts-online.ru?scroll={target}"))]
#     ])

def get_buy_button(brand, back_callback_data="gallery_back"):
    is_iphone = normalize(brand) == "apple"
    target = "iphone" if is_iphone else "android"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍 КУПИТЬ", web_app=WebAppInfo(url=f"https://nts-online.ru?scroll={target}"))],
        [InlineKeyboardButton("🔙 Назад", callback_data=back_callback_data)]
    ])

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    logger.info(f"🧩 Raw callback data: {data}")

    if data == "find_dream":
        await send_gallery_main_menu(query.message.chat.id, context.bot)
    elif data == "gallery_back":
        try:
            await query.message.delete()  # delete the last message
        except Exception as e:
            logger.warning(f"Failed to delete message: {e}")

        # Then send the original brand/model selection menu again
        await send_gallery_main_menu(update.effective_chat.id, context.bot)

    elif data in ["gallery_photos", "gallery_reviews", "gallery_unpack"]:
        await delete_previous_message(update, context) 
        label_map = {
            "gallery_photos": ("Фото", "photos"),
            "gallery_reviews": ("Видеообзоры", "review"),
            "gallery_unpack": ("Видео-распаковки", "unpacking")
        }
        label, prefix = label_map[data]
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📱 Айфоны", callback_data=f"{prefix}_iphones")],
            [InlineKeyboardButton("🤖 Андроиды", callback_data=f"{prefix}_android")]
        ])
        await query.edit_message_text(f"Выберите категорию для {label}:", reply_markup=keyboard)
    elif data == "catalog_iphones":
        await query.edit_message_text(
            text="📱 Перейти к iPhone:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Открыть iPhone каталог", web_app=WebAppInfo(url="https://nts-online.ru?scroll=iphone"))]
            ])
        )

    elif data == "catalog_androids":
        print(f"herejnsjnsfdn")
        await query.edit_message_text(
            text="🤖 Перейти к Android:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Открыть Android каталог", web_app=WebAppInfo(url="https://nts-online.ru?scroll=android"))]
            ])
        )
    elif data.endswith("_iphones"):
        print(f"herejnsjnsfdn")
        await delete_previous_message(update, context) 
        content_type = data.split("_")[0]
        
        # get Apple models of that type
        docs = list(gallery.find({"brand": "Apple", "type": content_type}))
        buttons = []

        for doc in docs:
            model = doc.get("model")
            if model:
                buttons.append([
                    InlineKeyboardButton(model, callback_data=f"model_{str(doc['_id'])}")
                ])

        buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="gallery_back")])
        await query.edit_message_text(f"Выберите модель iPhone ({content_type}):", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.endswith("_android"):
        print(f"herejnsjnsfdn")
        await delete_previous_message(update, context) 
        content_type = data.split("_")[0]
        
        # Distinct Android brands
        brands = gallery.distinct("brand", {"brand": {"$ne": "Apple"}, "type": content_type})
        buttons = []

        for brand in brands:
            buttons.append([
                InlineKeyboardButton(brand, callback_data=f"{content_type}_brand_{quote(brand)}")
            ])

        buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="gallery_back")])
        await query.edit_message_text(f"Выберите бренд Android ({content_type}):", reply_markup=InlineKeyboardMarkup(buttons))


    elif data.startswith("model_"):
        doc_id = data.replace("model_", "")
        doc = gallery.find_one({"_id": ObjectId(doc_id)})

        if not doc:
            await query.edit_message_text("⚠️ Модель не найдена.")
            return

        model = doc.get("model", "")
        brand = doc.get("brand", "")
        content_type = doc.get("type", "")

        if "submodels" in doc and doc["submodels"]:
            buttons = [[InlineKeyboardButton(
                sub["name"],
                callback_data=f"v_{str(doc['_id'])}_{i}"
            )] for i, sub in enumerate(doc["submodels"])]
            buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="gallery_back")])
            await query.edit_message_text(
                f"Выберите версию модели {model}:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await query.edit_message_text("⚠️ У этой модели нет подверсий.")
            
    elif data.startswith(("photos_brand_", "review_brand_", "unpacking_brand_")):
        print(f"herejnsjnsfdn")
        content_type, _, brand = parse_callback_data(data)
        brand = unquote(brand)
        models = gallery.distinct("model", {"brand": brand, "type": content_type})
        buttons = [[InlineKeyboardButton(model, callback_data=f"{content_type}_{brand}_{quote(model)}")] for model in models]
        buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="gallery_back")])
        await query.edit_message_text(f"Выберите модель {brand}:", reply_markup=InlineKeyboardMarkup(buttons))

    # ✅ Submodel selected
    elif data.count("_") >= 3:
        print(f"herejnsjnsfdn")
        parts = data.split("_", 3)
        if len(parts) != 4:
            return
        content_type, brand, raw_model, raw_submodel = parts
        model = unquote(raw_model)
        submodel = unquote(raw_submodel)

        logger.info(f"📦 Submodel requested: {brand} {model} - {submodel}")
        doc = gallery.find_one({
            "brand": {"$regex": f"^{brand}$", "$options": "i"},
            "model": {"$regex": f"^{model}$", "$options": "i"},
            "type": content_type
        })

        if not doc or "submodels" not in doc:
            await query.edit_message_text("⚠️ Контент не найден.")
            return

        submodel_norm = normalize(submodel)
        match = next((s for s in doc["submodels"] if normalize(s["name"]) == submodel_norm), None)

        if not match or not match.get("files"):
            await query.edit_message_text("⚠️ Контент не найден для этой версии.")
            return

        try:
            # Clean up previous gallery messages
            if "last_gallery_message_ids" in context.user_data:
                for msg_id in context.user_data["last_gallery_message_ids"]:
                    try:
                        await context.bot.delete_message(chat_id=query.message.chat.id, message_id=msg_id)
                    except Exception as e:
                        logger.warning(f"Could not delete message {msg_id}: {e}")
                context.user_data.pop("last_gallery_message_ids", None)

            caption = match.get("caption", "")
            caption_used = False
            last_message_ids = []

            for url in match["files"][:10]:
                is_image = url.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
                is_video = url.lower().endswith((".mp4", ".mov", ".mkv"))

                if is_image:
                    msg = await context.bot.send_photo(
                        chat_id=query.message.chat.id,
                        photo=url,
                        caption=caption if not caption_used else None,
                        reply_markup=get_buy_button(brand)  # or get_buy_and_back_buttons(brand)
                    )
                    last_message_ids.append(msg.message_id)
                    caption_used = True

                elif is_video:
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url) as resp:
                                if resp.status == 200:
                                    video_bytes = await resp.read()
                                    video_stream = BytesIO(video_bytes)
                                    video_stream.name = "video.mp4"
                                    msg = await context.bot.send_video(
                                        chat_id=query.message.chat.id,
                                        video=InputFile(video_stream),
                                        caption=caption if not caption_used else None,
                                        reply_markup=get_buy_button(brand)  # or get_buy_and_back_buttons(brand)
                                    )
                                    last_message_ids.append(msg.message_id)
                                    caption_used = True
                                else:
                                    logger.warning(f"Failed to fetch video: {url} | Status: {resp.status}")
                    except Exception as e:
                        logger.error(f"Failed to download/send video: {url} | {e}")

                else:
                    logger.warning(f"Unsupported media: {url}")

            if last_message_ids:
                context.user_data["last_gallery_message_ids"] = last_message_ids

        except Exception as e:
            logger.error(f"Error sending submodel media: {e}")
            logger.error(traceback.format_exc())
            await query.edit_message_text("⚠️ Ошибка при загрузке контента.")


    # ✅ Regular model selected (check for submodels or content)
    elif data.startswith(("photos_", "review_", "unpacking_")) and data.count("_") >= 2:
        print(f"herejnsjnsfdn")
        content_type, brand, model = parse_callback_data(data)
        model = unquote(model)

        logger.info(f"🎯 Model selected: {brand} {model} ({content_type})")
        doc = gallery.find_one({
            "brand": {"$regex": f"^{brand}$", "$options": "i"},
            "model": {"$regex": f"^{model}$", "$options": "i"},
            "type": content_type
        })

        if not doc:
            await query.edit_message_text("⚠️ Контент не найден.")
            return

        if "submodels" in doc and doc["submodels"]:
            # buttons = [[InlineKeyboardButton(
            #     sub["name"],
            #     callback_data=f"{content_type}_{brand}_{quote(model)}_{quote(sub['name'])}"
            # )] for sub in doc["submodels"]]
            buttons = [[InlineKeyboardButton(
                sub["name"],
                callback_data=f"v_{str(doc['_id'])}_{i}"
            )] for i, sub in enumerate(doc["submodels"])]

            buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="gallery_back")])
            await query.edit_message_text(
                f"Выберите версию модели {model}:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

        if not doc.get("files"):
            await query.edit_message_text("⚠️ Контент не найден.")
            return

        try:
            # Clean up previous messages
            if "last_gallery_message_ids" in context.user_data:
                for msg_id in context.user_data["last_gallery_message_ids"]:
                    try:
                        await context.bot.delete_message(chat_id=query.message.chat.id, message_id=msg_id)
                    except Exception as e:
                        logger.warning(f"Could not delete message {msg_id}: {e}")
                context.user_data.pop("last_gallery_message_ids", None)

            last_message_ids = []
            caption_used = False

            for url in doc["files"][:10]:
                is_image = content_type == "photos" or url.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
                is_video = url.lower().endswith((".mp4", ".mov", ".mkv"))

                if is_image:
                    msg = await context.bot.send_photo(
                        chat_id=query.message.chat.id,
                        photo=url,
                        caption=caption if not caption_used else None,
                        reply_markup=get_buy_button(brand)
                    )
                    last_message_ids.append(msg.message_id)
                    caption_used = True

                elif is_video:
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url) as resp:
                                if resp.status == 200:
                                    video_bytes = await resp.read()
                                    video_stream = BytesIO(video_bytes)
                                    video_stream.name = "video.mp4"
                                    msg = await context.bot.send_video(
                                        chat_id=query.message.chat.id,
                                        video=InputFile(video_stream),
                                        caption=caption if not caption_used else None,
                                        reply_markup=get_buy_button(brand)
                                    )
                                    last_message_ids.append(msg.message_id)
                                    caption_used = True
                                else:
                                    logger.warning(f"Failed to fetch video: {url} | Status: {resp.status}")
                    except Exception as e:
                        logger.error(f"Failed to download or send video: {url} | {e}")
                else:
                    logger.warning(f"Unsupported media: {url}")

            context.user_data["last_gallery_message_ids"] = last_message_ids


        except Exception as e:
            logger.error(f"Error sending media group: {e}")
            await query.edit_message_text("⚠️ Ошибка при загрузке контента.")
    elif data.startswith("v_"):  # View submodel by doc ID and index
        print(f"herejnsjnsfdn")
        try:
            _, doc_id, sub_idx = data.split("_")
            doc = gallery.find_one({"_id": ObjectId(doc_id)})
            sub_idx = int(sub_idx)

            if not doc or "submodels" not in doc or sub_idx >= len(doc["submodels"]):
                await query.edit_message_text("⚠️ Контент не найден.")
                return

            brand = doc.get("brand", "")
            model = doc.get("model", "")
            match = doc["submodels"][sub_idx]
            caption = match.get("caption", "")
            caption_used = False

            # Clean up previous media
            if "last_gallery_message_ids" in context.user_data:
                for msg_id in context.user_data["last_gallery_message_ids"]:
                    try:
                        await context.bot.delete_message(chat_id=query.message.chat.id, message_id=msg_id)
                    except Exception as e:
                        logger.warning(f"Could not delete message {msg_id}: {e}")
                context.user_data.pop("last_gallery_message_ids", None)
            media_urls = match.get("files", [])[:1]  # Just take the first one
            if not media_urls:
                await query.edit_message_text("⚠️ Медиа не найдено.")
                return

            url = media_urls[0]
            is_image = url.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
            is_video = url.lower().endswith((".mp4", ".mov", ".mkv"))

            if is_image:
                msg = await context.bot.send_photo(
                    chat_id=query.message.chat.id,
                    photo=url,
                    caption=caption,
                    reply_markup=get_buy_button(brand)
                )
                context.user_data["last_gallery_message_ids"] = [msg.message_id]

            elif is_video:
                print(f"here")
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            video_bytes = await resp.read()
                            video_stream = BytesIO(video_bytes)
                            video_stream.name = "video.mp4"
                            msg = await context.bot.send_video(
                                chat_id=query.message.chat.id,
                                video=InputFile(video_stream),
                                caption=caption,
                                reply_markup=get_buy_button(brand)
                            )
                            context.user_data["last_gallery_message_ids"] = [msg.message_id]
                        else:
                            await query.edit_message_text("⚠️ Не удалось загрузить видео.")
                            return
            else:
                await query.edit_message_text("⚠️ Формат файла не поддерживается.")
                return

        except Exception as e:
            logger.error(f"Error handling short callback_data: {e}")
            await query.edit_message_text("⚠️ Ошибка при загрузке контента.")

            


async def send_gallery_main_menu(chat_id, bot):
    gallery_main_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Видео-распаковки", callback_data="gallery_unpack")],
        [InlineKeyboardButton("🎥 Видеообзоры", callback_data="gallery_reviews")],
        [InlineKeyboardButton("📸 Фотографии", callback_data="gallery_photos")]
    ])
    await bot.send_message(chat_id=chat_id, text="Выберите раздел из Галереи 👇", reply_markup=gallery_main_keyboard)

# /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"👋 Привет, {user.first_name}!\n\n"
        "📱 Компания «Надежные смартфоны» — ваш проводник в мир технологий, "
        "где главенствуют надежность, выгода и забота о каждом покупателе!\n\n"
        "🏆 Мы продали около 1 000 000 смартфонов — нам доверяют во всех регионах России\n"
        "🔒 100% оригинальная продукция\n"
        "🛡 Гарантия до 2-х лет\n"
        "💸 Мгновенный возврат денег, если что-то не понравится\n\n"
        "🔥 ТОЛЬКО У НАС:\n"
        "✅ Дополнительная скидка 10% при оплате наличными\n"
        "💰 10% кэшбек через приложение Т-Банка (раздел «Кэшбек у партнёров»)\n"
        "📅 Рассрочка со скидкой до 10%\n"
        "🚚 Бесплатная доставка (в день заказа — в регионах присутствия)\n\n"
        "🕘 Онлайн-поддержка 24/7 — мы всегда на связи!\n\n"
        "Нажмите на кнопку ниже ⬇️ и откройте мир выгодных и надёжных покупок, проверенных миллионами!"
    )
    inline_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼 ГАЛЕРЕЯ", callback_data="find_dream")]
    ])
    # Сначала отправляем приветствие с кнопкой «НАЙТИ СМАРТФОН МЕЧТЫ»
    # await update.message.reply_text(welcome_text, reply_markup=inline_keyboard)
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo="https://nts-center.ru/uploads/photos/nts_welcome_message.png",  # Replace with actual image URL
        caption=welcome_text,
        reply_markup=inline_keyboard,
        parse_mode="HTML"  # Or "MarkdownV2" if your text uses markdown
    )   

    # Затем отправляем полноценное меню
    await update.message.reply_text("👇 Главное меню:", reply_markup=main_menu_keyboard)

async def delete_previous_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if context.user_data.get("last_bot_message_id"):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data["last_bot_message_id"]
            )
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение: {e}")

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🛍 КУПИТЬ":
        await delete_previous_message(update, context)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛍 Перейти в магазин", web_app=WebAppInfo(url="https://nts-online.ru"))]
        ])
        msg1 =await update.message.reply_text("👇 Нажмите кнопку ниже, чтобы перейти:", reply_markup=keyboard)
        context.user_data["last_bot_message_id"] = msg1.message_id


    elif text == "🖼 ГАЛЕРЕЯ":
        await delete_previous_message(update, context)
        await send_gallery_main_menu(update.effective_chat.id, context.bot)
    elif text == "📂 КАТАЛОГ":
        await delete_previous_message(update, context)

        # Remove the menu (restores 4-dot Telegram menu button)
        # await update.message.reply_text("⏳ Загрузка категорий...", reply_markup=ReplyKeyboardRemove())

        # Send categories as inline buttons
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📱 Айфоны", callback_data="catalog_iphones")],
            [InlineKeyboardButton("🤖 Андроиды", callback_data="catalog_androids")]
        ])
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выберите категорию:",
            reply_markup=keyboard
        )
        context.user_data["last_bot_message_id"] = msg.message_id
        
    # elif text == "📱 Айфоны":
    #     await delete_previous_message(update, context)
    #     keyboard = InlineKeyboardMarkup([
    #         [InlineKeyboardButton("📱 Перейти к iPhone", web_app=WebAppInfo(url="https://nts-online.ru?scroll=iphone"))]
    #     ])
    #     msg=await update.message.reply_text("Выберите в Telegram-магазине:", reply_markup=keyboard)
    #     context.user_data["last_bot_message_id"] = msg.message_id

    # elif text == "🤖 Андроиды":
    #     await delete_previous_message(update, context)
    #     keyboard = InlineKeyboardMarkup([
    #         [InlineKeyboardButton("🤖 Перейти к Android", web_app=WebAppInfo(url="https://nts-online.ru?scroll=android"))]
    #     ])
    #     msg=await update.message.reply_text("Выберите в Telegram-магазине:", reply_markup=keyboard)
    #     context.user_data["last_bot_message_id"] = msg.message_id

    elif text == "ℹ️ О КОМПАНИИ":
        await delete_previous_message(update, context)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ℹ️ Подробнее о компании", url="https://www.nts-company.ru/about")]
        ])
        msg=await update.message.reply_text("Открыть страницу:", reply_markup=keyboard)
        context.user_data["last_bot_message_id"] = msg.message_id

    elif text == "⭐ ОТЗЫВЫ":
        await delete_previous_message(update, context)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐ Читать отзывы", url="https://www.nts-company.ru/reviews")]
        ])
        msg=await update.message.reply_text("Отзывы:", reply_markup=keyboard)
        context.user_data["last_bot_message_id"] = msg.message_id
    elif text == "⬅️ Назад":
        await start(update, context)

# Main execution block
if __name__ == '__main__':
    # Replace with your token
    bot_token = "8053579909:AAH85DDtqdUgm-f5motmn872jhwH7chLtDM"

    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("🤖 NTS-Company Bot is running...")
    app.run_polling()
