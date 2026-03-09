import re


HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]+\)")
ICON_TOKEN_RE = re.compile(r"(?<!\w)/[a-z][a-z0-9_-]*", re.IGNORECASE)
REPEATED_PUNCT_RE = re.compile(r"([!?.,:;])\1+")
EMPTY_BULLET_RE = re.compile(r"^\s*[-*+]\s*$")
RULE_ONLY_RE = re.compile(r"^\s*[-_=]{3,}\s*$")


def _clean_line(line: str) -> str:
    line = ICON_TOKEN_RE.sub("", line)
    line = REPEATED_PUNCT_RE.sub(r"\1", line)
    line = re.sub(r"\s{2,}", " ", line).strip()
    return line


def clean_markdown(markdown: str) -> str:
    text = markdown.replace("\r\n", "\n").replace("\r", "\n")
    text = HTML_COMMENT_RE.sub("", text)
    text = MARKDOWN_IMAGE_RE.sub("", text)

    cleaned_lines = []
    previous_blank = False

    for raw_line in text.split("\n"):
        line = _clean_line(raw_line)

        if not line:
            if not previous_blank:
                cleaned_lines.append("")
            previous_blank = True
            continue

        if EMPTY_BULLET_RE.match(line):
            continue
        if RULE_ONLY_RE.match(line):
            continue

        cleaned_lines.append(line)
        previous_blank = False

    return "\n".join(cleaned_lines).strip()
