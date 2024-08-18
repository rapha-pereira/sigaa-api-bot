"""Commands file. Here we set the bot commands and add them to the factory."""

from abc import ABC, abstractmethod
from telegram import Update


class Command(ABC):
    _PARSE_MODE = "Markdown"

    """Abstract base class for all command handlers."""
    def __init__(self, update: Update):
        self.update = update

    @abstractmethod
    async def execute(self):
        """Execute command logic. Must be implemented by subclasses."""
        pass

    @property
    def is_bot(self) -> bool:
        """Optional validate user logic for all commands."""
        # Check if the user is not a bot
        return self.update.message.from_user.is_bot


class _StartCommand(Command):
    _MESSAGE = (
        "Olá, sou o bot do SIGAA! Sirvo para trazer, de maneira rápida, informações do seu perfil no SIGAA.\n"
        "Qual informação você gostaria de acessar? (Perfil, Cursos)"
    )
    _IS_BOT_MESSAGE = (
        "Não posso prestar atendimentos a bots."
    )

    def __init__(self, update: Update):
        super().__init__(update)

    async def execute(self):
        if not self.is_bot:
            await self.update.message.reply_text(
                text=self._MESSAGE,
                parse_mode=self._PARSE_MODE
            )
        else:
            await self.update.message.reply_text(
                text=self._IS_BOT_MESSAGE,
                parse_mode=self._PARSE_MODE
            )


class _HelpCommand(Command):
    _MESSAGE = (
        "Sou um bot que, através da API do SIGAA (não oficial), traz informações do seu perfil na plataforma."
    )
    _IS_BOT_MESSAGE = (
        "Não posso prestar atendimentos a bots."
    )

    def __init__(self, update: Update):
        super().__init__(update)

    async def execute(self):
        if not self.is_bot:
            await self.update.message.reply_text(
                text=self._MESSAGE,
                parse_mode=self._PARSE_MODE
            )
        else:
            await self.update.message.reply_text(
                text=self._IS_BOT_MESSAGE,
                parse_mode=self._PARSE_MODE
            )


class _UnknownCommand(Command):
    _MESSAGE = (
        "Hm, não conheço este comando ainda."
    )
    _IS_BOT_MESSAGE = (
        "Não posso prestar atendimentos a bots."
    )

    def __init__(self, update: Update):
        super().__init__(update)

    async def execute(self):
        if not self.is_bot:
            await self.update.message.reply_text(
                text=self._MESSAGE,
                parse_mode=self._PARSE_MODE
            )
        else:
            await self.update.message.reply_text(
                text=self._IS_BOT_MESSAGE,
                parse_mode=self._PARSE_MODE
            )


class CommandsFactory:
    @staticmethod
    def get_command(command_name: str, update: Update) -> _StartCommand | _HelpCommand | _UnknownCommand:
        commands = {
            "/start": _StartCommand,
            "/help": _HelpCommand
        }
        command_class = commands.get(command_name, _UnknownCommand)
        return command_class(update)
