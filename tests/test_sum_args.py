from bot.sum_args import parse_sum_args


def test_empty():
    args = parse_sum_args("")
    assert args.chat_query is None
    assert args.limit is None
    assert args.instructions is None


def test_username_only():
    args = parse_sum_args("@durov")
    assert args.chat_query == "@durov"
    assert args.limit is None
    assert args.instructions is None


def test_username_with_limit():
    args = parse_sum_args("@durov 50")
    assert args.chat_query == "@durov"
    assert args.limit == 50


def test_username_limit_instructions():
    args = parse_sum_args("@durov 50 только про дедлайны")
    assert args.chat_query == "@durov"
    assert args.limit == 50
    assert args.instructions == "только про дедлайны"


def test_numeric_id_with_limit():
    args = parse_sum_args("-1001234567890 200")
    assert args.chat_query == "-1001234567890"
    assert args.limit == 200


def test_title_with_instructions_no_limit():
    args = parse_sum_args("рабочая только важное")
    assert args.chat_query == "рабочая"
    assert args.limit is None
    assert args.instructions == "только важное"


def test_tme_link():
    args = parse_sum_args("https://t.me/durov 30")
    assert args.chat_query == "https://t.me/durov"
    assert args.limit == 30
