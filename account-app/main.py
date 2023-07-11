import os, dotenv, sys
from baumanecbank_common import (
    Log, DEBUG,
    START_COMMAND,
    HELP_COMMAND,
    RE_AMOUNT, RE_UUID,
    RE_INVALID_UUID,
    ApplicationBbCreate,
    ApplicationBb,
    MessageFilterBb,
    KeyButtonHitted,
    FunctionButtonHitted
)

from telegram import Message, Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler
)
from telegram.ext.filters import (
    ChatType,
    Regex,
    TEXT,
    PHOTO,
)

from start_help import (
    not_client_start_handler,
    not_client_help_handler,
    not_account_start_handler,
    not_account_help_handler,
    is_account_start_handler,
    is_account_help_handler
)

from keyboard_functions import (
    BALANCE_FUNCTION,
    OPERATIONS_FUNCTION,
    balance_handler,
    operations_handler
)

from salary import (
    SALARY_FUNCTION,
    CALBACK_EMPLOYEE_TEMPLATE,
    SALARY_AWAIT_AMOUNT,
    SALARY_CLOSE_AWAIT,
    salary_start_handler,
    salary_callback_handler,
    salary_amount_input_handler,
    salary_amount_invalid_handler,
    salary_close_handler
)

from service import (
    SERVICE_AMOUNT_AWAIT,
    SERVICE_UUID_AWAIT,
    SERVICE_CLOSE_AWAIT,
    SERVICE_START_FUNCTION,
    SERVICE_CHANGE_AMOUNT_FUNCTION,
    service_start_handler,
    service_amount_input_handler,
    service_amount_invalid_handler,
    service_change_amount_handler,
    service_uuid_input_handler,
    service_uuid_invalid_handler,
    service_uuid_invalid_full_handler,
    service_qr_input_handler,
    service_close_handler,
)

from update import update_task

KEYBOARD_MAIN   = 'keyboard_main'
KEYBOARD_AMOUNT = 'keyboard_amount'
KEYBOARD_UUID   = 'keyboard_uuid'
KEYBOARD_CLOSE  = 'keyboard_close'
CANCEL_FUNCTION = 'cancel'
CLOSE_FUNCTION  = 'close'

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

class AccountExist(MessageFilterBb):
    def filter(self, message: Message) -> bool:
        return self.app.pgcon.check_if_account_exists_by_chat_id(message.chat_id)

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_text(
        app.i18n.app['cancel'],
        reply_markup=app.keyboard_main
    )
    context.user_data.clear()
    return ConversationHandler.END

if __name__ == "__main__":
    Log.info("Starting...")
    app = ApplicationBbCreate(update_task=update_task)
    app.init_keyboard(KEYBOARD_MAIN,   KEYBOARD_MAIN)
    app.init_keyboard(KEYBOARD_AMOUNT, KEYBOARD_AMOUNT)
    app.init_keyboard(KEYBOARD_UUID,   KEYBOARD_UUID)
    app.init_keyboard(KEYBOARD_CLOSE,  KEYBOARD_CLOSE)

    client_exist_smp = ClientExist(app=app)
    client_not_exist = ChatType.PRIVATE & ~client_exist_smp
    
    account_exist_smp = AccountExist(app=app)
    account_exist     = ChatType.PRIVATE &  account_exist_smp
    account_not_exist = ChatType.PRIVATE & ~account_exist_smp

    button_hitted = lambda key, keyboard: account_exist & \
        KeyButtonHitted(attr_name=keyboard, app=app) & \
        FunctionButtonHitted(key, from_config=keyboard, app=app)

    cancel_button_hitted = \
        button_hitted(CANCEL_FUNCTION, KEYBOARD_AMOUNT) | \
        button_hitted(CANCEL_FUNCTION, KEYBOARD_UUID)   | \
        button_hitted(CANCEL_FUNCTION, KEYBOARD_CLOSE)

    app.add_handlers([
        CommandHandler(START_COMMAND, not_client_start_handler,  filters=client_not_exist,  block=False),
        CommandHandler(HELP_COMMAND,  not_client_help_handler,   filters=client_not_exist,  block=False),
        CommandHandler(START_COMMAND, not_account_start_handler, filters=account_not_exist, block=False),
        CommandHandler(HELP_COMMAND,  not_account_help_handler,  filters=account_not_exist, block=False),
        CommandHandler(START_COMMAND, is_account_start_handler,  filters=account_exist,     block=False),
        CommandHandler(HELP_COMMAND,  is_account_help_handler,   filters=account_exist,     block=False),
    ])

    balance_button_hitted    = button_hitted(BALANCE_FUNCTION,    KEYBOARD_MAIN)
    operations_button_hitted = button_hitted(OPERATIONS_FUNCTION, KEYBOARD_MAIN)

    app.add_handlers([
        MessageHandler(balance_button_hitted,    balance_handler,    block=False),
        MessageHandler(operations_button_hitted, operations_handler, block=False),
    ])

    salary_button_hitted = button_hitted(SALARY_FUNCTION, KEYBOARD_MAIN)
    close_button_hitted  = button_hitted(CLOSE_FUNCTION,  KEYBOARD_CLOSE)
    salary_conversation  = ConversationHandler(
        entry_points = [
            CallbackQueryHandler(salary_callback_handler, pattern=CALBACK_EMPLOYEE_TEMPLATE)
        ],
        states = {
            SALARY_AWAIT_AMOUNT: [
                MessageHandler(account_exist & Regex(RE_AMOUNT),             salary_amount_input_handler),
                MessageHandler(account_exist & ~cancel_button_hitted & TEXT, salary_amount_invalid_handler)
            ],
            SALARY_CLOSE_AWAIT: [
                MessageHandler(close_button_hitted, salary_close_handler)
            ]
        },
        fallbacks = [
            MessageHandler(cancel_button_hitted, cancel_handler)
        ],
        block = False,
        per_message = False
    )

    app.add_handlers([
        MessageHandler(salary_button_hitted, salary_start_handler, block=False),
        salary_conversation
    ])

    service_start_button_hitted         = button_hitted(SERVICE_START_FUNCTION, KEYBOARD_MAIN)
    service_change_amount_button_hitted = button_hitted(SERVICE_CHANGE_AMOUNT_FUNCTION, KEYBOARD_UUID)

    service_conversation = ConversationHandler(
        entry_points = [
            MessageHandler(service_start_button_hitted, service_start_handler)
        ],
        states = {
            SERVICE_AMOUNT_AWAIT: [
                MessageHandler(account_exist & Regex(RE_AMOUNT),             service_amount_input_handler),
                MessageHandler(account_exist & ~cancel_button_hitted & TEXT, service_amount_invalid_handler)
            ],
            SERVICE_UUID_AWAIT: [
                MessageHandler(service_change_amount_button_hitted,          service_change_amount_handler),
                MessageHandler(account_exist & Regex(RE_UUID),               service_uuid_input_handler),
                MessageHandler(account_exist & Regex(RE_INVALID_UUID),       service_uuid_invalid_handler),
                MessageHandler(account_exist & ~cancel_button_hitted & TEXT, service_uuid_invalid_full_handler),
                MessageHandler(account_exist & PHOTO,                        service_qr_input_handler),
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