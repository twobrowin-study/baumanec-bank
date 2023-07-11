import os
from telegram import Bot
from telegram.ext import (
    ApplicationBuilder,
    ChatMemberHandler
)

from baumanecbank_common.application import ApplicationBb
from baumanecbank_common.postgres import PgCon
from baumanecbank_common.i18n import I18n

from baumanecbank_common.handlers import (
    ErrorHandlerFun, ChatMemberHandlerFun
)

from typing import Any, Callable, Coroutine

async def default_post_init(app: ApplicationBb, my_commands: list[dict]) -> None:
    app.pgcon.write_event("Starting an application")
    bot: Bot = app.bot
    await bot.set_my_commands([
        (k, v)
        for command in my_commands
        for k,v in command.items()
    ])

    if app.update is not None:
        app.create_update_task()

async def post_init_std_my_commands(app: ApplicationBb) -> None:
    await default_post_init(app, app.i18n.pure['my_commands'])

async def post_init_app_my_commands(app: ApplicationBb) -> None:
    await default_post_init(app, app.i18n.app['my_commands'])

async def post_shutdown(app: ApplicationBb) -> None:
    app.pgcon.write_event("Stopping an application")

APP_NAME = 'APP_NAME'

def ApplicationBbCreate(initialize_my_commands_from_an_app: bool = False, update_task: Callable[[ApplicationBb], Coroutine[Any, Any, None]] = None) -> ApplicationBb:
    appname = os.environ.get(APP_NAME, 'app')
    pgcon   = PgCon(appname)
    i18n    = I18n(appname)
    pgcon.connect()
    token = pgcon.get_telegram_token()
    app: ApplicationBb = ApplicationBuilder() \
        .application_class(ApplicationBb) \
        .token(token) \
        .post_init(post_init_std_my_commands if not initialize_my_commands_from_an_app else post_init_app_my_commands) \
        .post_shutdown(post_shutdown) \
        .build()
    app.appname = appname
    app.pgcon   = pgcon
    app.i18n    = i18n
    app.update  = update_task
    app.add_error_handler(ErrorHandlerFun, block=False)
    app.add_handler(ChatMemberHandler(ChatMemberHandlerFun, chat_member_types=ChatMemberHandler.MY_CHAT_MEMBER, block=False))
    return app