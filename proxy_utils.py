from __future__ import annotations

from urllib.parse import unquote, urlparse

# Maps URL schemes to Telethon/python_socks proxy_type strings.
_SCHEME_TO_TELETHON = {
    "socks5": "socks5",
    "socks5h": "socks5",
    "socks4": "socks4",
    "http": "http",
    "https": "http",
}


def normalize_proxy_url(url: str | None) -> str | None:
    """Ensure the proxy URL has a scheme, defaulting to http:// when missing.

    aiogram/aiohttp-socks require an explicit scheme (parse_proxy_url raises on
    a schemeless "host:port"), while Telethon tolerates either. Normalizing here
    keeps a single source of truth so both clients accept the same .env value.
    """
    if not url:
        return None
    url = url.strip()
    if not url:
        return None
    if "://" in url:
        return url
    # Schemeless "host:port" or "user:pass@host:port" -> assume HTTP proxy.
    return f"http://{url}"


def telethon_proxy(url: str | None):
    """Convert a proxy URL into the tuple Telethon expects.

    Accepts forms like:
        http://host:port
        http://login:password@host:port
        socks5://host:1080

    Returns None when no proxy is configured. Telethon's `_parse_proxy`
    signature is (proxy_type, addr, port, rdns, username, password).
    """
    if not url:
        return None

    parsed = urlparse(url if "://" in url else f"//{url}", scheme="http")
    scheme = (parsed.scheme or "http").lower()
    proxy_type = _SCHEME_TO_TELETHON.get(scheme)
    if proxy_type is None:
        raise ValueError(
            f"Неподдерживаемая схема прокси {scheme!r}. "
            "Используй http://, socks5:// или socks4://."
        )

    host = parsed.hostname
    port = parsed.port
    if not host or not port:
        raise ValueError(f"В прокси-URL не хватает хоста или порта: {url!r}")

    username = unquote(parsed.username) if parsed.username else None
    password = unquote(parsed.password) if parsed.password else None
    # rdns=True resolves the hostname through the proxy (recommended for SOCKS).
    return (proxy_type, host, port, True, username, password)
