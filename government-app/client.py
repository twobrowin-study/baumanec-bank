from baumanecbank_common import (
    ApplicationBb,
    MessageFilterBb
)

from telegram import Update, Message
from telegram.ext import ContextTypes

import re

CREATE_CLIENT = "create_client"

CC_ONE_SHOT = r"\/create_client\s*(.*)\n(.*)\n(\d+)"

class IsCreateClientOneShot(MessageFilterBb):
    def filter(self, message: Message) -> bool:
        return re.match(CC_ONE_SHOT, message.text) is not None

async def create_client_one_shot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    groups = re.findall(CC_ONE_SHOT, update.message.text)
    card_code, name, squad = groups[0]
    card_code_id = app.pgcon.get_card_code_id_or_none_by_uuid(card_code)
    
    if card_code_id is None:
        await update.message.reply_markdown(
            app.i18n.app['create_client']['unavaliable_card_code'].format(card_code=card_code)
        )
        return

    if not app.pgcon.check_if_squad_valid(squad):
        await update.message.reply_markdown(
            app.i18n.app['create_client']['invalid_squad_num']
        )
        return

    err = app.pgcon.create_client(card_code_id, name, squad)
    if err is not None:
        await update.message.reply_markdown(
            app.i18n.app['create_client']['error']
        )
        raise err

    await update.message.reply_markdown(
        app.i18n.app['create_client']['success'].format(
            card_code = card_code,
            name  = name,
            squad = squad,
        )
    )

