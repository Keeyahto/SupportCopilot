from kits.kit_chunker.chunker import split_text, split_markdown


def test_split_text_overlap():
    text = "x" * 100
    chunks = split_text(text, max_tokens=32, overlap=8)
    assert chunks and len(chunks) > 1
    assert chunks[0].endswith("x")


def test_split_markdown_headings():
    md = "# A\npara\n## B\nmore text"
    chunks = split_markdown(md, max_tokens=16, overlap=4)
    assert len(chunks) >= 2

