#!/usr/bin/env python3
"""
News Aggregation Bot
Aggregates news from CryptoPanic, FRED, LunarCrush, and Twitter APIs,
processes into summaries, and sends to Discord webhook.
"""

import os
import time
import logging
from datetime import datetime
import requests
from dotenv import load_dotenv
import schedule

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_bot.log'),
        logging.StreamHandler()
    ]
)

# API Keys from environment variables
CRYPTOPANIC_API_KEY = os.getenv('CRYPTOPANIC_API_KEY')
FRED_API_KEY = os.getenv('FRED_API_KEY')
LUNARCRUSH_API_KEY = os.getenv('LUNARCRUSH_API_KEY')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# Rate limiting settings (adjust based on API limits)
RATE_LIMIT_DELAY = 1  # seconds between requests

def fetch_cryptopanic_news():
    """Fetch news from CryptoPanic API."""
    # Try English first
    url_en = f"https://cryptopanic.com/api/developer/v2/posts/?auth_token={CRYPTOPANIC_API_KEY}&public=true"
    # Try with language filter for broader coverage
    url_all = f"https://cryptopanic.com/api/developer/v2/posts/?auth_token={CRYPTOPANIC_API_KEY}&public=true&filter=hot"

    try:
        # Try English/crypto news first
        response = requests.get(url_en)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching CryptoPanic news: {e}")
        return None

def fetch_fred_data():
    """Fetch economic data from FRED API."""
    # Example: Fetch unemployment rate
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=UNRATE&api_key={FRED_API_KEY}&file_type=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching FRED data: {e}")
        return None

def fetch_lunarcrush_data():
    """Fetch social sentiment data from LunarCrush API."""
    url = f"https://api.lunarcrush.com/v1/feeds?key={LUNARCRUSH_API_KEY}&limit=10"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching LunarCrush data: {e}")
        return None

def fetch_arabic_news():
    """Fetch Arabic news from Al Jazeera or similar sources."""
    try:
        # Using Al Jazeera Arabic RSS feed (no API key required)
        url = "https://www.aljazeera.net/rss/RssFeeds?Url=home"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Parse RSS feed
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)

        news_items = []
        for item in root.findall('.//item')[:3]:  # Get first 3 items
            title = item.find('title').text if item.find('title') is not None else "No title"
            description = item.find('description').text if item.find('description') is not None else ""
            # Extract first 100 characters of description
            if description:
                description = description[:100] + "..." if len(description) > 100 else description
            news_items.append({"title": title, "description": description})

        return {"arabic_news": news_items} if news_items else None

    except Exception as e:
        logging.error(f"Error fetching Arabic news: {e}")
        return None

def fetch_twitter_data():
    """Fetch tweets using Twitter API v2."""
    # Note: Twitter API v2 requires Bearer token, adjust accordingly
    headers = {"Authorization": f"Bearer {TWITTER_API_KEY}"}

    # Fetch both English and Arabic crypto tweets
    tweets_data = {"english": [], "arabic": []}

    # English crypto tweets
    try:
        url_en = "https://api.twitter.com/2/tweets/search/recent?query=crypto&max_results=5&lang=en"
        response = requests.get(url_en, headers=headers)
        response.raise_for_status()
        tweets_data["english"] = response.json().get("data", [])
    except requests.RequestException as e:
        logging.error(f"Error fetching English Twitter data: {e}")

    # Arabic crypto tweets
    try:
        url_ar = "https://api.twitter.com/2/tweets/search/recent?query=عملة OR بيتكوين OR كريبتو&max_results=5&lang=ar"
        response = requests.get(url_ar, headers=headers)
        response.raise_for_status()
        tweets_data["arabic"] = response.json().get("data", [])
    except requests.RequestException as e:
        logging.error(f"Error fetching Arabic Twitter data: {e}")

    return tweets_data if tweets_data["english"] or tweets_data["arabic"] else None

def process_and_summarize(data_sources):
    """Process fetched data and create a summary."""
    summary = f"**News Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}**\n\n"

    # Process CryptoPanic
    if data_sources['cryptopanic']:
        posts = data_sources['cryptopanic'].get('results', [])
        summary += "**CryptoPanic News:**\n"
        for post in posts[:5]:  # Limit to 5 posts
            summary += f"- {post.get('title', 'No title')}\n"
        summary += "\n"

    # Process FRED
    if data_sources['fred']:
        observations = data_sources['fred'].get('observations', [])
        if observations:
            latest = observations[-1]
            summary += f"**FRED Economic Data:**\n- Unemployment Rate: {latest.get('value', 'N/A')}%\n\n"

    # Process LunarCrush
    if data_sources['lunarcrush']:
        feeds = data_sources['lunarcrush'].get('data', [])
        summary += "**LunarCrush Sentiment:**\n"
        for feed in feeds[:3]:
            summary += f"- {feed.get('title', 'No title')}\n"
        summary += "\n"

    # Process Twitter (English and Arabic)
    if data_sources['twitter']:
        summary += "**Recent Crypto Tweets:**\n"

        # English tweets
        if data_sources['twitter'].get('english'):
            summary += "*English:*\n"
            for tweet in data_sources['twitter']['english'][:2]:
                summary += f"- {tweet.get('text', 'No text')[:80]}...\n"

        # Arabic tweets
        if data_sources['twitter'].get('arabic'):
            summary += "*العربية (Arabic):*\n"
            for tweet in data_sources['twitter']['arabic'][:2]:
                summary += f"- {tweet.get('text', 'No text')[:80]}...\n"

        summary += "\n"

    # Process Arabic News
    if data_sources['arabic_news'] and data_sources['arabic_news'].get('arabic_news'):
        summary += "**الأخبار العربية (Arabic News):**\n"
        for news in data_sources['arabic_news']['arabic_news'][:2]:
            summary += f"- **{news.get('title', 'No title')}**\n"
            if news.get('description'):
                summary += f"  {news['description']}\n"
        summary += "\n"

    return summary

def send_to_discord(message):
    """Send message to Discord webhook."""
    data = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        response.raise_for_status()
        logging.info("Message sent to Discord successfully")
    except requests.RequestException as e:
        logging.error(f"Error sending to Discord: {e}")

def fetch_all_data():
    """Fetch data from all sources with rate limiting."""
    data = {}
    sources = [
        ('cryptopanic', fetch_cryptopanic_news),
        ('fred', fetch_fred_data),
        ('lunarcrush', fetch_lunarcrush_data),
        ('twitter', fetch_twitter_data),
        ('arabic_news', fetch_arabic_news)
    ]

    for name, func in sources:
        logging.info(f"Fetching data from {name}")
        data[name] = func()
        time.sleep(RATE_LIMIT_DELAY)  # Rate limiting

    return data

def main():
    """Main function to run the news aggregation bot."""
    logging.info("Starting News Aggregation Bot")

    # Check if all required environment variables are set
    required_vars = [CRYPTOPANIC_API_KEY, FRED_API_KEY, LUNARCRUSH_API_KEY, TWITTER_API_KEY, DISCORD_WEBHOOK_URL]
    if not all(required_vars):
        logging.error("Missing required environment variables. Please check your .env file.")
        return

    # Schedule the job to run every 4 hours (6 times per day - very safe for API rate limits)
    schedule.every(4).hours.do(lambda: run_news_fetch())

    # Run immediately on start
    run_news_fetch()

    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def run_news_fetch():
    """Fetch news, process, and send to Discord."""
    try:
        data = fetch_all_data()
        summary = process_and_summarize(data)
        send_to_discord(summary)
    except Exception as e:
        logging.error(f"Error in news fetch cycle: {e}")

if __name__ == "__main__":
    main()