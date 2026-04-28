import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ----- تنظیمات -----
BOT_TOKEN = "665419412:REnWbsHEGIC_EP0kjB_VbKhxzTpLyZsFPG4"

# آدرس Bot API که روی سرورت ران کردی
CUSTOM_BASE_URL = "https://tapi.bale.ai/bot"
CUSTOM_BASE_FILE_URL = "https://your-server.com/file/bot"
# -------------------


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هر پیامی بیاد همونو برمی‌گردونه."""
    if update.message is None:
        return

    await update.message.reply_text(update.message.text)


async def main():
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .base_url(CUSTOM_BASE_URL)
        .base_file_url(CUSTOM_BASE_FILE_URL)
        .build()
    )

    # هندل پیام‌های متنی
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    )

    print("Echo Bot is running with custom Bot API...")
    await application.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
