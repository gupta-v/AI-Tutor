from langchain.tools import Tool
import requests
from bs4 import BeautifulSoup

def scrape_w3schools(url):
    """Scrapes main content from W3Schools"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    main_content = soup.find("div", id="main")
    if not main_content:
        return "Content not found."

    text = []
    for tag in main_content.find_all(["p"]):
        text.append(tag.get_text(strip=True))

    for tag in main_content.find_all("li"):
        text.append(tag.get_text(strip=True))
    
    return "\n".join(text)

def scrape_tutorialspoint(url):
    """Scrapes main content from TutorialsPoint."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    main_content = soup.find("div", id="mainContent")
    if not main_content:
        return "Content not found."

    # Extract text from all <p> tags
    text = [p.get_text(strip=True) for p in main_content.find_all("p")]
    
    return "\n".join(text)

def scrape_freecodecamp(url):
    """Scrapes main content from FreeCodeCamp"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    article = soup.find("article")
    if not article:
        return "Content not found."

    text = [p.get_text(strip=True) for p in article.find_all("p")]
    return "\n".join(text)

def scrape_programiz(url):
    """Scrapes main content from Programiz"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    article = soup.find("article")
    if not article:
        return "Content not found."

    text = [p.get_text(strip=True) for p in article.find_all("p")]
    return "\n".join(text)

def scrape_wikipedia(url):
    """Scrapes main content from Wikipedia"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    content_div = soup.find("div", id="bodyContent")
    if not content_div:
        return "Content not found."

    text = []
    for p in content_div.find_all("p", limit=10):  
        text.append(p.get_text(strip=True))

    return "\n".join(text)

def scrape_url(url):
    """Chooses the appropriate scraper based on URL"""
    if "w3schools.com" in url:
        return scrape_w3schools(url)
    elif "tutorialspoint.com" in url:
        return scrape_tutorialspoint(url)
    elif "freecodecamp.org" in url:
        return scrape_freecodecamp(url)
    elif "programiz.com" in url:
        return scrape_programiz(url)
    elif "wikipedia.org" in url:
        return scrape_wikipedia(url)
    else:
        return "Unsupported site."

# Wrap the function in a LangChain Tool
web_scraper_tool = Tool(
    name="WebScraper",
    func=scrape_url,
    description=(
        "Scrapes the given website URL and returns the main content by extracting and concatenating all text within <p> tags. "
        "Intended for educational websites such as:\n"
        "- W3Schools (https://www.w3schools.com)\n"
        "- TutorialsPoint (https://www.tutorialspoint.com)\n"
        "- JavatPoint (https://www.tpointtech.com)\n"
        "- freeCodeCamp (https://www.freecodecamp.org)\n"
        "- Programiz (https://www.programiz.com)\n\n"
        "Note: Wikipedia (https://en.wikipedia.org) should be used only as a fallback option if no content is found from the above sources."
    )
)