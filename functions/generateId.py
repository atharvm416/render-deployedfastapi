def generate_code(prefix: str, id: int, length: int = 6) -> str:
    return f"{prefix}-{str(id).zfill(length)}"
