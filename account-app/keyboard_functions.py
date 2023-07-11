from baumanecbank_common import Log, ApplicationBb

from telegram import Update
from telegram.ext import ContextTypes

BALANCE_FUNCTION    = 'balance'
OPERATIONS_FUNCTION = 'operations'

async def balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    account = app.pgcon.get_account_by_chat_id(update.effective_user.id)
    await update.message.reply_markdown(
        app.i18n.app['balance'].format(account=account),
        reply_markup=app.keyboard_main
    )

async def operations_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    operations = app.pgcon.get_frim_operations_by_account_chat_id(update.effective_chat.id)
    if len(operations) == 0:
        await update.message.reply_markdown(app.i18n.app['operations']['no_operations'])
        return
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
        await update.message.reply_markdown(message, reply_markup=app.keyboard_main)