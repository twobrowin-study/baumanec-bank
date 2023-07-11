import yaml, os

from baumanecbank_common.abstract import AbstractBbClass
from baumanecbank_common.log import Log

I18N_DIR       = 'I18N_DIR'
I18N_LOCALE    = 'I18N_LOCALE'
I18N_EXTENTION = 'I18N_EXTENTION'

class I18n(AbstractBbClass):
    def __init__(self, appname: str) -> None:
        super().__init__(appname)
        self.i18n_dir       = os.environ.get(I18N_DIR,       '../i18n')
        self.i18n_locale    = os.environ.get(I18N_LOCALE,    'en-US')
        self.i18n_extention = os.environ.get(I18N_EXTENTION, 'yaml')
        self.i18n_file   = f"{self.i18n_dir}/{self.i18n_locale}.{self.i18n_extention}"

        with open(self.i18n_file, "r") as stream:
            try:
                self.pure = yaml.safe_load(stream)[self.i18n_locale]
            except yaml.YAMLError as exc:
                Log.error(msg="Exception while loading I18n file", exc_info=exc)
        
        self.app = self.pure[self.appname]