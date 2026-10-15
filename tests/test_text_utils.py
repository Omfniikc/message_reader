from bot.text_utils import chunk_text


def test_short_text_single_chunk():
    assert chunk_text("hello") == ["hello"]


def test_empty():
    assert chunk_text("   ") == []


def test_long_text_splits():
    text = " ".join(["word"] * 2000)  # ~10k chars
    chunks = chunk_text(text, max_size=500)
    assert len(chunks) > 1
    assert all(len(c) <= 500 for c in chunks)
    # no content lost (modulo whitespace)
    assert "".join(chunks).replace(" ", "").replace("\n", "") == text.replace(" ", "")


def test_paragraph_boundary():
    text = "a" * 300 + "\n" + "b" * 300
    chunks = chunk_text(text, max_size=400)
    assert chunks[0] == "a" * 300
    assert chunks[1] == "b" * 300
