from langchain_core.tools import tool
from src.markdowns.stock.main import (
    generate_company_markdown,
    generate_price_history_markdown,
)
import httpx
import os
from typing import Any


async def get_company_main_data(ticker: str) -> Any:
    async with httpx.AsyncClient() as client:
        x_api_key = os.getenv("X_API_KEY")
        if not x_api_key:
            raise Exception("X_API_KEY not found")

        headers = {"x-api-key": x_api_key}

        try:
            response = await client.get(
                f"https://investfacilhub-be.com.br/api/v1/stock/company?companyCode={ticker}",
                headers=headers,
            )

            result = response.json()

            return result["results"]
        except Exception as e:
            print(e)


@tool
async def search_stock_updated_data(ticker: str):
    """
    Fetches up-to-date financial and profile data for a given company ticker
    from the InvestFacilHub API. Returns a formatted Markdown report with key
    information such as company overview, market indicators, stock prices,
    and valuation formulas.

    Parameters:
        ticker (str): The stock ticker symbol of the company (e.g., "PETR4").

    Returns:
        str: A Markdown-formatted string summarizing the company's financial data
        and profile.
    """

    if len(ticker) > 5:
        return ""

    print(f"[search_stock_updated_data] Called with ticker: {ticker}")
    result = await get_company_main_data(ticker)
    if not result:
        print("[search_stock_updated_data] No data received")
        return "No data found for ticker: " + ticker

    formatted = generate_company_markdown(result)
    print(
        f"[search_stock_updated_data] Generated markdown length: {len(formatted)} characters"
    )
    return {"results": formatted}


@tool("search_stock_aggregated_data", return_direct=True)
async def search_stock_aggregated_data(ticker: str, property: str):
    """
    The property field can be one of the followings:

    historyDataPrice: For stock price history


    Parameters:
        ticker (str): The stock ticker symbol of the company (e.g., "PETR4").

    Returns:
        str: A Markdown-formatted string summarizing the property requested.
    """

    print(
        f"[search_stock_aggregated_data] Called with ticker: {ticker} and property: {property}"
    )
    result = await get_company_main_data(ticker)
    if not result:
        print("[search_stock_aggregated_data] No data received")
        return "No data found for ticker: " + ticker

    if property not in result:
        print(
            f"[search_stock_aggregated_data] Property '{property}' not found in result keys: {list(result.keys())}"
        )
        return f"Property '{property}' not found in stock data."

    data = result[property]
    print(
        f"[search_stock_aggregated_data] Extracted {len(data)} items from property '{property}'"
    )

    formatted = generate_price_history_markdown(list(reversed(data))[0:30])
    print(
        f"[search_stock_aggregated_data] Generated markdown length: {len(formatted)} characters"
    )
    return {"results": formatted}
