import asyncio
from typing import Any, Callable, Coroutine

from telegram.ext._application import Application
from telegram.ext._basepersistence import BasePersistence
from telegram.ext._contexttypes import ContextTypes
from telegram.ext._updater import Updater
from telegram.ext._baseupdateprocessor import BaseUpdateProcessor

from baumanecbank_common.postgres import PgCon
from baumanecbank_common.i18n import I18n
from baumanecbank_common.log import Log

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

class ApplicationBb(Application):
    def __init__(self, *, bot: Any, update_queue: asyncio.Queue, updater: Updater | None, job_queue: Any, update_processor: BaseUpdateProcessor, persistence: BasePersistence | None, context_types: ContextTypes, post_init: Callable[[Application], Coroutine[Any, Any, None]] | None, post_shutdown: Callable[[Application], Coroutine[Any, Any, None]] | None, post_stop: Callable[[Application], Coroutine[Any, Any, None]] | None):
        super().__init__(bot=bot, update_queue=update_queue, updater=updater, job_queue=job_queue, update_processor=update_processor, persistence=persistence, context_types=context_types, post_init=post_init, post_shutdown=post_shutdown, post_stop=post_stop)
        self.appname: str   = None
        self.pgcon:   PgCon = None
        self.i18n:    I18n  = None
        self.update:  Callable[[ApplicationBb], Coroutine[Any, Any, None]] = None

        self.reply_keyboard_keys = []
        self.reply_keyboard      = ReplyKeyboardRemove()
    
    def init_keyboard(self, from_config: str = 'keyboard', attr_name: str = 'reply_keyboard') -> None:
        keyboard_keys = [
            val for _,val in self.i18n.app[from_config].items()
        ] if from_config in self.i18n.app else []
        setattr(self, f"{attr_name}_keys", keyboard_keys)

        if from_config not in self.i18n.app:
            setattr(self, attr_name, ReplyKeyboardRemove())
            return

        reply_keyboard = ReplyKeyboardMarkup([
            keyboard_keys[idx:idx+2]
            for idx in range(0,len(keyboard_keys),2)
        ])
        setattr(self, attr_name, reply_keyboard)

    def get_function_from_keyboard(self, key: str, from_config: str = 'keyboard') -> str|None:
        for fun,val in self.i18n.app[from_config].items():
            if val == key:
                return fun
        return None

    def check_if_key_in_keyboard(self, key: str, attr_name: str = 'reply_keyboard') -> bool:
        if not hasattr(self, attr_name):
            return False
        return key in getattr(self, f"{attr_name}_keys")

    def split_by_max_len(self, message: str, delimeter='\n', max_len=4096) -> list[str]:
        if len(message) < max_len:
            return [message]
        ret = []
        while len(message) > max_len:
            index = message[:max_len].rfind(delimeter)
            ret.append(message[:index])
            message = message[index:]
        ret.append(message)
        return ret

    def create_update_task(self) -> None:
        if self.update is not None:
            Log.info("Creating update task")
            self.create_task(
                self.update(self),
                {
                    "action": "update task",
                    "appname": self.appname
                }
            )