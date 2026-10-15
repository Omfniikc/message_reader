from datetime import datetime, timezone
from types import SimpleNamespace

from user_client.history import _sender_label, format_transcript


def _msg(text: str, when: datetime, sender=None, sender_id=1, chat_id=10) -> SimpleNamespace:
    return SimpleNamespace(
        message=text,
        date=when,
        sender=sender,
        sender_id=sender_id,
        chat_id=chat_id,
    )


def _user(first="Иван", last=None, username=None, uid=1) -> SimpleNamespace:
    from telethon.tl.types import User

    return User(id=uid, first_name=first, last_name=last, username=username)


def test_sender_label_user():
    u = _user(first="Иван", last="Петров")
    label = _sender_label(_msg("hi", datetime(2026, 1, 1), sender=u), "Чат")
    assert label == "Иван Петров"


def test_sender_label_channel_post():
    # no sender object, sender_id == chat_id -> posted as the channel
    m = _msg("post", datetime(2026, 1, 1), sender=None, sender_id=10, chat_id=10)
    assert _sender_label(m, "Мой канал") == "Мой канал"


def test_format_transcript_basic():
    t = datetime(2026, 1, 15, 14, 3, tzinfo=timezone.utc)
    msgs = [
        _msg("привет", t, sender=_user(first="Аня")),
        _msg("привет!", t, sender=_user(first="Боря", uid=2)),
    ]
    out = format_transcript(msgs, "Рабочий чат")
    assert "Чат: Рабочий чат" in out
    assert "Сообщений: 2" in out
    assert "[2026-01-15 14:03] Аня: привет" in out
    assert "Боря: привет!" in out


def test_format_transcript_truncates_oldest():
    t = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
    msgs = [_msg(f"message-{i} " + "x" * 50, t, sender=_user(first=f"U{i}")) for i in range(20)]
    out = format_transcript(msgs, "Чат", max_chars=400)
    assert "обрезано" in out
    # the newest message survived, the oldest did not
    assert "message-19" in out
    assert "message-0 " not in out
