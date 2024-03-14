from telegram.ext import ApplicationBuilder, filters, CommandHandler, MessageHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN, admins_id
import sqlite3

conn = sqlite3.connect('music.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS musics
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
               file_id TEXT,
               title TEXT)''')
conn.commit()


async def start(update, context):
    await update.message.reply_text(
        text="Buyroqni tanlang", reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton(text='/start'),
             KeyboardButton(text='/delete')],
            [KeyboardButton(text='/nasheed')]
        ], resize_keyboard=True))


async def handle_music(update, context):
    isAdmin = update.message.from_user.id in admins_id
    file_id = update.message.audio.file_id
    title = update.message.audio.title
    if isAdmin:
        cursor.execute('SELECT * FROM musics WHERE file_id = ?', (file_id,))
        existing_music = cursor.fetchone()
        if existing_music:
            await update.message.reply_text('Bu musiqa fayli allaqachon saqlangan!')
        else:
            cursor.execute(
                'INSERT INTO musics (file_id, title) VALUES (?, ?)', (file_id, title))
            conn.commit()
            await update.message.reply_text('Musiqa muvaffaqiyatli saqlandi!')

    else:
        await update.message.reply_text("Sizga ruxsat yo'q")


async def nasheed(update, context):
    cursor.execute('SELECT * FROM musics')
    musics = cursor.fetchall()
    if musics:
        for music in musics:
            await context.bot.send_audio(
                chat_id=update.effective_chat.id, audio=music[1], title=music[2])
    else:
        await update.message.reply_text('Hozircha hech qanday musiqa mavjud emas.')


async def delete(update, context):
    isAdmin = update.message.from_user.id in admins_id
    if isAdmin:
        cursor.execute('DELETE FROM musics')
        conn.commit()
        await update.message.reply_text('Barcha musiqa fayllari muvaffaqiyatli o\'chirildi!')
    else:
        await update.message.reply_text("Sizga Ruxsat yo'q")


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("nasheed", nasheed))
    app.add_handler(CommandHandler("delete", delete))
    app.add_handler(MessageHandler(filters.AUDIO, handle_music))

    app.run_polling()


if __name__ == '__main__':
    main()
