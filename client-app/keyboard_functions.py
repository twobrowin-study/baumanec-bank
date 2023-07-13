from baumanecbank_common import Log, ApplicationBb, MessageFilterBb

from telegram import Update, Message
from telegram.ext import ContextTypes

BALANCE_FUNCTION    = 'balance'
OPERATIONS_FUNCTION = 'operations'

async def balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    client = app.pgcon.get_client_by_chat_id(update.effective_user.id)
    await update.message.reply_markdown(
        app.i18n.app['balance'].format(client=client),
        reply_markup=app.get_keyboard_by_condition(client.is_master)
    )

async def operations_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    operations = app.pgcon.get_client_operations_by_chat_id(update.effective_chat.id)
    if len(operations) == 0:
        await update.message.reply_markdown(app.i18n.app['operations']['no_operations'])
        return
    message = app.i18n.app['operations']['row_separator'].join([
        app.i18n.app['operations'][operation.type].format(
            operation = operation,
            operation_timestamp = operation.timestamp.strftime(
                app.i18n.pure['timestamp']['format']
            ),
        )
        for operation in operations
    ])
    messages  = app.split_by_max_len(message)
    is_master = app.pgcon.check_if_client_is_master_by_chat_id(update.effective_user.id)
    for message in messages:
        await update.message.reply_markdown(message, reply_markup=app.get_keyboard_by_condition(is_master))