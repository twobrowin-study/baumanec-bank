import os, dotenv, sys
from baumanecbank_common import (
    Log, DEBUG,
    HELP_COMMAND,
    ApplicationBbCreate,
    ApplicationBb,
    MessageFilterBb,
    KeyButtonHitted,
    FunctionButtonHitted,
    RE_AMOUNT, RE_UUID,
    RE_INVALID_UUID
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
    PHOTO
)

from balance import (
    BALANCE_AWAIT_UUID,
    balance_start_handler,
    balance_uuid_handler,
    balance_uuid_invalid_handler,
    balance_uuid_invalid_full_handler,
    balance_qr_handler,
)

from operations import (
    OPERATIONS_AWAIT_UUID,
    operations_start_handler,
    operations_uuid_handler,
    operations_uuid_invalid_handler,
    operations_uuid_invalid_full_handler,
    operations_qr_handler,
)

from deposit import (
    DEPOSIT_AMOUNT_AWAIT,
    DEPOSIT_UUID_AWAIT,
    DEPOSIT_CLOSE_AWAIT,
    deposit_start_handler,
    deposit_amount_input_handler,
    deposit_amount_invalid_handler,
    deposit_change_amount_handler,
    deposit_uuid_input_handler,
    deposit_uuid_invalid_handler,
    deposit_uuid_invalid_full_handler,
    deposit_qr_input_handler,
    deposit_close_handler,
)

from withdraw import (
    WITHDRAW_AMOUNT_AWAIT,
    WITHDRAW_UUID_AWAIT,
    WITHDRAW_CLOSE_AWAIT,
    withdraw_start_handler,
    withdraw_amount_input_handler,
    withdraw_amount_invalid_handler,
    withdraw_change_amount_handler,
    withdraw_uuid_input_handler,
    withdraw_uuid_invalid_handler,
    withdraw_uuid_invalid_full_handler,
    withdraw_qr_input_handler,
    withdraw_close_handler,
)

from loan import (
    LOAN_AMOUNT_AWAIT,
    LOAN_UUID_AWAIT,
    LOAN_CLOSE_AWAIT,
    loan_start_handler,
    loan_amount_input_handler,
    loan_amount_invalid_handler,
    loan_change_amount_handler,
    loan_uuid_input_handler,
    loan_uuid_invalid_handler,
    loan_uuid_invalid_full_handler,
    loan_qr_input_handler,
    loan_close_handler,
)

from repay import (
    REPAY_AMOUNT_AWAIT,
    REPAY_UUID_AWAIT,
    REPAY_CLOSE_AWAIT,
    repay_start_handler,
    repay_amount_input_handler,
    repay_amount_invalid_handler,
    repay_change_amount_handler,
    repay_uuid_input_handler,
    repay_uuid_invalid_handler,
    repay_uuid_invalid_full_handler,
    repay_qr_input_handler,
    repay_close_handler,
)

MAIN_KEYBOARD   = 'main_keyboard'
CANCEL_KEYBOARD = 'cancel_keyboard'
CHANGE_KEYBOARD = 'change_keyboard'
CLOSE_KEYBOARD  = 'close_keyboard'

BALANCE_KEY       = 'balance'
OPERARIONS_KEY    = 'operations'
DEPOSIT_KEY       = 'deposit'
WITHDRAW_KEY      = 'withdraw'
LOAN_KEY          = 'loan'
REPAY_KEY         = 'repay'

CANCEL_KEY        = 'cancel'
CLOSE_KEY         = 'close'
CHANGE_AMOUNT_KEY = 'cahnge_amount'

if "DOCKER_RUN" in os.environ:
    Log.info("Running in docker environment")
else:
    dotenv.load_dotenv()
    Log.info("Running in dotenv environment")

if len(sys.argv) > 1 and sys.argv[1] in ['debug', '--debug', '-D']:
    Log.setLevel(DEBUG)
    Log.debug("Starting in debug mode")

class IsBankGroup(MessageFilterBb):
    def filter(self, message: Message) -> bool:
        return self.app.pgcon.check_if_bank_group(message.chat_id)

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['help'],
        reply_markup=app.main_keyboard
    )

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_text(
        app.i18n.app['cancel'],
        reply_markup=app.main_keyboard
    )
    context.user_data.clear()
    return ConversationHandler.END

if __name__ == "__main__":
    Log.info("Starting...")
    app = ApplicationBbCreate()
    app.init_keyboard(from_config=MAIN_KEYBOARD,   attr_name=MAIN_KEYBOARD)
    app.init_keyboard(from_config=CANCEL_KEYBOARD, attr_name=CANCEL_KEYBOARD)
    app.init_keyboard(from_config=CHANGE_KEYBOARD, attr_name=CHANGE_KEYBOARD)
    app.init_keyboard(from_config=CLOSE_KEYBOARD,  attr_name=CLOSE_KEYBOARD)
    is_bank_group = ChatType.GROUPS & IsBankGroup(app=app)
    button_hitted = lambda key, keyboard: is_bank_group & \
        KeyButtonHitted(attr_name=keyboard, app=app) & \
        FunctionButtonHitted(key, from_config=keyboard, app=app)

    app.add_handler(CommandHandler(HELP_COMMAND, help_handler, filters=is_bank_group, block=False))

    balance_button_hitted    = button_hitted(BALANCE_KEY,    MAIN_KEYBOARD)
    operations_button_hitted = button_hitted(OPERARIONS_KEY, MAIN_KEYBOARD)
    deposit_button_hitted    = button_hitted(DEPOSIT_KEY,    MAIN_KEYBOARD)
    withdraw_button_hitted   = button_hitted(WITHDRAW_KEY,   MAIN_KEYBOARD)
    loan_button_hitted       = button_hitted(LOAN_KEY,       MAIN_KEYBOARD)
    repay_button_hitted      = button_hitted(REPAY_KEY,      MAIN_KEYBOARD)

    close_button_hitted         = button_hitted(CLOSE_KEY,         CLOSE_KEYBOARD)
    change_amount_button_hitted = button_hitted(CHANGE_AMOUNT_KEY, CHANGE_KEYBOARD
                                             )
    cancel_button_hitted     = \
        button_hitted(CANCEL_KEY, CANCEL_KEYBOARD) | \
        button_hitted(CANCEL_KEY, CHANGE_KEYBOARD) | \
        button_hitted(CANCEL_KEY, CLOSE_KEYBOARD)

    balance_conversation = ConversationHandler(
        entry_points = [
            MessageHandler(balance_button_hitted, balance_start_handler)
        ],
        states = {
            BALANCE_AWAIT_UUID: [
                MessageHandler(is_bank_group & Regex(RE_UUID),               balance_uuid_handler),
                MessageHandler(is_bank_group & Regex(RE_INVALID_UUID),       balance_uuid_invalid_handler),
                MessageHandler(is_bank_group & ~cancel_button_hitted & TEXT, balance_uuid_invalid_full_handler),
                MessageHandler(is_bank_group & PHOTO,                        balance_qr_handler),
            ]
        },
        fallbacks = [
            MessageHandler(cancel_button_hitted, cancel_handler)
        ],
        block = False
    )
    app.add_handler(balance_conversation)

    operations_conversation = ConversationHandler(
        entry_points = [
            MessageHandler(operations_button_hitted, operations_start_handler)
        ],
        states = {
            OPERATIONS_AWAIT_UUID: [
                MessageHandler(is_bank_group & Regex(RE_UUID),               operations_uuid_handler),
                MessageHandler(is_bank_group & Regex(RE_INVALID_UUID),       operations_uuid_invalid_handler),
                MessageHandler(is_bank_group & ~cancel_button_hitted & TEXT, operations_uuid_invalid_full_handler),
                MessageHandler(is_bank_group & PHOTO,                        operations_qr_handler),
            ]
        },
        fallbacks = [
            MessageHandler(cancel_button_hitted, cancel_handler)
        ],
        block = False
    )
    app.add_handler(operations_conversation)

    deposit_conversation = ConversationHandler(
        entry_points = [
            MessageHandler(deposit_button_hitted, deposit_start_handler)
        ],
        states = {
            DEPOSIT_AMOUNT_AWAIT: [
                MessageHandler(is_bank_group & Regex(RE_AMOUNT),             deposit_amount_input_handler),
                MessageHandler(is_bank_group & ~cancel_button_hitted & TEXT, deposit_amount_invalid_handler)
            ],
            DEPOSIT_UUID_AWAIT: [
                MessageHandler(change_amount_button_hitted,                  deposit_change_amount_handler),
                MessageHandler(is_bank_group & Regex(RE_UUID),               deposit_uuid_input_handler),
                MessageHandler(is_bank_group & Regex(RE_INVALID_UUID),       deposit_uuid_invalid_handler),
                MessageHandler(is_bank_group & ~cancel_button_hitted & TEXT, deposit_uuid_invalid_full_handler),
                MessageHandler(is_bank_group & PHOTO,                        deposit_qr_input_handler),
            ],
            DEPOSIT_CLOSE_AWAIT: [
                MessageHandler(close_button_hitted, deposit_close_handler)
            ]
        },
        fallbacks = [
            MessageHandler(cancel_button_hitted, cancel_handler),
        ],
        block = False
    )
    app.add_handler(deposit_conversation)

    withdraw_conversation = ConversationHandler(
        entry_points = [
            MessageHandler(withdraw_button_hitted, withdraw_start_handler)
        ],
        states = {
            WITHDRAW_AMOUNT_AWAIT: [
                MessageHandler(is_bank_group & Regex(RE_AMOUNT),             withdraw_amount_input_handler),
                MessageHandler(is_bank_group & ~cancel_button_hitted & TEXT, withdraw_amount_invalid_handler)
            ],
            WITHDRAW_UUID_AWAIT: [
                MessageHandler(change_amount_button_hitted,                  withdraw_change_amount_handler),
                MessageHandler(is_bank_group & Regex(RE_UUID),               withdraw_uuid_input_handler),
                MessageHandler(is_bank_group & Regex(RE_INVALID_UUID),       withdraw_uuid_invalid_handler),
                MessageHandler(is_bank_group & ~cancel_button_hitted & TEXT, withdraw_uuid_invalid_full_handler),
                MessageHandler(is_bank_group & PHOTO,                        withdraw_qr_input_handler),
            ],
            WITHDRAW_CLOSE_AWAIT: [
                MessageHandler(close_button_hitted, withdraw_close_handler)
            ]
        },
        fallbacks = [
            MessageHandler(cancel_button_hitted, cancel_handler),
        ],
        block = False
    )
    app.add_handler(withdraw_conversation)

    loan_conversation = ConversationHandler(
        entry_points = [
            MessageHandler(loan_button_hitted, loan_start_handler)
        ],
        states = {
            LOAN_AMOUNT_AWAIT: [
                MessageHandler(is_bank_group & Regex(RE_AMOUNT),             loan_amount_input_handler),
                MessageHandler(is_bank_group & ~cancel_button_hitted & TEXT, loan_amount_invalid_handler)
            ],
            LOAN_UUID_AWAIT: [
                MessageHandler(change_amount_button_hitted,                  loan_change_amount_handler),
                MessageHandler(is_bank_group & Regex(RE_UUID),               loan_uuid_input_handler),
                MessageHandler(is_bank_group & Regex(RE_INVALID_UUID),       loan_uuid_invalid_handler),
                MessageHandler(is_bank_group & ~cancel_button_hitted & TEXT, loan_uuid_invalid_full_handler),
                MessageHandler(is_bank_group & PHOTO,                        loan_qr_input_handler),
            ],
            LOAN_CLOSE_AWAIT: [
                MessageHandler(close_button_hitted, loan_close_handler)
            ]
        },
        fallbacks = [
            MessageHandler(cancel_button_hitted, cancel_handler),
        ],
        block = False
    )
    app.add_handler(loan_conversation)

    repay_conversation = ConversationHandler(
        entry_points = [
            MessageHandler(repay_button_hitted, repay_start_handler)
        ],
        states = {
            REPAY_AMOUNT_AWAIT: [
                MessageHandler(is_bank_group & Regex(RE_AMOUNT),             repay_amount_input_handler),
                MessageHandler(is_bank_group & ~cancel_button_hitted & TEXT, repay_amount_invalid_handler)
            ],
            REPAY_UUID_AWAIT: [
                MessageHandler(change_amount_button_hitted,                  repay_change_amount_handler),
                MessageHandler(is_bank_group & Regex(RE_UUID),               repay_uuid_input_handler),
                MessageHandler(is_bank_group & Regex(RE_INVALID_UUID),       repay_uuid_invalid_handler),
                MessageHandler(is_bank_group & ~cancel_button_hitted & TEXT, repay_uuid_invalid_full_handler),
                MessageHandler(is_bank_group & PHOTO,                        repay_qr_input_handler),
            ],
            REPAY_CLOSE_AWAIT: [
                MessageHandler(close_button_hitted, repay_close_handler)
            ]
        },
        fallbacks = [
            MessageHandler(cancel_button_hitted, cancel_handler),
        ],
        block = False
    )
    app.add_handler(repay_conversation)

    app.run_polling()
    Log.info("Done. Goodby!")