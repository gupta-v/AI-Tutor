import os
import sys
import webbrowser
from difflib import SequenceMatcher
from serpapi import GoogleSearch
from dotenv import load_dotenv

# Add aiFeatures/python to sys.path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "aiFeatures/python")))
from .web_scraper_tool import scrape_url

load_dotenv()
serp_api_key=os.getenv("SERP_API_KEY")

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

def web_response(query):
    api_key = serp_api_key
    query = query.strip()
    
    best_link = search_best_link(query, api_key)
    if best_link:
        print("Best link found:", best_link)
        webbrowser.open(best_link)
        
        # Scrape the content from the best link
        content = scrape_url(best_link)
        
        # Ensure the output folder exists
        output_folder = "data/scrapings"
        os.makedirs(output_folder, exist_ok=True)

        # Save the scraped content to a file
        output_file = os.path.join(output_folder, "scraped_content.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Scraped content has been stored in '{output_file}'")
                # Read and print the contents of the scraped file
        with open(output_file, "r", encoding="utf-8") as f:
            scraped_contents = f.read()

    else:
        print("No suitable link found for your query.")
    return scraped_contents

def main():
    query = input("Enter your search query: ")
    scraped_text=web_response(query)
    print("\n--- Scraped Content Start ---\n")
    print(scraped_text)
    print("\n--- Scraped Content End ---\n")
    # You can add more processing or analysis of the scraped_text here    
if __name__ == "__main__":
    main()
