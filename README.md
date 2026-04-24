# Trip Planner with LangChain & Gemini

AI-powered trip planning tool that helps you choose the best destination and create an itinerary.

## Quick Start

```bash
poetry run python main.py
```

Then answer these prompts:
- **Where are you traveling from?** → `Mangalore`
- **Enter city options (comma separated):** → `Shirdi, Ayodhya, Shimla`
- **Enter trip date range:** → `July 10 - July 20`
- **Enter your travel interests:** → `temples, nature, culture`

## How It Works

The app has **3 AI Agents** that work together:

1. **City Selection Agent** 🏙️
   - Reviews weather, prices, and attractions for each city
   - Recommends the BEST city based on your interests
   - Example: "Shirdi is best for temples in July"
   - **Tools:** Search Internet(picks the top 4 websites in the search and gathers title, link and snippet, this is done through serpapi), Scrape Websites(uses browserless api to scrape). If required info is already found with 'search internet' tool then the AI sees no need in using the other tool provided to it. It uses it as per need.

2. **Local Expert Agent** 🗺️
   - Provides insider tips about the selected city(here it is shirdi)
   - Shares info about attractions, customs, best neighborhoods
   - Example: "Visit Shirdi's temples in early morning, then explore local markets"
   - **Tools:** Search Internet, Scrape Websites

3. **Travel Concierge Agent** 📋
   - Creates a detailed day-by-day itinerary
   - Includes activities, hotels, budget, packing tips, food recommendations
   - Example: "Day 1: Arrive in Shirdi → Visit temples → Local dinner. Budget: $50/day"
   - **Tools:** Search Internet, Scrape Websites, Calculator

## Setup

1. Create `.env` file with your API keys:
```
GOOGLE_API_KEY=your_key_here
SERPER_API_KEY=your_key_here
BROWSERLESS_API_KEY=your_key_here
```

2. Install dependencies:
```bash
poetry install --no-root
```

## Requirements
- Python 3.10+
- Poetry package manager
- Google Gemini API key (use APIKEY of your prefered model provider, refer https://docs.langchain.com/oss/python/langchain/models)
- Serper API key (search)
- Browserless API key (web scraping)
