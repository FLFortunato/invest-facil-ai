from langchain_core.tools import tool
from src.markdowns.currency.main import generate_currency_list_markdown


from src.utils import fetch_stock_api


@tool
async def get_currencies_list():
    """
    Fetches real-time, up-to-date information about available currencies from the stock API
    and formats it in a Markdown-friendly table for easy readability.

    This tool provides:
    - Currency codes (e.g., USD, EUR, BRL)
    - Currency names
    - Optional metadata such as country or symbol

    The returned Markdown can be directly used by the agent to answer user questions
    about currency values or to list all supported currencies.

    Returns:
        str: A Markdown-formatted table containing current currency data.

    Raises:
        RuntimeError: If fetching or formatting the currency list fails. The original
                      exception message will be included for debugging purposes.
    """

    print("[get_currencies_list] Being called...")
    results = await fetch_stock_api("currencies/currencies-list")
    formatted = generate_currency_list_markdown(results)
    print(
        f"[get_currencies_list] Generated markdown length: {len(formatted)} characters"
    )
    return {"results": formatted}
