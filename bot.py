import os
import logging
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Flask app
app = Flask(__name__)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    logger.error("❌ BOT_TOKEN not set!")
    exit(1)

logger.info(f"✅ Bot token found: {TOKEN[:10]}...")

# About text (116 characters)
ABOUT_TEXT = """🤖 QozenIQ - Your smart AI assistant for quick answers, info, and insights. Fast, private, and helpful! ✨"""

# Create application
application = Application.builder().token(TOKEN).build()

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    await update.message.reply_text(
        "🏓 *Pong!*\n\nBot is online and ready! ✅",
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    user_message = update.message.text
    
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

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("about", about_command))
application.add_handler(CommandHandler("ping", ping_command))
application.add_handler(CallbackQueryHandler(button_callback))

from telegram.ext import MessageHandler, filters
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Flask routes
@app.route('/')
def healthcheck():
    return jsonify({"status": "healthy", "message": "QozenIQ Bot is running!"}), 200

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming updates via webhook."""
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.process_update(update)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Set the webhook URL (for debugging)."""
    railway_url = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
    if not railway_url:
        return jsonify({"error": "RAILWAY_PUBLIC_DOMAIN not set"}), 400
    
    webhook_url = f"https://{railway_url}/webhook"
    try:
        application.bot.set_webhook(webhook_url)
        return jsonify({
            "status": "success", 
            "webhook_url": webhook_url,
            "message": "Webhook set successfully!"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/remove_webhook', methods=['GET'])
def remove_webhook():
    """Remove webhook (for debugging)."""
    try:
        application.bot.delete_webhook()
        return jsonify({"status": "success", "message": "Webhook removed!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    
    # Initialize bot before starting
    logger.info("🚀 Starting QozenIQ Bot with webhook...")
    
    # For local testing, use polling
    if os.environ.get('ENV') == 'local':
        logger.info("🤖 Running in polling mode (local)...")
        application.run_polling()
    else:
        # In production, set webhook
        railway_url = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
        if railway_url:
            webhook_url = f"https://{railway_url}/webhook"
            try:
                application.bot.set_webhook(webhook_url)
                logger.info(f"✅ Webhook set to: {webhook_url}")
            except Exception as e:
                logger.error(f"❌ Failed to set webhook: {e}")
        else:
            logger.warning("⚠️ RAILWAY_PUBLIC_DOMAIN not set, webhook won't work")
        
        # Run Flask
        logger.info(f"🌐 Web server running on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
