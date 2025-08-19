from datetime import datetime, timezone


def generate_company_markdown(data: dict) -> str:
    md = f"""# Dados da Empresa: **{data.get('companyName')}** ({data.get('tickerb3')})

![Logo]({data.get('logoUrl')})

---

## Informações Gerais

| Campo                  | Valor                                         |
|------------------------|-----------------------------------------------|
| Nome Completo          | {data.get('companyName')}                      |
| Nome Fantasia          | {data.get('tradeName')}                        |
| Ticker B3              | {data.get('tickerb3')}                         |
| Segmento               | {data.get('segment')}                          |
| Setor                  | {data.get('sector')}                           |
| Documento (CNPJ)       | {data.get('document')}                         |

---

## Resumo

{data.get('summary')}

---

## Cotação Atual

| Indicador              | Valor                                         |
|------------------------|-----------------------------------------------|
| Cotação Atual          | R$ {data.get('actualQuotationPrice')}         |
| Última Cotação do Dia  | R$ {data.get('lastDayQuotation')}             |
| Máxima 52 Semanas      | R$ {data.get('fiftyTwoWeekHigh')}             |
| Mínima 52 Semanas      | R$ {data.get('fiftyTwoWeekLow')}              |
| Valorização Último Mês | {data.get('lastMonthAppreciation'):.2f}%      |
| Valorização Últimos 12 Meses | {data.get('lastTwelveAppreciation'):.2f}% |
| Liquidez Diária        | {data.get('dailyLiquidity')}                   |
| Dividend Yield (DY)    | {data.get('dyPay'):.2f}%                        |

---

## Indicadores Financeiros

| Indicador                   | Valor             |
|-----------------------------|-------------------|
| P/L (Preço/Lucro)           | {data['indicators'].get('pl')}  |
| P/VP (Preço/Valor Patrimonial) | {data['indicators'].get('pvp')} |
| Dividend Yield (%)           | {data['indicators'].get('dividendYield')} |
| EV/EBIT                     | {data['indicators'].get('evebit')} |
| LPA (Lucro por ação)         | {data['indicators'].get('lpa')}  |
| VPA (Valor Patrimonial por ação) | {data['indicators'].get('vpa')}  |
| ROE (Retorno sobre Patrimônio) | {data['indicators'].get('roe')}  |
| Dívida Líquida / Patrimônio Líquido | {data['indicators'].get('liquidOwePl')} |
| ROA (Retorno sobre Ativos)   | {data['indicators'].get('roa')}  |
| CAGR Receita 5 anos          | {data['indicators'].get('cagrFiveYearsRevenue')}% |
| CAGR Lucro 5 anos            | {data['indicators'].get('cagrFiveYearsProfit')}%  |
| Margem EBITDA (%)            | {data['indicators'].get('marginEbitda')}  |
| Margem EBIT (%)              | {data['indicators'].get('marginEbit')}  |
| Margem Líquida (%)           | {data['indicators'].get('liquidMargin')}  |
| Margem Bruta (%)             | {data['indicators'].get('grossMargin')}  |

---

## Perfil da Empresa

| Campo                 | Valor                                    |
|-----------------------|------------------------------------------|
| Endereço              | {data['summaryProfile'].get('address1')}, {data['summaryProfile'].get('address2')} |
| Cidade                | {data['summaryProfile'].get('city')}                   |
| Estado                | {data['summaryProfile'].get('state')}                  |
| País                  | {data['summaryProfile'].get('country')}                |
| Website               | [{data['summaryProfile'].get('website')}]({data['summaryProfile'].get('website')}) |
| Segmento              | {data['summaryProfile'].get('segment')}                |
| Setor                 | {data['summaryProfile'].get('sector')}                 |
| Subsetor              | {data['summaryProfile'].get('subSector')}              |
| Funcionários          | {data['summaryProfile'].get('fullTimeEmployees')}     |
| Ativos Totais         | R$ {data['summaryProfile'].get('totalAssets')}        |
| Patrimônio Líquido    | R$ {data['summaryProfile'].get('totalStockholderEquity')} |
| Dívida Total          | R$ {data['summaryProfile'].get('totalDebt')}           |
| Receita Total         | R$ {data['summaryProfile'].get('totalRevenue')}        |
| Valor de Mercado (Enterprise Value) | R$ {data['summaryProfile'].get('enterpriseValue')} |

---

## Fórmulas de Valoração

| Fórmula                  | Valor              |
|--------------------------|--------------------|
| Fórmula Graham           | R$ {data.get('grahamFormula')} |
| Fórmula Bazin            | R$ {data.get('bazinFormula')}  |

---

## Preço-Alvo (Target Price Formula)

| Campo                  | Valor                  |
|------------------------|------------------------|
| Nome da Valoração      | {data['targetPriceFormula'].get('nameValuation')} |
| Valoração              | R$ {data['targetPriceFormula'].get('valuation')}   |
| Preço Máximo de Compra | R$ {data['targetPriceFormula'].get('maxPurchasePrice')} |
| Preço Alvo             | R$ {data['targetPriceFormula'].get('priceTarget')} |

---

"""
    return md


def generate_price_history_markdown(data: list) -> str:

    md = "| Date | Open | High | Low | Close | Volume | Adjusted Close |\n"
    md += "|------|------|------|-----|-------|--------|----------------|\n"

    for item in data:
        dt = datetime.fromtimestamp(item["date"]).strftime("%Y-%m-%d %H:%M:%S")
        md += (
            f"| {dt} | "
            f"{item['open']:.2f} | "
            f"{item['high']:.2f} | "
            f"{item['low']:.2f} | "
            f"{item['close']:.2f} | "
            f"{item['volume']} | "
            f"{item['adjustedClose']:.2f} |\n"
        )

    md += (
        "\n*Note: All prices are in the original currency and timestamps are in UTC.*\n"
    )
    return md
