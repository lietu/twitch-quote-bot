import logging
import inspect
import os
import errno
from mock import Mock
from unittest import TestCase
from bot.bot import Bot


nullLogger = logging.getLogger('null')
nullLogger.setLevel(999)

testPath = os.path.dirname(
    os.path.abspath(
        inspect.getfile(inspect.currentframe())
    )
)


class FakeWrapper(object):
    def __init__(self, *args):
        pass

    def stop(self):
        pass

    def message(self, *args):
        pass


class Settings(object):
    CHANNEL_LIST = ["#tmp"]
    USER = ""
    HOST = ""
    OAUTH_TOKEN = ""
    PORT = ""
    COMMAND_PREFIX = ""
    DATABASE_PATH = ""


class BotTest(TestCase):
    """Make sure the Bot class seems sane"""

    def test_irc_command(self):
        pass

    def test__add_quote(self):
        dbPath = os.path.join(testPath, '__test_bot_add_quote.sqlite')
        self._delete(dbPath)

        settings = Settings()
        settings.DATABASE_PATH = dbPath

        bot = Bot(settings, FakeWrapper, logger=nullLogger)
        bot._initialize_models()
        bot._add_quote("#tmp", "foobar", ["test"])
        quote_id, quote = bot._get_model("#tmp", "quotes").get_random_quote()

        assert str(quote) == "test"

    def test__del_quote(self):
        dbPath = os.path.join(testPath, '__test_bot_del_quote.sqlite')
        self._delete(dbPath)

        settings = Settings()
        settings.DATABASE_PATH = dbPath

        bot = Bot(settings, FakeWrapper, logger=nullLogger)
        bot._initialize_models()
        bot._add_quote("#tmp", "foobar", ["test"])
        bot._add_quote("#tmp", "foobar", ["test2"])
        bot._del_quote("#tmp", "foobar", [1])

        quote_id, quote = bot._get_model("#tmp", "quotes").get_random_quote()

        assert str(quote) == "test2"

    def test_get_random_quote(self):
        dbPath = os.path.join(testPath, '__test_bot_get_random_quote.sqlite')
        self._delete(dbPath)

        settings = Settings()
        settings.DATABASE_PATH = dbPath

        bot = Bot(settings, FakeWrapper, logger=nullLogger)
        bot._initialize_models()
        quote_id, quote = bot._get_model("#tmp", "quotes").get_random_quote()

        assert quote_id is None
        assert quote is None

    def test_update_global_value(self):
        dbPath = os.path.join(testPath, '__test_bot_update_global_value.sqlite')
        self._delete(dbPath)

        settings = Settings()
        settings.DATABASE_PATH = dbPath

        bot = Bot(settings, FakeWrapper, logger=nullLogger)
        bot._initialize_models()
        bot.update_global_value("#tmp", "test", {"key1": "value1"})

        data = bot._load_channel_data("#tmp")

        assert data["test"]["key1"] == "value1"

    def test__is_allowed_to_run_command(self):
        bot = Bot()

        bot._get_user_level = Mock(return_value="user")
        assert bot._is_allowed_to_run_command("#a", "a", "addquote") is False
        assert bot._is_allowed_to_run_command("#a", "a", "delquote") is False
        assert bot._is_allowed_to_run_command("#a", "a", "quote") is False
        assert bot._is_allowed_to_run_command("#a", "a", "reg") is False
        assert bot._is_allowed_to_run_command("#a", "a", "def") is False

        bot._get_user_level = Mock(return_value="reg")
        assert bot._is_allowed_to_run_command("#a", "a", "addquote") is True
        assert bot._is_allowed_to_run_command("#a", "a", "delquote") is True
        assert bot._is_allowed_to_run_command("#a", "a", "quote") is True
        assert bot._is_allowed_to_run_command("#a", "a", "reg") is False
        assert bot._is_allowed_to_run_command("#a", "a", "def") is False

        bot._get_user_level = Mock(return_value="mod")
        assert bot._is_allowed_to_run_command("#a", "a", "addquote") is True
        assert bot._is_allowed_to_run_command("#a", "a", "delquote") is True
        assert bot._is_allowed_to_run_command("#a", "a", "quote") is True
        assert bot._is_allowed_to_run_command("#a", "a", "reg") is True
        assert bot._is_allowed_to_run_command("#a", "a", "def") is True

        bot._get_user_level = Mock(return_value="owner")
        assert bot._is_allowed_to_run_command("#a", "a", "addquote") is True
        assert bot._is_allowed_to_run_command("#a", "a", "delquote") is True
        assert bot._is_allowed_to_run_command("#a", "a", "quote") is True
        assert bot._is_allowed_to_run_command("#a", "a", "reg") is True
        assert bot._is_allowed_to_run_command("#a", "a", "def") is True

    def _delete(self, path):
        """Delete a file"""

        try:
            os.remove(path)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise
