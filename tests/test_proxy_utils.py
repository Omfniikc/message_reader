import pytest

from proxy_utils import telethon_proxy


def test_none():
    assert telethon_proxy(None) is None
    assert telethon_proxy("") is None


def test_http_with_auth():
    t = telethon_proxy("http://user:pass@1.2.3.4:8080")
    assert t == ("http", "1.2.3.4", 8080, True, "user", "pass")


def test_socks5_no_auth():
    t = telethon_proxy("socks5://localhost:1080")
    assert t == ("socks5", "localhost", 1080, True, None, None)


def test_url_encoded_credentials():
    t = telethon_proxy("http://user%40corp:p%40ss@proxy.example.com:3128")
    assert t == ("http", "proxy.example.com", 3128, True, "user@corp", "p@ss")


def test_missing_port():
    with pytest.raises(ValueError):
        telethon_proxy("http://proxy.example.com")


def test_unknown_scheme():
    with pytest.raises(ValueError):
        telethon_proxy("ftp://proxy.example.com:21")
