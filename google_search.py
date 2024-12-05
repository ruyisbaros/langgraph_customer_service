import os
import pandas as pd
import httpx

GOOGLE_SEARCH_KEY = os.getenv('GOOGLE_SEARCH_KEY')
GOOGLE_SEARCH_ID = os.getenv('GOOGLE_SEARCH_ID')
query = "Python websockets"


def google_search(query, api_key=GOOGLE_SEARCH_KEY, search_engine_id=GOOGLE_SEARCH_ID, **params):
    url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": search_engine_id,
        **params
    }
    response = httpx.get(url, params=params)
    response.raise_for_status()
    return response.json()


def google_search_results(query="", max_results=1):
    search_results = []

    for i in range(max_results):
        response = google_search(query, start=i)
        search_results.extend(response.get('items', []))
    return search_results
