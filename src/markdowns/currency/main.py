def generate_currency_list_markdown(data: list) -> str:

    final_text = ""

    for item in data:
        item_text = f"""
                    ## 💱 Currency Exchange: {item.get("name", "")}

                    | Field              | Value |
                    |--------------------|-------|
                    | **From Currency**  | {item.get("fromCurrency", "")} |
                    | **To Currency**    | {item.get("toCurrency", "")} |
                    | **High**           | {item.get("high", "")} |
                    | **Low**            | {item.get("low", "")} |
                    | **Bid Variation**  | {item.get("bidVariation", "")} |
                    | **% Change**       | {item.get("percentageChange", "")} |
                    | **Bid Price**      | {item.get("bidPrice", "")} |
                    | **Ask Price**      | {item.get("askPrice", "")} |
                    | **Updated At**     | {item.get("updatedAtDate", "")} |
                    | **12M Variation**  | {item.get("variation12Months", "")} |"""
        final_text += item_text
    return final_text
