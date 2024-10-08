from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from nonebot.adapters.onebot.v11 import GroupMessageEvent as GroupMessageEventV11
    from nonebot.adapters.onebot.v11 import (
        PrivateMessageEvent as PrivateMessageEventV11,
    )


def fake_group_message_event_v11(**field) -> 'GroupMessageEventV11':
    from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
    from nonebot.adapters.onebot.v11.event import Sender
    from pydantic import create_model

    _Fake = create_model('_Fake', __base__=GroupMessageEvent)

    class FakeEvent(_Fake):
        time: int = 1000000
        self_id: int = 1
        post_type: Literal['message'] = 'message'
        sub_type: str = 'normal'
        user_id: int = 10
        message_type: Literal['group'] = 'group'
        group_id: int = 10000
        message_id: int = 1
        message: Message = Message('test')
        raw_message: str = 'test'
        font: int = 0
        sender: Sender = Sender(
            card='',
            nickname='test',
            role='member',
        )
        to_me: bool = False

        class FakeConfig:
            extra = 'allow'

    return FakeEvent(**field)


def fake_private_message_event_v11(**field) -> 'PrivateMessageEventV11':
    from nonebot.adapters.onebot.v11 import Message, PrivateMessageEvent
    from nonebot.adapters.onebot.v11.event import Sender
    from pydantic import create_model

    _Fake = create_model('_Fake', __base__=PrivateMessageEvent)

    class FakeEvent(_Fake):
        time: int = 1000000
        self_id: int = 1
        post_type: Literal['message'] = 'message'
        sub_type: str = 'friend'
        user_id: int = 10
        message_type: Literal['private'] = 'private'
        message_id: int = 1
        message: Message = Message('test')
        raw_message: str = 'test'
        font: int = 0
        sender: Sender = Sender(nickname='test')
        to_me: bool = False

        class FakeConfig:
            extra = 'forbid'

    return FakeEvent(**field)
