"""States file. Here we set the bot states in between the conversation with user and add them to a factory."""

from abc import ABC, abstractmethod

from telegram import Update
from telegram.ext import ContextTypes


class BotState(ABC):
    _PARSE_MODE = "Markdown"

    @abstractmethod
    async def handle(
        self,
        bot_context: "BotContext",
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> bool:
        pass


class ServiceState(BotState):
    _SERVICE_NOT_AVAILABLE_MESSAGE = (
        "Serviço não disponível. Favor selecionar um destes: {api_services_list}"
    )
    _SERVICE_AVAILABLE_MESSAGE = (
        "Certo! Favor me passar suas informações de login no formato: *usuario;senha*"
    )

    def __init__(self) -> None:
        from sigaa_api_bot.bot.main import (
            api_available_services_dict,
            api_available_services_list,
        )

        self.api_available_services_list = api_available_services_list
        self.api_available_services_dict = api_available_services_dict

    async def _check_service_availability(self, service: str) -> bool:
        return service in self.api_available_services_list

    async def handle(
        self,
        bot_context: "BotContext",
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> bool:
        user_selected_service = update.message.text.lower()
        is_available = await self._check_service_availability(user_selected_service)
        if is_available:
            # Add the selected service to the conversation context
            context.user_data["selected_service"] = user_selected_service
            await update.message.reply_text(
                text=self._SERVICE_AVAILABLE_MESSAGE, parse_mode=self._PARSE_MODE
            )
            # Go to the next state
            bot_context.set_state(CredentialsState())
            return True
        if not is_available:
            await update.message.reply_text(
                text=self._SERVICE_NOT_AVAILABLE_MESSAGE.format(
                    api_services_list=self.api_available_services_list
                ),
                parse_mode=self._PARSE_MODE,
            )
            return False

    @property
    def state_identifier(self) -> int:
        return 1


class CredentialsState(BotState):
    _INVALID_CREDENTIALS_MESSAGE = "Formato inválido. Favor me passar suas informações de login no formato: *usuario;senha*"
    _CREDENTIALS_RECEIVED_MESSAGE = (
        "Credenciais recebidas com sucesso! Processando sua solicitação...\n"
        "_Por motivos de segurança, deletamos sua mensagem com as informações de login._"
    )

    async def _check_user_credentials(self, user_credentials: list) -> bool:
        return len(user_credentials) == 2

    async def handle(
        self,
        bot_context: "BotContext",
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> bool:
        user_credentials: list = update.message.text.split(";")
        is_valid_credentials = await self._check_user_credentials(user_credentials)
        if is_valid_credentials:
            username, password = user_credentials
            context.user_data["username"] = username
            context.user_data["password"] = password
            await update.message.reply_text(
                text=self._CREDENTIALS_RECEIVED_MESSAGE, parse_mode=self._PARSE_MODE
            )
            # Since credentials are saved already, delete them now
            await update.message.delete()
            return True
        if not is_valid_credentials:
            await update.message.reply_text(
                text=self._INVALID_CREDENTIALS_MESSAGE, parse_mode=self._PARSE_MODE
            )
            # Since credentials are saved already, delete them now
            await update.message.delete()
            bot_context.set_state(CredentialsState())
            return False

    @property
    def state_identifier(self) -> int:
        return 2


class BotContext:
    def __init__(self):
        # set initial bot state
        self.actual_state = ServiceState()

    def set_state(self, state: BotState):
        self.actual_state = state

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        return await self.actual_state.handle(self, update, context)
