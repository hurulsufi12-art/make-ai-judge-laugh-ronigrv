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
        raise SystemExit("entry text must be 1-200 characters")
    if any(ord(c) < 0x20 for c in text):
        raise SystemExit("entry text contains a control character (\\x00-\\x1f)")
    if "\n" in text or "\r" in text:
        raise SystemExit("entry text must be a single line")
    if not text.strip():
        raise SystemExit("entry text must not be whitespace-only")
    if text != text.strip():
        raise SystemExit("entry text must not have leading or trailing whitespace")


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
