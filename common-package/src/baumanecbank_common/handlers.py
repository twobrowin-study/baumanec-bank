import traceback
import html
import json

from telegram import Bot, Update, Chat
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from baumanecbank_common.log import Log
from baumanecbank_common.application import ApplicationBb

from psycopg2 import OperationalError

async def ErrorHandlerFun(update: Update|dict, context: ContextTypes.DEFAULT_TYPE) -> None:
    Log.error(msg="Exception while handling an update:", exc_info=context.error)
    app: ApplicationBb = context.application
    bot: Bot = app.bot

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    update_str = update.to_dict() if isinstance(update, Update) else update if isinstance(update, dict) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )
    for group_id in app.pgcon.get_admin_groups():
        await bot.send_message(group_id, message, parse_mode=ParseMode.HTML)

    if context.error.__class__ == OperationalError.__class__:
        exit(127)
    app.pgcon.write_event(message)

async def ChatMemberHandlerFun(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    Log.debug(f"Chat member event \n{update.my_chat_member}\n")
    app: ApplicationBb = context.application
    chat_id = update.effective_chat.id
    if update.effective_chat.type in [Chat.GROUP, Chat.SUPERGROUP, Chat.CHANNEL]:
        message = (
            f"{update.my_chat_member.new_chat_member['status'].title()} event "
            f"in {update.effective_chat.type} with title {update.effective_chat.title}"
        )
        Log.info(f"{message} {chat_id=}")
        app.pgcon.write_event(message, chat_id)
        return
    
    elif update.effective_chat.type == Chat.PRIVATE:
        if update.my_chat_member.new_chat_member['status'] == update.my_chat_member.new_chat_member.BANNED:
            message = 'I was banned by private user'
            Log.info(f"{message} {chat_id=}")
            app.pgcon.write_event(message, chat_id)
            return
        
        elif update.my_chat_member.new_chat_member['status'] == update.my_chat_member.new_chat_member.MEMBER:
            message = 'I was unbanned by private user'
            Log.info(f"{message} {chat_id=}")
            app.pgcon.write_event(message, chat_id)
            return
    Log.info(f"Other chat member event in {update.effective_chat.type} {chat_id=}")