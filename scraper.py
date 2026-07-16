import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# Headers to prevent getting blocked by public APIs
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=en"
}

def get_latest_hkex_filings():
    """Queries the free, public HKEX document API directly."""
    url = "https://www1.hkexnews.hk/search/titleSearchServlet.do"
    
    # Payload targeting New Listing / IPO Application Proofs
    payload = {
        "lang": "EN",
        "category": "0",
        "market": "SEHK",
        "searchType": "1",
        "t1code": "40000",  # New Listings Category
        "t2code": "40100",  # Application Proofs / PHIPs
        "from": datetime.today().strftime('%Y%m%d'),
        "to": datetime.today().strftime('%Y%m%d')
    }
    
    try:
        response = requests.post(url, data=payload, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json().get("docList", [])
    except Exception as e:
        print(f"Error querying HKEX API: {e}")
    return []

def get_aastocks_ipo_details(symbol):
    """
    Parses AAStocks' public detail page to pull Sponsor names,
    estimated IPO size, and target market cap.
    """
    url = f"http://www.aastocks.com/en/stocks/market/ipo/upcomingipo/company-info?symbol={symbol}"
    try:
        # Pass a standard browser User-Agent
        res = requests.get(url, headers={"User-Agent": HEADERS["User-Agent"]}, timeout=10)
        if res.status_code != 200:
            return {}
            
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Scrape and clean basic targets from table elements
        # Note: AAStocks' layout maps details to specific class tags
        data = {
            "sponsor": soup.find(text="Sponsor").find_next('td').text.strip() if soup.find(text="Sponsor") else "N/A",
            "ipo_size": soup.find(text="Offer Size").find_next('td').text.strip() if soup.find(text="Offer Size") else "N/A",
            "market_cap": soup.find(text="Market Cap").find_next('td').text.strip() if soup.find(text="Market Cap") else "N/A"
        }
        return data
    except Exception:
        return {"sponsor": "N/A", "ipo_size": "N/A", "market_cap": "N/A"}

def query_yahoo_market_cap(stock_code):
    """Queries Yahoo Finance's open endpoint for verified existing Market Cap."""
    ticker = f"{stock_code.zfill(5)}.HK"
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker}"
    try:
        res = requests.get(url, headers={"User-Agent": HEADERS["User-Agent"]}, timeout=10)
        if res.status_code == 200:
            data = res.json()
            quote = data['quoteResponse']['result'][0]
            return quote.get("marketCap", "N/A")
    except Exception:
        pass
    return "N/A"

def main():
    filings = get_latest_hkex_filings()
    consolidated_data = []

    for item in filings:
        stock_code = item.get("stockCode", "").strip()
        
        # Pull baseline properties from official HKEX response
        issuer_eng = item.get("stockName", "").strip()
        issuer_chi = item.get("stockNameChi", "").strip()
        filing_date = item.get("releaseDate", "")
        
        # Enforce cross-checks using alternative free endpoints
        aastocks_data = get_aastocks_ipo_details(stock_code) if stock_code else {}
        yahoo_cap = query_yahoo_market_cap(stock_code) if stock_code else "N/A"
        
        entry = {
            "filing_date": filing_date,
            "stock_code": stock_code,
            "issuer_name_eng": issuer_eng,
            "issuer_name_chi": issuer_chi,
            "sponsor_name": aastocks_data.get("sponsor", "N/A"),
            "ipo_size_estimate": aastocks_data.get("ipo_size", "N/A"),
            "existing_market_cap_yahoo": yahoo_cap,
            "market_cap_estimate_aastocks": aastocks_data.get("market_cap", "N/A")
        }
        consolidated_data.append(entry)
        
    # Write directly to the repository as raw JSON
    with open("ipo_scan_results.json", "w", encoding="utf-8") as f:
        json.dump(consolidated_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
