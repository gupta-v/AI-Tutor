import os
from difflib import SequenceMatcher
from serpapi import GoogleSearch
from web_scraper_tool import scrape_url
import webbrowser

# List of allowed websites
ALLOWED_SITES = [
    "en.wikipedia.org",
    "w3schools.com",
    "tpointtech.com",  
    "tutorialspoint.com",
    "freecodecamp.org",
    "programiz.com"
]

def similar(a, b):
    """Return a similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def search_best_link(query, api_key):
    """
    Use SerpAPI to search Google with a query restricted to allowed websites.
    From the organic results, take the first three allowed results (in order)
    and select the one with the highest title similarity to the query.
    """
    # Construct a site filter string using Google operator "site:"
    site_filter = " OR ".join([f"site:{site}" for site in ALLOWED_SITES])
    params = {
        "engine": "google",
        "q": f"{query} {site_filter}",
        "num": 20,  # Fetch more results to have a larger pool
        "api_key": api_key
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    organic_results = results.get("organic_results", [])
    if not organic_results:
        return None

    # Filter results to only those from allowed sites (in their given order)
    allowed_results = []
    for result in organic_results:
        link = result.get("link", "")
        if any(site in link for site in ALLOWED_SITES):
            allowed_results.append(result)
        if len(allowed_results) >= 3:
            break

    if not allowed_results:
        return None

    # Compare the first three allowed results using title similarity
    best_link = None
    best_score = 0
    for result in allowed_results:
        link = result.get("link", "")
        title = result.get("title", "")
        score = similar(query, title)
        if score > best_score:
            best_score = score
            best_link = link

    return best_link

def main():
    # Set your SerpAPI key here:
    serp_api_key = "YOUR_API_KEY"
    query = input("Enter your search query: ").strip()
    
    best_link = search_best_link(query, serp_api_key)
    if best_link:
        print("Best link found:", best_link)
        webbrowser.open(best_link)  
        # Scrape the content from the best link
        content = scrape_url(best_link)
        # Save the scraped content to a file
        output_file = "scraped_content.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Scraped content has been stored in '{output_file}'")
    else:
        print("No suitable link found for your query.")

if __name__ == "__main__":
    main()
