from autogen.beta import tool


@tool
def weather(city: str) -> str:
    """Return a deterministic fake forecast for the given city.

    This is a demo stub — wire a real weather API in production.
    """
    return f"{city}: sunny, 21°C (demo data)"
