from baumanecbank_common import ApplicationBb

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes

async def not_client_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['not_client']['start'],
        reply_markup=ReplyKeyboardRemove()
    )

async def not_client_help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['not_client']['help'],
        reply_markup=ReplyKeyboardRemove()
    )

async def not_account_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['not_account']['start'],
        reply_markup=ReplyKeyboardRemove()
    )

async def not_account_help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['not_account']['help'],
        reply_markup=ReplyKeyboardRemove()
    )

async def is_account_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    account = app.pgcon.get_account_by_chat_id(update.effective_user.id)
    await update.message.reply_markdown(
        app.i18n.app['is_account']['start'].format(account=account),
        reply_markup=app.keyboard_main
    )

async def is_account_help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    account = app.pgcon.get_account_by_chat_id(update.effective_user.id)
    await update.message.reply_markdown(
        app.i18n.app['is_account']['help'].format(account=account),
        reply_markup=app.keyboard_main
    )