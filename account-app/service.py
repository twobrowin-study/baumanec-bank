from baumanecbank_common import (
    ApplicationBb,
    RecognizeUuidFromQr
)

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

SERVICE_AMOUNT_AWAIT, SERVICE_UUID_AWAIT, SERVICE_CLOSE_AWAIT = range(3)

SERVICE_START_FUNCTION         = 'service'
SERVICE_CHANGE_AMOUNT_FUNCTION = 'cahnge_amount'

async def service_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['service']['start'],
        reply_markup=app.keyboard_amount
    )
    return SERVICE_AMOUNT_AWAIT

async def service_amount_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    amount = float(update.message.text.replace(',', '.'))
    context.user_data["amount"] = amount
    await update.message.reply_markdown(
        app.i18n.app['service']['amount_input'].format(amount=amount),
        reply_markup=app.keyboard_uuid
    )
    return SERVICE_UUID_AWAIT

async def service_amount_invalid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['service']['amount_invalid'],
        reply_markup=app.keyboard_amount
    )
    return SERVICE_AMOUNT_AWAIT

async def service_change_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['service']['amount_change'],
        reply_markup=app.keyboard_amount
    )
    return SERVICE_AMOUNT_AWAIT

async def service_uuid_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    uuid = update.message.text.lower()
    context.user_data["uuid"] = uuid
    amount = context.user_data["amount"]
    await update.message.reply_markdown(
        app.i18n.app['service']['uuid_input'].format(amount=amount, uuid=uuid),
        reply_markup=app.keyboard_close
    )
    return SERVICE_CLOSE_AWAIT

async def service_uuid_invalid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    uuid = update.message.text
    await update.message.reply_markdown(
        app.i18n.app['service']['uuid_invalid'].format(uuid=uuid),
        reply_markup=app.keyboard_uuid
    )
    return SERVICE_UUID_AWAIT

async def service_uuid_invalid_full_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    uuid = update.message.text
    await update.message.reply_markdown(
        app.i18n.app['service']['uuid_invalid_full'].format(uuid=uuid),
        reply_markup=app.keyboard_uuid
    )
    return SERVICE_UUID_AWAIT

async def service_qr_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(app.i18n.app['service']['qr_preprocess'])

    uuid = await RecognizeUuidFromQr(update.message.photo[-1], update.effective_user.id)
    if uuid is None:
        await update.message.reply_markdown(
            app.i18n.app['service']['qr_error'],
            reply_markup=app.keyboard_uuid
        )
        return SERVICE_UUID_AWAIT
    
    context.user_data["uuid"] = uuid
    amount = context.user_data["amount"]
    await update.message.reply_markdown(
        app.i18n.app['service']['uuid_input'].format(amount=amount, uuid=uuid),
        reply_markup=app.keyboard_close
    )
    return SERVICE_CLOSE_AWAIT

async def service_close_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    amount      = context.user_data["amount"]
    uuid        = context.user_data["uuid"]
    account     = app.pgcon.get_account_by_chat_id(update.message.chat_id)
    client_firm = app.pgcon.get_client_firm_by_uuid(uuid)

    if client_firm is None:
        await update.message.reply_markdown(
            app.i18n.app['service']['recipient_not_found'].format(uuid=uuid),
            reply_markup=app.keyboard_uuid
        )
        return SERVICE_UUID_AWAIT

    if not client_firm.is_government and client_firm.balance < amount:
        await update.message.reply_markdown(
            app.i18n.app['service']['balance_not_enough'],
            reply_markup=app.keyboard_main
        )
        return ConversationHandler.END

    err = app.pgcon.create_service(client_firm.card_code_id, account.firm_card_code_id, amount)
    if err is not None:
        await update.message.reply_markdown(
            app.i18n.app['service']['error'],
            reply_markup=app.keyboard_main
        )
        return ConversationHandler.END

    await update.message.reply_markdown(
        app.i18n.app['service']['success'],
        reply_markup=app.keyboard_main
    )
    return ConversationHandler.END