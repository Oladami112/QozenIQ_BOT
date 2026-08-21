import os
import logging
from flask import Flask, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import asyncio

# Flask app for healthcheck
app = Flask(__name__)

@app.route('/')
def healthcheck():
    return jsonify({"status": "healthy", "message": "QozenIQ Bot is running!"}), 200

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    logger.error("❌ BOT_TOKEN not set!")
    exit(1)

logger.info(f"✅ Bot token loaded: {TOKEN[:10]}...")

# About text (116 chars)
ABOUT_TEXT = """🤖 QozenIQ - Your smart AI assistant for quick answers, info, and insights. Fast, private, and helpful! ✨"""

# Create bot application
application = Application.builder().token(TOKEN).build()

# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome = f"""👋 *Welcome to QozenIQ, {user.first_name}!*

Your intelligent assistant is ready to help you.

📌 *Quick Start:*
• /help - See all commands
• /about - Learn more
• /ping - Check status

Type /help to get started! 🚀"""

    keyboard = [
        [InlineKeyboardButton("📚 Help", callback_data='help')],
        [InlineKeyboardButton("ℹ️ About", callback_data='about')],
        [InlineKeyboardButton("🔄 Ping", callback_data='ping')]
    ]
    await update.message.reply_text(welcome, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """📚 *QozenIQ Bot Commands*

/start - Welcome message
/help - Show this help
/about - Learn about QozenIQ
/ping - Check bot status

💡 Just type your question!"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='start')]]
    await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='start')]]
    await update.message.reply_text(ABOUT_TEXT, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 *Pong!*\n\nBot is online and ready! ✅", parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'start':
        user = update.effective_user
        await query.edit_message_text(
            f"👋 *Welcome back, {user.first_name}!*\n\nReady to help you. Use /help to see commands.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📚 Help", callback_data='help')],
                [InlineKeyboardButton("ℹ️ About", callback_data='about')],
                [InlineKeyboardButton("🔄 Ping", callback_data='ping')]
            ])
        )
    elif query.data == 'help':
        await query.edit_message_text(
            "📚 *Quick Help*\n\nCommands: /start, /help, /about, /ping",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='start')]])
        )
    elif query.data == 'about':
        await query.edit_message_text(
            ABOUT_TEXT,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='start')]])
        )
    elif query.data == 'ping':
        await query.edit_message_text(
            "🏓 *Pong!*\n\nEverything is working perfectly! ✅",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='start')]])
        )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower()
    
    if any(word in msg for word in ['hello', 'hi', 'hey']):
        response = "👋 Hello! How can I help?"
    elif 'how are you' in msg:
        response = "🤖 I'm great! Ready to assist you."
    elif 'thanks' in msg or 'thank' in msg:
        response = "😊 You're welcome!"
    elif 'help' in msg:
        response = "💡 Type /help to see all commands."
    elif 'about' in msg:
        response = "ℹ️ Type /about to learn more."
    else:
        response = f"🤔 Got: '{update.message.text}'\n\nType /help for commands."
    
    await update.message.reply_text(response, parse_mode='Markdown')

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("about", about_command))
application.add_handler(CommandHandler("ping", ping_command))
application.add_handler(CallbackQueryHandler(button_callback))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# --- Main Function ---
def run_bot():
    """Run the bot with proper event loop."""
    logger.info("🤖 Starting bot polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

def run_flask():
    """Run Flask server."""
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🌐 Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    logger.info("🚀 Starting QozenIQ Bot...")
    
    # Method 1: Try running bot directly (simplest)
    try:
        # Run both using asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Start bot polling in background
        async def run_bot_async():
            await application.initialize()
            await application.start()
            await application.updater.start_polling()
            logger.info("✅ Bot is running!")
            # Keep running
            while True:
                await asyncio.sleep(3600)
        
        # Run Flask in a thread
        import threading
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        # Run bot
        loop.run_until_complete(run_bot_async())
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        # Fallback to simple polling
        logger.info("🔄 Trying fallback method...")
        run_bot()
