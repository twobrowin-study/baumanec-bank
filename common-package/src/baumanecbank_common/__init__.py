from baumanecbank_common.log import Log
from logging import INFO, DEBUG
Log.setLevel(INFO)

from baumanecbank_common.application import ApplicationBb
from baumanecbank_common.postgres    import PgCon
from baumanecbank_common.i18n        import I18n
from baumanecbank_common.qr          import RecognizeUuidFromQr

from baumanecbank_common.filter import (
    MessageFilterBb,
    KeyButtonHitted,
    FunctionButtonHitted
)

from baumanecbank_common.application_create import ApplicationBbCreate

START_COMMAND = 'start'
HELP_COMMAND  = 'help'

RE_AMOUNT       = r"^[0-9.,]+$"
RE_UUID         = r"^[0-9a-f]{12}$"
RE_INVALID_UUID = r"^[0-9a-f]+$"