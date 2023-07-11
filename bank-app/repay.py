from baumanecbank_common import (
    ApplicationBb,
    RecognizeUuidFromQr
)

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

REPAY_AMOUNT_AWAIT, REPAY_UUID_AWAIT, REPAY_CLOSE_AWAIT = range(3)

async def repay_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['repay']['start'],
        reply_markup=app.cancel_keyboard
    )
    return REPAY_AMOUNT_AWAIT

async def repay_amount_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    amount = float(update.message.text.replace(',', '.'))
    context.user_data["amount"] = amount
    await update.message.reply_markdown(
        app.i18n.app['amount_input'].format(amount=amount),
        reply_markup=app.change_keyboard
    )
    return REPAY_UUID_AWAIT

async def repay_amount_invalid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['amount_invalid'],
        reply_markup=app.cancel_keyboard
    )
    return REPAY_AMOUNT_AWAIT

async def repay_change_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['amount_change'],
        reply_markup=app.cancel_keyboard
    )
    return REPAY_AMOUNT_AWAIT

async def repay_uuid_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    uuid = update.message.text.lower()
    context.user_data["uuid"] = uuid
    amount = context.user_data["amount"]
    await update.message.reply_markdown(
        app.i18n.app['repay']['confirmation'].format(amount=amount, uuid=uuid, govtax=amount*0.2),
        reply_markup=app.close_keyboard
    )
    return REPAY_CLOSE_AWAIT

async def repay_uuid_invalid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    uuid = update.message.text
    await update.message.reply_markdown(
        app.i18n.app['uuid_invalid'].format(uuid=uuid),
        reply_markup=app.change_keyboard
    )
    return REPAY_UUID_AWAIT

async def repay_uuid_invalid_full_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    uuid = update.message.text
    await update.message.reply_markdown(
        app.i18n.app['uuid_invalid_full'].format(uuid=uuid),
        reply_markup=app.change_keyboard
    )
    return REPAY_UUID_AWAIT

async def repay_qr_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(app.i18n.app['qr_preprocess'])

    uuid = await RecognizeUuidFromQr(update.message.photo[-1], update.effective_user.id)
    if uuid is None:
        await update.message.reply_markdown(
            app.i18n.app['qr_error'],
            reply_markup=app.change_keyboard
        )
        return REPAY_UUID_AWAIT
    
    context.user_data["uuid"] = uuid
    amount = context.user_data["amount"]
    await update.message.reply_markdown(
        app.i18n.app['repay']['confirmation'].format(amount=amount, uuid=uuid, govtax=amount*0.2),
        reply_markup=app.close_keyboard
    )
    return REPAY_CLOSE_AWAIT

async def repay_close_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    amount      = context.user_data["amount"]
    uuid        = context.user_data["uuid"]
    client_firm = app.pgcon.get_client_firm_by_uuid(uuid)

    if client_firm is None:
        await update.message.reply_markdown(
            app.i18n.app['counter_not_found'].format(uuid=uuid),
            reply_markup=app.change_keyboard
        )
        return REPAY_UUID_AWAIT

    err = app.pgcon.create_repay_transaction(client_firm.card_code_id, amount)
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