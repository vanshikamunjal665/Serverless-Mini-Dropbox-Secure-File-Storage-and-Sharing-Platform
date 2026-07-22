"""
Small display-formatting helpers.
"""


def format_bytes(size) -> str:
    """
    Convert a byte count into a human-readable string.
    e.g. 1536 -> "1.5 KB"
    """
    if not size:
        return "0 B"

    size = float(size)
    units = ["B", "KB", "MB", "GB", "TB"]

    for unit in units:
        if size < 1024:
            return f"{int(size)} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024

    return f"{size:.1f} PB"
