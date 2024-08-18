# tests/test_handlers.py
import unittest
from sigaa_api_bot.bot.handlers import CommandFactory, StartCommand, HelpCommand, UnknownCommand


class TestCommandFactory(unittest.TestCase):
    def test_get_start_command(self):
        command = CommandFactory.get_command("/start")
        self.assertIsInstance(command, StartCommand)

    def test_get_help_command(self):
        command = CommandFactory.get_command("/help")
        self.assertIsInstance(command, HelpCommand)

    def test_get_unknown_command(self):
        command = CommandFactory.get_command("/unknown")
        self.assertIsInstance(command, UnknownCommand)


if __name__ == '__main__':
    unittest.main()
