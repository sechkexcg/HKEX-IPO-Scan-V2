import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=en"
}

def test_hkex_api():
    print("--- Testing HKEX News Search Servlet API ---")
    url = "https://www1.hkexnews.hk/search/titleSearchServlet.do"
    
    # Query the last 7 days to ensure we get historical testing records
    date_to = datetime.today()
    date_from = date_to - timedelta(days=7)
    
    payload = {
        "lang": "EN",
        "category": "0",
        "market": "SEHK",
        "searchType": "1",
        "t1code": "40000",  # New Listings / IPO category
        "t2code": "40100",  # Application Proofs / PHIPs
        "from": date_from.strftime('%Y%m%d'),
        "to": date_to.strftime('%Y%m%d')
    }
    
    try:
        response = requests.post(url, data=payload, headers=HEADERS, timeout=10)
        print(f"HKEX Response Status: {response.status_code}")
        
        if response.status_code == 200:
            doc_list = response.json().get("docList", [])
            print(f"Successfully found {len(doc_list)} IPO filings in the last 7 days.\n")
            
            # Print the first item to inspect the payload structure
            if doc_list:
                sample = doc_list[0]
                print("--- SAMPLE METADATA ---")
                print(f"Filing Date:   {sample.get('releaseTime') or sample.get('releaseDate')}")
                print(f"Stock Code:    {sample.get('stockCode')}")
                print(f"English Name:  {sample.get('stockName')}")
                print(f"Chinese Name:  {sample.get('stockNameChi')}")
                print(f"Sponsor:       {sample.get('sponsorName', 'None')}")
                print(f"Doc Title:     {sample.get('title')}")
                print("-" * 23)
            return doc_list
        else:
            print("Failed to fetch. Headers might need tweaking or endpoint is down.")
    except Exception as e:
        print(f"Error occurred: {e}")
    return []

if __name__ == "__main__":
    test_hkex_api()
