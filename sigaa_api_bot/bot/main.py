import logging
from typing import Optional

import httpx
from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from sigaa_api_bot.bot.config import Config
from sigaa_api_bot.bot.utils import enable_logging, pretty_print_model
from sigaa_api_bot.handlers.apis import SIGAAClient
from sigaa_api_bot.handlers.commands import CommandsFactory
from sigaa_api_bot.handlers.states import BotContext

# Enable logging
logger = enable_logging()

# Bot configuration
config = Config()
bot_token = config.token
api_base_url = config.api_base_url
api_available_services_list = config.get_available_api_services()
api_endpoints_list = config.get_api_endpoints()
api_available_services_dict = config.available_api_services

# Bot states
# [TECH DEBT]: This should be dynamically generated based on the states defined in the states.py file
SERVICE_STATE = 1
CREDENTIALS_STATE = 2


# Telegram bot functions
async def bot_entry_point(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start command to initiate the bot."""
    bot_context = BotContext()
    context.user_data["bot_context"] = bot_context
    # Start the bot context for current conversation and get the command
    user_message = update.message.text.lower()
    command = CommandsFactory.get_command(command_name=user_message, update=update)
    await command.execute()
    return bot_context.actual_state.state_identifier


async def get_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    bot_context: Optional["BotContext"] = context.user_data.get("bot_context")
    if bot_context:
        await bot_context.handle(update, context)
        return bot_context.actual_state.state_identifier
    else:
        # Handle the case where bot_context is missing (note: shouldn't happen)
        await update.message.reply_text(
            "Ocorreu um erro. Por favor, reinicie a conversa."
        )
        context.user_data.clear()
        return ConversationHandler.END


async def get_credentials(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Now, bot_context needs to exist, otherwise this function shouldn't be called
    bot_context: "BotContext" = context.user_data.get("bot_context")
    handler = await bot_context.handle(update, context)

    if handler and bot_context.actual_state.state_identifier == 2:
        await call_api(update, context)
        context.user_data.clear()
        return ConversationHandler.END
    else:
        return bot_context.actual_state.state_identifier


async def call_api(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Call the API based on the provided service."""

    logger.log(logging.INFO, "Calling the API.")

    async def answer_request(data: dict) -> None:
        await update.message.reply_text(
            text=pretty_print_model(data), parse_mode="Markdown"
        )

    async def answer_error(is_valid_credentials: bool) -> None:
        if is_valid_credentials:
            await update.message.reply_text(
                "Hmmm, a API do SIGAA parece estar com algum erro..."
            )
        else:
            await update.message.reply_text(
                "Credenciais inválidas. Reinicie a conversa com /start."
            )

    selected_service = context.user_data.get("selected_service")
    username = context.user_data.get("username")
    password = context.user_data.get("password")

    auth = (username, password)

    try:
        data = await SIGAAClient().call(selected_service, auth)
        await answer_request(data)

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            logger.log(logging.ERROR, "credentials error: %s", e)
            await answer_error(is_valid_credentials=False)
        else:
            logger.log(logging.ERROR, "API error: %s", e)
            await answer_error(is_valid_credentials=True)


async def security_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fallback function to handle security issues."""
    await update.message.reply_text(
        "Ocorreu um erro, não posso continuar com a conversa. Reinicie a conversa com /start."
    )
    context.user_data.clear()
    context.chat_data.clear()


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(bot_token).build()

    # Define a conversation handler with states SERVICE and CREDENTIALS
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.COMMAND, bot_entry_point)],
        states={
            SERVICE_STATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_service)
            ],
            CREDENTIALS_STATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_credentials)
            ],
        },
        fallbacks=[MessageHandler(None, security_fallback)],
        conversation_timeout=180,
    )

    # Add the conversation handler to the application
    application.add_handler(conv_handler)

    # Run the bot until you send a signal to stop
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
