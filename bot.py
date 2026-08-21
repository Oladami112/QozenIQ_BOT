import os
import logging
import threading
import sys
from flask import Flask, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import InvalidToken, NetworkError

# Flask app for healthcheck
app = Flask(__name__)

@app.route('/')
def healthcheck():
    return jsonify({"status": "healthy", "message": "QozenIQ Bot is running!"}), 200

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

# Enable logging with more detail
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment variable
TOKEN = os.environ.get('BOT_TOKEN')

# Check if token exists
if not TOKEN:
    logger.error("❌ BOT_TOKEN environment variable not set!")
    sys.exit(1)
else:
    logger.info(f"✅ Bot token found: {TOKEN[:10]}...")

# About text - 116 characters
ABOUT_TEXT = """🤖 QozenIQ - Your smart AI assistant for quick answers, info, and insights. Fast, private, and helpful! ✨"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when /start is issued."""
    user = update.effective_user
    welcome_message = f"""👋 *Welcome to QozenIQ, {user.first_name}!*

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
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    logger.info(f"User {user.first_name} started the bot")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when /help is issued."""
    help_text = """📚 *QozenIQ Bot Commands*

🤖 *Basic Commands:*
/start - Welcome message
/help - Show this help
/about - Learn about QozenIQ
/ping - Check bot status

💡 *Tips:*
• Type your question naturally
• I'll try my best to help you
• Be respectful and kind

🔄 *Questions?*
Contact @QozenIQ_Support for assistance"""

    keyboard = [
        [InlineKeyboardButton("🔙 Back to Start", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when /about is issued."""
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Start", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        ABOUT_TEXT,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when /ping is issued."""
    await update.message.reply_text(
        "🏓 *Pong!*\n\nBot is online and ready! ✅",
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'start':
        user = update.effective_user
        welcome_message = f"""👋 *Welcome back, {user.first_name}!*

Ready to help you. Use /help to see commands."""
        await query.edit_message_text(
            welcome_message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📚 Help", callback_data='help')],
                [InlineKeyboardButton("ℹ️ About", callback_data='about')],
                [InlineKeyboardButton("🔄 Ping", callback_data='ping')]
            ])
        )
    elif query.data == 'help':
        help_text = """📚 *Quick Help*

Commands:
/start - Welcome
/help - This help
/about - About QozenIQ
/ping - Check status"""
        await query.edit_message_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data='start')]
            ])
        )
    elif query.data == 'about':
        await query.edit_message_text(
            ABOUT_TEXT,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data='start')]
            ])
        )
    elif query.data == 'ping':
        await query.edit_message_text(
            "🏓 *Pong!*\n\nEverything is working perfectly! ✅",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data='start')]
            ])
        )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message - simple response."""
    user_message = update.message.text
    
    # Simple responses based on keywords
    if any(word in user_message.lower() for word in ['hello', 'hi', 'hey']):
        response = "👋 Hello there! How can I help you today?"
    elif 'how are you' in user_message.lower():
        response = "🤖 I'm doing great! Ready to assist you."
    elif 'thanks' in user_message.lower() or 'thank you' in user_message.lower():
        response = "😊 You're welcome! Happy to help."
    elif 'help' in user_message.lower():
        response = "💡 Type /help to see all available commands."
    elif 'about' in user_message.lower():
        response = "ℹ️ Type /about to learn more about QozenIQ."
    else:
        response = f"🤔 Got: '{user_message}'\n\nType /help for available commands."
    
    await update.message.reply_text(
        response,
        parse_mode='Markdown'
    )

def run_bot():
    """Run the Telegram bot."""
    try:
        # Create application
        application = Application.builder().token(TOKEN).build()
        logger.info("✅ Application built successfully")

        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("ping", ping_command))
        
        # Add callback query handler for buttons
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Handle non-command messages
        from telegram.ext import MessageHandler, filters
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

        # Start the bot
        logger.info("🤖 Bot is starting polling...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except InvalidToken as e:
        logger.error(f"❌ Invalid Bot Token! Please check your BOT_TOKEN: {e}")
    except NetworkError as e:
        logger.error(f"❌ Network Error! Check internet connection: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")

def run_web():
    """Run the Flask web server for healthchecks."""
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🌐 Web server running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    logger.info("🚀 Starting QozenIQ Bot...")
    
    # Run bot in a separate thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Run web server (blocks)
    run_web()
