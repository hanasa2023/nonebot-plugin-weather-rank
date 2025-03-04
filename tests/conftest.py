import os

import nonebot
import pytest
from nonebot.adapters.onebot.v11 import Adapter
from nonebug import NONEBOT_INIT_KWARGS


def pytest_configure(config: pytest.Config):
    config.stash[NONEBOT_INIT_KWARGS] = {
        'driver': '~fastapi',
        'log_level': 'DEBUG',
        'host': '127.0.0.1',
        'port': '9555',
    }
    os.environ['PLUGIN_ALCONNA_TESTENV'] = '1'


@pytest.fixture(scope='session', autouse=True)
def _load_bot():
    # 加载适配器
    driver = nonebot.get_driver()
    driver.register_adapter(Adapter)

    # 加载插件
    nonebot.load_from_toml('pyproject.toml')
