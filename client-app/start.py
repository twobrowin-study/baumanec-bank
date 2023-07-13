from baumanecbank_common import (
    ApplicationBb,
    RecognizeUuidFromQr
)

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import re

START_AWAIT_QR = 0

RE_START_UUID = r"\/start\s+(.+)"

async def start_simple_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(app.i18n.app['start']['simple'])
    return START_AWAIT_QR

async def restart_help_await_qr_uuid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(app.i18n.app['start']['await_qr_uuid'])
    return START_AWAIT_QR

async def uuid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    uuid = update.message.text.lower()
    return await setup_client(uuid, 'got_uuid', update, context)

async def qr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(app.i18n.app['start']['got_qr'])

    uuid = await RecognizeUuidFromQr(update.message.photo[-1], update.effective_user.id)
    if uuid is None:
        await update.message.reply_markdown(app.i18n.app['start']['qr_error'])
        return START_AWAIT_QR

    return await setup_client(uuid, 'read_qr', update, context)

async def start_uuid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    uuid = re.findall(RE_START_UUID, update.message.text)[0]
    return await setup_client(uuid, 'uuid', update, context)

async def restart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    client = app.pgcon.get_client_by_chat_id(update.effective_user.id)
    await update.message.reply_markdown(
        app.i18n.app['start']['restart'].format(client=client),
        reply_markup=app.get_keyboard_by_condition(client.is_master)
    )
    
async def setup_client(uuid: str, reply_message_tag: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application

    if not app.pgcon.check_if_client_exists_by_uuid(uuid):
        await update.message.reply_markdown(
            app.i18n.app['start']['client_not_exist'].format(uuid=uuid)
        )
        return ConversationHandler.END

    client = app.pgcon.get_client_by_uuid(uuid)
    err = app.pgcon.update_client_chat_id_username(
        client.id,
        update.effective_user.id,
        update.effective_user.username
    )
    if err is not None:
        await update.message.reply_markdown(
            app.i18n.app['start']['error'].format(
                uuid = uuid,
                chat_id = update.effective_user.id
            )
        )
        return START_AWAIT_QR

    await update.message.reply_markdown(
        app.i18n.app['start'][reply_message_tag].format(client=client),
        reply_markup=app.get_keyboard_by_condition(client.is_master)
    )
    return ConversationHandler.END