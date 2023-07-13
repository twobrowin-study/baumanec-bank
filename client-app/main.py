import os, dotenv, sys
from baumanecbank_common import (
    Log, DEBUG,
    START_COMMAND,
    HELP_COMMAND,
    RE_AMOUNT,
    RE_UUID,
    RE_INVALID_UUID,
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

from service import (
    SERVICE_AMOUNT_AWAIT,
    SERVICE_UUID_AWAIT,
    SERVICE_CLOSE_AWAIT,
    service_start_handler,
    service_amount_input_handler,
    service_amount_invalid_handler,
    service_change_amount_handler,
    service_uuid_input_handler,
    service_uuid_invalid_handler,
    service_uuid_invalid_full_handler,
    service_qr_input_handler,
    service_close_handler
)

CANCEL_KEYBOARD = 'cancel_keyboard'
CHANGE_KEYBOARD = 'change_keyboard'
CLOSE_KEYBOARD  = 'close_keyboard'

SERVICE_KEY       = 'service'
CANCEL_KEY        = 'cancel'
CLOSE_KEY         = 'close'
CHANGE_AMOUNT_KEY = 'cahnge_amount'

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

class ClientIsMaser(MessageFilterBb):
    def filter(self, message: Message) -> bool:
        return app.pgcon.check_if_client_is_master_by_chat_id(message.chat_id)

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    client = app.pgcon.get_client_by_chat_id(update.effective_user.id)
    await update.message.reply_markdown(
        app.i18n.app['help'].format(client=client),
        reply_markup=app.get_keyboard_by_condition(client.is_master)
    )

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    is_master = app.pgcon.check_if_client_is_master_by_chat_id(update.effective_user.id)
    await update.message.reply_text(
        app.i18n.app['cancel'],
        reply_markup=app.get_keyboard_by_condition(is_master)
    )
    context.user_data.clear()
    return ConversationHandler.END

if __name__ == "__main__":
    Log.info("Starting...")
    app = ApplicationBbCreate(update_task=update_task)
    app.init_keyboard()
    app.init_keyboard(from_config=CANCEL_KEYBOARD, attr_name=CANCEL_KEYBOARD)
    app.init_keyboard(from_config=CHANGE_KEYBOARD, attr_name=CHANGE_KEYBOARD)
    app.init_keyboard(from_config=CLOSE_KEYBOARD,  attr_name=CLOSE_KEYBOARD)
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
    
    service_key_hitted = key_button_hitted & ClientIsMaser(app=app) & FunctionButtonHitted(SERVICE_KEY, app=app)
    button_hitted = lambda key, keyboard: client_exist & \
        KeyButtonHitted(attr_name=keyboard, app=app) & \
        FunctionButtonHitted(key, from_config=keyboard, app=app)

    close_button_hitted         = button_hitted(CLOSE_KEY,         CLOSE_KEYBOARD)
    change_amount_button_hitted = button_hitted(CHANGE_AMOUNT_KEY, CHANGE_KEYBOARD)
    cancel_button_hitted     = \
        button_hitted(CANCEL_KEY, CANCEL_KEYBOARD) | \
        button_hitted(CANCEL_KEY, CHANGE_KEYBOARD) | \
        button_hitted(CANCEL_KEY, CLOSE_KEYBOARD)

    service_conversation = ConversationHandler(
        entry_points = [
            MessageHandler(service_key_hitted, service_start_handler)
        ],
        states = {
            SERVICE_AMOUNT_AWAIT: [
                MessageHandler(client_exist & Regex(RE_AMOUNT),             service_amount_input_handler),
                MessageHandler(client_exist & ~cancel_button_hitted & TEXT, service_amount_invalid_handler)
            ],
            SERVICE_UUID_AWAIT: [
                MessageHandler(change_amount_button_hitted,                 service_change_amount_handler),
                MessageHandler(client_exist & Regex(RE_UUID),               service_uuid_input_handler),
                MessageHandler(client_exist & Regex(RE_INVALID_UUID),       service_uuid_invalid_handler),
                MessageHandler(client_exist & ~cancel_button_hitted & TEXT, service_uuid_invalid_full_handler),
                MessageHandler(client_exist & PHOTO,                        service_qr_input_handler),
            ],
            SERVICE_CLOSE_AWAIT: [
                MessageHandler(close_button_hitted, service_close_handler)
            ]
        },
        fallbacks = [
            MessageHandler(cancel_button_hitted, cancel_handler),
        ],
        block = False
    )
    app.add_handler(service_conversation)

    app.run_polling()
    Log.info("Done. Goodby!")