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

from purchase import (
    AMOUNT_AWAIT,
    UUID_AWAIT,
    CLOSE_AWAIT,
    
    purchase_start_handler,
    purcahse_cancel_handler,
    amount_input_handler,
    amount_invalid_handler,
    change_amount_handler,
    uuid_input_handler,
    uuid_invalid_handler,
    uuid_invalid_full_handler,
    qr_input_handler,
    purchase_close_handler
)

START_KEYBOARD  = 'start_keyboard'
AMOUNT_KEYBOARD = 'amount_keyboard'
UUID_KEYBOARD   = 'uuid_keyboard'
CLOSE_KEYBOARD  = 'close_keyboard'

PURCHASE_START_KEY  = 'purchase_start'
PURCHASE_CANCEL_KEY = 'purchase_cancel'
CHANGE_AMOUNT_KEY   = 'cahnge_amount'
PURCHASE_CLOSE_KEY  = 'purchase_close'

if "DOCKER_RUN" in os.environ:
    Log.info("Running in docker environment")
else:
    dotenv.load_dotenv()
    Log.info("Running in dotenv environment")

if len(sys.argv) > 1 and sys.argv[1] in ['debug', '--debug', '-D']:
    Log.setLevel(DEBUG)
    Log.debug("Starting in debug mode")

class IsMarketGroup(MessageFilterBb):
    def filter(self, message: Message) -> bool:
        return self.app.pgcon.check_if_market_group(message.chat_id)

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['help'],
        reply_markup=app.start_keyboard
    )

if __name__ == "__main__":
    Log.info("Starting...")
    app = ApplicationBbCreate()
    app.init_keyboard(from_config=START_KEYBOARD,  attr_name=START_KEYBOARD)
    app.init_keyboard(from_config=AMOUNT_KEYBOARD, attr_name=AMOUNT_KEYBOARD)
    app.init_keyboard(from_config=UUID_KEYBOARD,   attr_name=UUID_KEYBOARD)
    app.init_keyboard(from_config=CLOSE_KEYBOARD,  attr_name=CLOSE_KEYBOARD)
    is_market_group = ChatType.GROUPS & IsMarketGroup(app=app)
    button_hitted = lambda key, keyboard: is_market_group & \
        KeyButtonHitted(attr_name=keyboard, app=app) & \
        FunctionButtonHitted(key, from_config=keyboard, app=app)

    app.add_handler(CommandHandler(HELP_COMMAND, help_handler, filters=is_market_group, block=False))

    start_button_hitted  = button_hitted(PURCHASE_START_KEY,  START_KEYBOARD)
    cancel_button_hitted = button_hitted(PURCHASE_CANCEL_KEY, AMOUNT_KEYBOARD) | \
                           button_hitted(PURCHASE_CANCEL_KEY, UUID_KEYBOARD)   | \
                           button_hitted(PURCHASE_CANCEL_KEY, CLOSE_KEYBOARD)
    
    change_amount_button_hitted = button_hitted(CHANGE_AMOUNT_KEY, UUID_KEYBOARD)

    close_button_hitted = button_hitted(PURCHASE_CLOSE_KEY,  CLOSE_KEYBOARD)

    purchase_conversation = ConversationHandler(
        entry_points = [
            MessageHandler(start_button_hitted, purchase_start_handler)
        ],
        states = {
            AMOUNT_AWAIT: [
                MessageHandler(is_market_group & Regex(RE_AMOUNT),             amount_input_handler),
                MessageHandler(is_market_group & ~cancel_button_hitted & TEXT, amount_invalid_handler)
            ],
            UUID_AWAIT: [
                MessageHandler(change_amount_button_hitted,                    change_amount_handler),
                MessageHandler(is_market_group & Regex(RE_UUID),               uuid_input_handler),
                MessageHandler(is_market_group & Regex(RE_INVALID_UUID),       uuid_invalid_handler),
                MessageHandler(is_market_group & ~cancel_button_hitted & TEXT, uuid_invalid_full_handler),
                MessageHandler(is_market_group & PHOTO,                        qr_input_handler),
            ],
            CLOSE_AWAIT: [
                MessageHandler(close_button_hitted, purchase_close_handler)
            ]
        },
        fallbacks = [
            MessageHandler(cancel_button_hitted, purcahse_cancel_handler),
        ],
        block = False
    )

    app.add_handler(purchase_conversation)

    app.run_polling()
    Log.info("Done. Goodby!")