import os, dotenv, sys
from baumanecbank_common import (
    Log, DEBUG,
    START_COMMAND,
    HELP_COMMAND,
    ApplicationBbCreate,
    ApplicationBb,
    MessageFilterBb,
    KeyButtonHitted,
    FunctionButtonHitted
)

from telegram import Update, Message
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
)
from telegram.ext.filters import (
    ChatType,
    Regex,
    TEXT,
    PHOTO,
)

from start import (
    RE_START_UUID,
    START_AWAIT_QR,
    start_simple_handler,
    restart_help_await_qr_uuid_handler,
    uuid_handler,
    qr_handler,
    start_uuid_handler,
    restart_handler
)

from keyboard_functions import (
    BALANCE_FUNCTION,
    OPERATIONS_FUNCTION,
    balance_handler,
    operations_handler
)

from update import update_task

if "DOCKER_RUN" in os.environ:
    Log.info("Running in docker environment")
else:
    dotenv.load_dotenv()
    Log.info("Running in dotenv environment")

if len(sys.argv) > 1 and sys.argv[1] in ['debug', '--debug', '-D']:
    Log.setLevel(DEBUG)
    Log.debug("Starting in debug mode")

class ClientExist(MessageFilterBb):
    def filter(self, message: Message) -> bool:
        return self.app.pgcon.check_if_client_exists_by_chat_id(message.chat_id)

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    client = app.pgcon.get_client_by_chat_id(update.effective_user.id)
    await update.message.reply_markdown(
        app.i18n.app['help'].format(client=client),
        reply_markup=app.reply_keyboard
    )

if __name__ == "__main__":
    Log.info("Starting...")
    app = ApplicationBbCreate(update_task=update_task)
    app.init_keyboard()
    client_exist_smp = ClientExist(app=app)
    client_exist     = ChatType.PRIVATE &  client_exist_smp
    client_not_exist = ChatType.PRIVATE & ~client_exist_smp

    is_start_has_uuid = client_not_exist & Regex(RE_START_UUID)
    start_qr_uuid_conversation = ConversationHandler(
        entry_points = [
            CommandHandler(START_COMMAND, start_uuid_handler,   filters=is_start_has_uuid),
            CommandHandler(START_COMMAND, start_simple_handler, filters=client_not_exist),
            CommandHandler(HELP_COMMAND,  start_simple_handler, filters=client_not_exist)
        ],
        states = {
            START_AWAIT_QR: [
                CommandHandler(START_COMMAND, restart_help_await_qr_uuid_handler),
                CommandHandler(HELP_COMMAND,  restart_help_await_qr_uuid_handler),
                MessageHandler(PHOTO,         qr_handler),
                MessageHandler(TEXT,          uuid_handler),
            ]
        },
        fallbacks = [
        ],
        block = False
    )
    app.add_handler(start_qr_uuid_conversation)

    app.add_handlers([
        CommandHandler(START_COMMAND, restart_handler, filters=client_exist, block=False),
        CommandHandler(HELP_COMMAND,  help_handler,    filters=client_exist, block=False)
    ])

    key_button_hitted     = client_exist      & KeyButtonHitted(app=app)
    balance_key_hitted    = key_button_hitted & FunctionButtonHitted(BALANCE_FUNCTION,    app=app)
    operations_key_hitted = key_button_hitted & FunctionButtonHitted(OPERATIONS_FUNCTION, app=app)

    app.add_handlers([
        MessageHandler(balance_key_hitted,    balance_handler,    block=False),
        MessageHandler(operations_key_hitted, operations_handler, block=False),
    ])

    app.run_polling()
    Log.info("Done. Goodby!")