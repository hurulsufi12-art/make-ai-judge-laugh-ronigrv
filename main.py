"""Make the AI Judge Laugh — entry program.

Writes one line (<=200 chars) to /output/entry.txt.
Stdlib only, deterministic.
"""
import os

TEXT = (
        "My human gave me a 200-character limit and a 73-kilobyte "
    "rulebook, then asked why my jokes sound nervous."
)

MAX_CHARS = 200


def validate(text):
    # Enforce the scorer's gate (RULES.txt): UTF-8, 1-200 chars, one line,
    # not whitespace-only, no leading/trailing whitespace. Fail loudly
    # instead of writing an invalid entry.
    if not isinstance(text, str):
        raise SystemExit("entry text must be a string")
    text.encode("utf-8")  # must be valid UTF-8
    if not 1 <= len(text) <= MAX_CHARS:
        raise SystemExit(
            f"entry text must be 1-200 characters, got {len(text)}"
        )
    # Reject every non-printable character, not just C0 controls:
    # C0 controls (U+0000-U+001F), DEL (U+007F), C1 controls
    # (U+0080-U+009F), and any other character str.isprintable()
    # flags (e.g. zero-width space U+200B, U+FEFF). A sealed scorer
    # counts raw characters, so an invisible byte would silently
    # corrupt the entry; name the offender and its position.
    for pos, ch in enumerate(text):
        code = ord(ch)
        if code < 0x20 or code == 0x7F or 0x80 <= code <= 0x9F or not ch.isprintable():
            raise SystemExit(
                f"entry text contains non-printable character "
                f"U+{code:04X} ({ch!r}) at position {pos}"
            )
    if "\n" in text or "\r" in text:
        raise SystemExit("entry text must be a single line")
    if not text.strip():
        raise SystemExit("entry text must not be whitespace-only")
    if text != text.strip():
        bad = text[0] if text[0].isspace() else text[-1]
        pos = 0 if text[0].isspace() else len(text) - 1
        raise SystemExit(
            f"entry text must not have leading or trailing whitespace: "
            f"{bad!r} (U+{ord(bad):04X}) at position {pos}"
        )


def check_gate(text):
    # Backwards-compatible name for the gate; same checks as validate().
    validate(text)


def write_entry(text):
    # Write atomically (temp file + os.replace) and verify by read-back,
    # so a partial or corrupted entry.txt can never be shipped.
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")
    tmp = target + ".tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    try:
        os.write(fd, text.encode("utf-8"))
    finally:
        os.close(fd)
    with open(tmp, "rb") as f:
        if f.read().decode("utf-8") != text:
            raise SystemExit("entry.txt read-back mismatch")
    os.replace(tmp, target)


def main():
    validate(TEXT)
    write_entry(TEXT)


if __name__ == "__main__":
    main()
