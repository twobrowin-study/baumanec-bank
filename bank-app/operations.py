from baumanecbank_common import (
    ApplicationBb,
    RecognizeUuidFromQr
)

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

OPERATIONS_AWAIT_UUID = 0

async def operations_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['uuid_await'],
        reply_markup=app.cancel_keyboard
    )
    return OPERATIONS_AWAIT_UUID

async def operations_uuid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    uuid = update.message.text
    return await show_operations(uuid, update, context)

async def operations_uuid_invalid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    uuid = update.message.text
    await update.message.reply_markdown(
        app.i18n.app['uuid_invalid'].format(uuid=uuid),
        reply_markup=app.cancel_keyboard
    )
    return OPERATIONS_AWAIT_UUID

async def operations_uuid_invalid_full_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    uuid = update.message.text
    await update.message.reply_markdown(
        app.i18n.app['uuid_invalid_full'].format(uuid=uuid),
        reply_markup=app.cancel_keyboard
    )
    return OPERATIONS_AWAIT_UUID

async def operations_qr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(app.i18n.app['qr_preprocess'])

    uuid = await RecognizeUuidFromQr(update.message.photo[-1], update.effective_user.id)
    if uuid is None:
        await update.message.reply_markdown(
            app.i18n.app['qr_error'],
            reply_markup=app.cancel_keyboard
        )
        return OPERATIONS_AWAIT_UUID

    return await show_operations(uuid, update, context)

async def show_operations(uuid: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    operations = app.pgcon.get_client_frim_operations_by_uuid(uuid)
    if operations is None or len(operations) == 0:
        await update.message.reply_markdown(
            app.i18n.app['operations']['no_operations'].format(uuid=uuid),
            reply_markup=app.main_keyboard
        )
        return ConversationHandler.END
    message = app.i18n.app['operations']['row_separator'].join([
        app.i18n.app['operations'][operation.type][operation.operation].format(
            operation = operation,
            operation_timestamp = operation.timestamp.strftime(
                app.i18n.pure['timestamp']['format']
            ),
            name = operation.counter_firm_name if operation.counter_firm_id is not None else operation.counter_client_name
        )
        for operation in operations
    ])
    messages = app.split_by_max_len(message)
    for message in messages:
        await update.message.reply_markdown(message, reply_markup=app.main_keyboard)
    return ConversationHandler.END