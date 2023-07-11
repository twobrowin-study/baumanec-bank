from telegram.ext.filters import MessageFilter

from baumanecbank_common.application import ApplicationBb

from telegram import Message

class MessageFilterBb(MessageFilter):
    def __init__(self,
                 name: str = None, data_filter: bool = False,
                 app: ApplicationBb = None):
        super().__init__(name, data_filter)
        self.app = app

class KeyButtonHitted(MessageFilterBb):
    def __init__(self, attr_name: str = 'reply_keyboard',
                 name: str = None, data_filter: bool = False,
                 app: ApplicationBb = None):
        super().__init__(name, data_filter, app)
        self.attr_name = attr_name

    def filter(self, message: Message) -> bool:
        return self.app.check_if_key_in_keyboard(message.text, self.attr_name)

class FunctionButtonHitted(MessageFilterBb):
    def __init__(self, function: str, from_config: str = 'keyboard',
                 name: str = None, data_filter: bool = False,
                 app: ApplicationBb = None):
        super().__init__(name, data_filter, app)
        self.function    = function
        self.from_config = from_config

    def filter(self, message: Message) -> bool:
        return self.app.get_function_from_keyboard(message.text, self.from_config) == self.function