import os
from json import load
from json import JSONDecodeError
from re import search


class ConfigError(Exception):
    """ Error that will be raised when there is a problem with the config file """

    def __init__(self, message="Error message was not set"):
        self.message = message

    def __str__(self) -> str:
        return self.message


class Config:

    def __init__(self, filename: str):
        """ Initializes the config object, raises ConfigError if the config file is not valid """
        if filename is None or str(filename).strip() == "":
            raise ConfigError("Filename cannot be empty")
        self.filename = str(filename).strip()

        if not self._valid_file():
            raise ConfigError("Config file does not exist or is not readable")
        self._config_data = self._load_config()
        self._valid_config_data()

    def _valid_file(self) -> bool:
        """ Checks if the config file exists and is readable """
        return os.path.isfile(self.filename) and os.access(self.filename, os.R_OK)

    def _load_config(self) -> dict:
        try:
            with open(self.filename) as file:
                return load(file)
        except JSONDecodeError:
            raise ConfigError("Config file is not valid JSON")

    def _valid_config_data(self) -> bool:
        """ Checks if the config file contains the required data """
        data = self._config_data

        requirements = ["mail"]
        for requirement in requirements:
            if requirement not in data:
                raise ConfigError(f"Config file does not contain top-level-requirement: {requirement}")

        self._valid_mail_settings()

        return True

    def _valid_mail_settings(self) -> bool:
        """ Checks if the config file contains the required mail data """
        data = self._config_data["mail"]

        requirements = ["sender_email", "recipient_email"]
        for requirement in requirements:
            if requirement not in data:
                raise ConfigError(f"Config file does not contain requirement: {requirement}")

        if not self.valid_email(data["sender_email"]):
            raise ConfigError("Sender email must be a string and a valid email address")

        if not self.valid_email(data["recipient_email"]):
            raise ConfigError("Recipient email must be a string and a valid email address")

        return True

    def valid_email(self, email) -> bool:
        return isinstance(email, str) and search("([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+", email)

    def __setitem__(self, key, value):
        raise ConfigError("Config object is read-only")

    def __getitem__(self, item):
        try:
            return self._config_data[item]
        except KeyError:
            raise ConfigError(f"Config file does not contain: {item}")
