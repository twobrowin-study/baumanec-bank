from baumanecbank_common import (
    ApplicationBb,
    RecognizeUuidFromQr
)

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

SERVICE_AMOUNT_AWAIT, SERVICE_UUID_AWAIT, SERVICE_CLOSE_AWAIT = range(3)

async def service_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['service']['start'],
        reply_markup=app.cancel_keyboard
    )
    return SERVICE_AMOUNT_AWAIT

async def service_amount_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    amount = float(update.message.text.replace(',', '.'))
    context.user_data["amount"] = amount
    await update.message.reply_markdown(
        app.i18n.app['service']['amount_input'].format(amount=amount),
        reply_markup=app.change_keyboard
    )
    return SERVICE_UUID_AWAIT

async def service_amount_invalid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['service']['amount_invalid'],
        reply_markup=app.cancel_keyboard
    )
    return SERVICE_AMOUNT_AWAIT

async def service_change_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['service']['amount_change'],
        reply_markup=app.cancel_keyboard
    )
    return SERVICE_AMOUNT_AWAIT

async def service_uuid_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    uuid = update.message.text.lower()
    context.user_data["uuid"] = uuid
    amount = context.user_data["amount"]
    await update.message.reply_markdown(
        app.i18n.app['service']['uuid_input'].format(amount=amount, uuid=uuid),
        reply_markup=app.close_keyboard
    )
    return SERVICE_CLOSE_AWAIT

async def service_uuid_invalid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    uuid = update.message.text
    await update.message.reply_markdown(
        app.i18n.app['service']['uuid_invalid'].format(uuid=uuid),
        reply_markup=app.change_keyboard
    )
    return SERVICE_UUID_AWAIT

async def service_uuid_invalid_full_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    uuid = update.message.text
    await update.message.reply_markdown(
        app.i18n.app['service']['uuid_invalid_full'].format(uuid=uuid),
        reply_markup=app.change_keyboard
    )
    return SERVICE_UUID_AWAIT

async def service_qr_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(app.i18n.app['service']['qr_preprocess'])

    uuid = await RecognizeUuidFromQr(update.message.photo[-1], update.effective_user.id)
    if uuid is None:
        await update.message.reply_markdown(
            app.i18n.app['service']['qr_error'],
            reply_markup=app.change_keyboard
        )
        return SERVICE_UUID_AWAIT
    
    context.user_data["uuid"] = uuid
    amount = context.user_data["amount"]
    await update.message.reply_markdown(
        app.i18n.app['service']['uuid_input'].format(amount=amount, uuid=uuid),
        reply_markup=app.close_keyboard
    )
    return SERVICE_CLOSE_AWAIT

async def service_close_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    amount = context.user_data["amount"]
    uuid   = context.user_data["uuid"]
    firm   = app.pgcon.get_firm_by_uuid(uuid)
    client = app.pgcon.get_client_by_chat_id(update.effective_user.id)

    if firm is None:
        await update.message.reply_markdown(
            app.i18n.app['service']['recipient_not_found'].format(uuid=uuid),
            reply_markup=app.change_keyboard
        )
        return SERVICE_UUID_AWAIT

    if client.balance < amount:
        await update.message.reply_markdown(
            app.i18n.app['service']['balance_not_enough'],
            reply_markup=app.get_keyboard_by_condition(client.is_master)
        )
        return ConversationHandler.END

    err = app.pgcon.create_service(client.card_code_id, firm.card_code_id, amount)
    if err is not None:
        await update.message.reply_markdown(
            app.i18n.app['service']['error'],
            reply_markup=app.get_keyboard_by_condition(client.is_master)
        )
        return ConversationHandler.END

    await update.message.reply_markdown(
        app.i18n.app['service']['success'],
        reply_markup=app.get_keyboard_by_condition(client.is_master)
    )
    return ConversationHandler.END