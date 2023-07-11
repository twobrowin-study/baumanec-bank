from baumanecbank_common import (
    ApplicationBb,
    RecognizeUuidFromQr
)

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

BALANCE_AWAIT_UUID = 0

async def balance_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['uuid_await'],
        reply_markup=app.cancel_keyboard
    )
    return BALANCE_AWAIT_UUID

async def balance_uuid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    uuid = update.message.text
    return await show_balance(uuid, update, context)

async def balance_uuid_invalid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    uuid = update.message.text
    await update.message.reply_markdown(
        app.i18n.app['uuid_invalid'].format(uuid=uuid),
        reply_markup=app.cancel_keyboard
    )
    return BALANCE_AWAIT_UUID

async def balance_uuid_invalid_full_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    uuid = update.message.text
    await update.message.reply_markdown(
        app.i18n.app['uuid_invalid_full'].format(uuid=uuid),
        reply_markup=app.cancel_keyboard
    )
    return BALANCE_AWAIT_UUID

async def balance_qr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(app.i18n.app['qr_preprocess'])

    uuid = await RecognizeUuidFromQr(update.message.photo[-1], update.effective_user.id)
    if uuid is None:
        await update.message.reply_markdown(
            app.i18n.app['qr_error'],
            reply_markup=app.cancel_keyboard
        )
        return BALANCE_AWAIT_UUID

    return await show_balance(uuid, update, context)


async def show_balance(uuid: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    if app.pgcon.check_if_client_exists_by_uuid(uuid):
        client = app.pgcon.get_client_by_uuid(uuid)
        await update.message.reply_markdown(
            app.i18n.app['balance']['client'].format(client=client),
            reply_markup=app.main_keyboard
        )
        return ConversationHandler.END
    
    if app.pgcon.check_if_firm_exists_by_uuid(uuid):
        firm = app.pgcon.get_firm_by_uuid(uuid)
        await update.message.reply_markdown(
            app.i18n.app['balance']['firm'].format(firm=firm),
            reply_markup=app.main_keyboard
        )
        return ConversationHandler.END

    await update.message.reply_markdown(
        app.i18n.app['not_found'].format(uuid=uuid),
        reply_markup=app.main_keyboard
    )
    return ConversationHandler.END