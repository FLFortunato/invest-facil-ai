import httpx
import os
from typing import Any


async def fetch_stock_api(params: str) -> Any:
    async with httpx.AsyncClient() as client:
        x_api_key = os.getenv("X_API_KEY")
        if not x_api_key:
            raise Exception("X_API_KEY not found")

        headers = {"x-api-key": x_api_key}

        try:
            response = await client.get(
                f"https://investfacilhub-be.com.br/api/v1/{params}",
                headers=headers,
            )

            data = response.json()
            if "results" not in data:
                raise RuntimeError("API response does not contain 'results' field.")

            return data["results"]

        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"Stock API returned error {e.response.status_code}: {e.response.text}"
            ) from e
        except httpx.RequestError as e:
            raise RuntimeError(f"Network error while fetching stock API: {e}") from e
        except ValueError as e:
            raise RuntimeError(f"Failed to parse JSON from stock API: {e}") from e
