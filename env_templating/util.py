def confirm(message: str, default: bool = True) -> bool:
    """Prompt the user for a confirmation response"""
    while True:
        response = input(f"{message} [{'Y/n' if default else 'y/N'}]: ").strip().lower()
        if response in ("y", "n"):
            return response == "y"
        if not response:
            return default
