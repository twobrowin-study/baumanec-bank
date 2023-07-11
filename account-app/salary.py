from baumanecbank_common import ApplicationBb

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import ContextTypes, ConversationHandler

CALBACK_EMPLOYEE_PREFIX   = "employee_"
CALBACK_EMPLOYEE_TEMPLATE = "employee_*"
CALBACK_EMPLOYEE_PATTERN  = "employee_{employee.employee_client_uuid}"

SALARY_FUNCTION = 'salary'

SALARY_AWAIT_AMOUNT,SALARY_CLOSE_AWAIT = range(2)

async def salary_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['salary']['employees'],
        reply_markup=InlineKeyboardMarkup.from_column([
            InlineKeyboardButton(
                app.i18n.app['salary']['employee_template'].format(employee=employee),
                callback_data=CALBACK_EMPLOYEE_PATTERN.format(employee=employee)
            )
            for employee in app.pgcon.get_employees_by_account_chat_id(update.effective_user.id)
        ])
    )

async def salary_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    app: ApplicationBb = context.application
    employee_uuid = update.callback_query.data.removeprefix(CALBACK_EMPLOYEE_PREFIX)
    client = app.pgcon.get_client_by_uuid(employee_uuid)
    context.user_data['client'] = client
    await update.callback_query.message.reply_markdown(
        app.i18n.app['salary']['callback'].format(client=client),
        reply_markup=app.keyboard_amount
    )
    return SALARY_AWAIT_AMOUNT

async def salary_amount_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    amount = float(update.message.text.replace(',', '.'))
    context.user_data["amount"] = amount
    await update.message.reply_markdown(
        app.i18n.app['salary']['amount_input'].format(
            amount=amount,
            govtax=amount*0.13,
            client=context.user_data['client']
        ),
        reply_markup=app.keyboard_close
    )
    return SALARY_CLOSE_AWAIT

async def salary_amount_invalid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    app: ApplicationBb = context.application
    await update.message.reply_markdown(
        app.i18n.app['salary']['amount_invalid'],
        reply_markup=app.keyboard_amount
    )
    return SALARY_AWAIT_AMOUNT

async def salary_close_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app: ApplicationBb = context.application
    amount  = context.user_data["amount"]
    client  = context.user_data["client"]
    account = app.pgcon.get_account_by_chat_id(update.message.chat_id)

    err = app.pgcon.create_salary(account.firm_card_code_id, client.card_code_id, amount)
    if err is not None:
        await update.message.reply_markdown(
            app.i18n.app['salary']['error'],
            reply_markup=app.keyboard_main
        )
        return ConversationHandler.END

    await update.message.reply_markdown(
        app.i18n.app['salary']['success'],
        reply_markup=app.keyboard_main
    )
    return ConversationHandler.END
