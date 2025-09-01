# News Aggregation Bot

A Python-based bot that aggregates news from multiple sources (CryptoPanic, FRED, LunarCrush, Twitter) and sends summarized updates to a Discord webhook.

## Features

- Fetches news from CryptoPanic, economic data from FRED, social sentiment from LunarCrush, and recent tweets
- Supports both **English and Arabic** news content
- Includes Arabic tweets and news from Al Jazeera
- Processes data into readable summaries with bilingual support
- Sends updates to Discord via webhook
- Handles API rate limits and errors
- Runs continuously with 4-hour updates (safe for API limits)
- Secure API key management using environment variables

## Prerequisites

- Python 3.7+
- API keys for:
  - CryptoPanic
  - FRED (Federal Reserve Economic Data)
  - LunarCrush
  - Twitter API v2 (Bearer token)
- Discord webhook URL

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` and add your actual API keys and Discord webhook URL:
   ```
   CRYPTOPANIC_API_KEY=your_actual_key
   FRED_API_KEY=your_actual_key
   LUNARCRUSH_API_KEY=your_actual_key
   TWITTER_API_KEY=your_bearer_token
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_id/your_webhook_token
   ```

## Security Best Practices

- **Never hardcode API keys** in your source code
- Use environment variables or a secure secrets manager
- Add `.env` to your `.gitignore` file to prevent committing sensitive data
- Regularly rotate your API keys
- Limit webhook permissions to only necessary channels

## Usage

Run the bot:
```bash
python main.py
```

The bot will:
- Fetch data immediately on startup
- Send a summary to Discord
- Continue running and fetch new data every 4 hours

## Configuration

### Rate Limiting
The bot includes a 1-second delay between API requests to respect rate limits. Adjust `RATE_LIMIT_DELAY` in `main.py` if needed.

### Scheduling
Updates are scheduled every hour. Modify the schedule in the `main()` function if you need different intervals.

### Logging
Logs are written to `news_bot.log` and also printed to console. Check logs for errors or debugging information.

## API Details

### CryptoPanic
- Fetches recent crypto news posts
- API: https://cryptopanic.com/api/v3/posts/

### FRED
- Fetches economic indicators (example: unemployment rate)
- API: https://fred.stlouisfed.org/docs/api/fred/

### LunarCrush
- Fetches social media sentiment data
- API: https://lunarcrush.com/developers/docs

### Twitter
- Fetches recent tweets about crypto in both English and Arabic
- Searches for: "crypto" (English) and "عملة OR بيتكوين OR كريبتو" (Arabic)
- API: https://developer.twitter.com/en/docs/twitter-api

### Arabic News (Al Jazeera)
- Fetches Arabic news from Al Jazeera RSS feed
- No API key required
- Provides regional Arabic news content

## Error Handling

The bot includes comprehensive error handling:
- Network request failures
- Invalid API responses
- Missing environment variables
- Rate limit exceeded (with retry logic)

## Customization

You can modify the data processing in the `process_and_summarize()` function to:
- Change which data points are included
- Adjust summary format
- Add more sources

## Troubleshooting

- Check `news_bot.log` for detailed error messages
- Verify all API keys are correctly set in `.env`
- Ensure Discord webhook URL is valid
- Check API rate limits for each service

## License

This project is open source. Use at your own risk.