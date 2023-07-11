from baumanecbank_common import (
    ApplicationBb,
    RecognizeUuidFromQr
)

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

AMOUNT_AWAIT, UUID_AWAIT, CLOSE_AWAIT = range(3)

async def transaction_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['start'],
        reply_markup=app.amount_keyboard
    )
    return AMOUNT_AWAIT

async def transaction_cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    context.user_data.clear()
    await update.message.reply_markdown(
        app.i18n.app['cancel'],
        reply_markup=app.start_keyboard
    )
    return ConversationHandler.END

async def amount_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    amount = float(update.message.text.replace(',', '.'))
    context.user_data["amount"] = amount
    await update.message.reply_markdown(
        app.i18n.app['amount_input'].format(amount=amount),
        reply_markup=app.uuid_keyboard
    )
    return UUID_AWAIT

async def amount_invalid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['amount_invalid'],
        reply_markup=app.amount_keyboard
    )
    return AMOUNT_AWAIT

async def change_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['amount_change'],
        reply_markup=app.amount_keyboard
    )
    return AMOUNT_AWAIT

async def uuid_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    uuid = update.message.text.lower()
    context.user_data["uuid"] = uuid
    amount = context.user_data["amount"]
    await update.message.reply_markdown(
        app.i18n.app['uuid_input'].format(amount=amount, uuid=uuid),
        reply_markup=app.close_keyboard
    )
    return CLOSE_AWAIT

async def uuid_invalid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    uuid = update.message.text
    await update.message.reply_markdown(
        app.i18n.app['uuid_invalid'].format(uuid=uuid),
        reply_markup=app.uuid_keyboard
    )
    return UUID_AWAIT

async def uuid_invalid_full_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    uuid = update.message.text
    await update.message.reply_markdown(
        app.i18n.app['uuid_invalid_full'].format(uuid=uuid),
        reply_markup=app.uuid_keyboard
    )
    return UUID_AWAIT

async def qr_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(app.i18n.app['qr_preprocess'])

    uuid = await RecognizeUuidFromQr(update.message.photo[-1], update.effective_user.id)
    if uuid is None:
        await update.message.reply_markdown(
            app.i18n.app['qr_error'],
            reply_markup=app.uuid_keyboard
        )
        return UUID_AWAIT
    
    context.user_data["uuid"] = uuid
    amount = context.user_data["amount"]
    await update.message.reply_markdown(
        app.i18n.app['uuid_input'].format(amount=amount, uuid=uuid),
        reply_markup=app.close_keyboard
    )
    return CLOSE_AWAIT

async def transaction_close_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    amount = context.user_data["amount"]
    uuid   = context.user_data["uuid"]
    client_firm = app.pgcon.get_client_firm_by_uuid(uuid)

    if client_firm is None:
        await update.message.reply_markdown(
            app.i18n.app['recipient_not_found'].format(uuid=uuid),
            reply_markup=app.uuid_keyboard
        )
        return UUID_AWAIT

    err = app.pgcon.create_manual_transaction(client_firm.card_code_id, amount)
    if err is not None:
        await update.message.reply_markdown(
            app.i18n.app['error'],
            reply_markup=app.start_keyboard
        )
        return ConversationHandler.END

    await update.message.reply_markdown(
        app.i18n.app['success'],
        reply_markup=app.start_keyboard
    )
    return ConversationHandler.END