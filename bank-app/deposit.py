from baumanecbank_common import (
    ApplicationBb,
    RecognizeUuidFromQr
)

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

DEPOSIT_AMOUNT_AWAIT, DEPOSIT_UUID_AWAIT, DEPOSIT_CLOSE_AWAIT = range(3)

async def deposit_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['deposit']['start'],
        reply_markup=app.cancel_keyboard
    )
    return DEPOSIT_AMOUNT_AWAIT

async def deposit_amount_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    amount = float(update.message.text.replace(',', '.'))
    context.user_data["amount"] = amount
    await update.message.reply_markdown(
        app.i18n.app['amount_input'].format(amount=amount),
        reply_markup=app.change_keyboard
    )
    return DEPOSIT_UUID_AWAIT

async def deposit_amount_invalid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['amount_invalid'],
        reply_markup=app.cancel_keyboard
    )
    return DEPOSIT_AMOUNT_AWAIT

async def deposit_change_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['amount_change'],
        reply_markup=app.cancel_keyboard
    )
    return DEPOSIT_AMOUNT_AWAIT

async def deposit_uuid_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    uuid = update.message.text.lower()
    context.user_data["uuid"] = uuid
    amount = context.user_data["amount"]
    await update.message.reply_markdown(
        app.i18n.app['deposit']['confirmation'].format(amount=amount, uuid=uuid),
        reply_markup=app.close_keyboard
    )
    return DEPOSIT_CLOSE_AWAIT

async def deposit_uuid_invalid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    uuid = update.message.text
    await update.message.reply_markdown(
        app.i18n.app['uuid_invalid'].format(uuid=uuid),
        reply_markup=app.change_keyboard
    )
    return DEPOSIT_UUID_AWAIT

async def deposit_uuid_invalid_full_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    uuid = update.message.text
    await update.message.reply_markdown(
        app.i18n.app['uuid_invalid_full'].format(uuid=uuid),
        reply_markup=app.change_keyboard
    )
    return DEPOSIT_UUID_AWAIT

async def deposit_qr_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(app.i18n.app['qr_preprocess'])

    uuid = await RecognizeUuidFromQr(update.message.photo[-1], update.effective_user.id)
    if uuid is None:
        await update.message.reply_markdown(
            app.i18n.app['qr_error'],
            reply_markup=app.change_keyboard
        )
        return DEPOSIT_UUID_AWAIT
    
    context.user_data["uuid"] = uuid
    amount = context.user_data["amount"]
    await update.message.reply_markdown(
        app.i18n.app['deposit']['confirmation'].format(amount=amount, uuid=uuid),
        reply_markup=app.close_keyboard
    )
    return DEPOSIT_CLOSE_AWAIT

async def deposit_close_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    amount      = context.user_data["amount"]
    uuid        = context.user_data["uuid"]
    client_firm = app.pgcon.get_client_firm_by_uuid(uuid)

    if client_firm is None:
        await update.message.reply_markdown(
            app.i18n.app['counter_not_found'].format(uuid=uuid),
            reply_markup=app.change_keyboard
        )
        return DEPOSIT_UUID_AWAIT

    if not client_firm.is_government and client_firm.balance < amount:
        await update.message.reply_markdown(
            app.i18n.app['balance_not_enough'],
            reply_markup=app.main_keyboard
        )
        return ConversationHandler.END

    err = app.pgcon.create_deposit_transaction(client_firm.card_code_id, amount)
    if err is not None:
        await update.message.reply_markdown(
            app.i18n.app['error'],
            reply_markup=app.main_keyboard
        )
        return ConversationHandler.END

    await update.message.reply_markdown(
        app.i18n.app['success'],
        reply_markup=app.main_keyboard
    )
    return ConversationHandler.END