from langchain_core.tools import tool
from src.markdowns.currency.main import generate_currency_list_markdown


from src.utils import fetch_stock_api


@tool("currency_tool", return_direct=True)
async def get_currencies_list():
    """
    Retrieves a real-time list of supported currencies from the stock API
    and returns it in a Markdown-friendly format.

    The data typically includes currency codes, names, and other metadata,
    which is then passed to a Markdown generator for clean presentation.

    Returns:
        str: A Markdown-formatted table containing the list of available currencies.

    Raises:
        RuntimeError: If fetching or formatting the currency list fails for any reason.
                      The original exception message is included for debugging purposes.
    """
    print("[get_currencies_list] Being called...")
    results = await fetch_stock_api("currencies/currencies-list")
    formatted = generate_currency_list_markdown(results)
    print(
        f"[get_currencies_list] Generated markdown length: {len(formatted)} characters"
    )
    return {"results": formatted}
