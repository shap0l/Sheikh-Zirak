# Sheikh Zirak — Kurdish AI Chatbot

Sheikh Zirak is a Telegram chatbot designed to communicate in Sorani Kurdish. Powered by Google's Gemini API, it provides conversational responses, religious guidance, and dream interpretations through a culturally tailored personality.

## Features

- **AI-powered conversations:** Integrates Google's Gemini models.
- **Sorani Kurdish:** Designed for Kurdish-speaking users.
- **Conversation memory:** Stores chat history in an SQLite database to provide conversational context.
- **Telegram integration:** Uses Telegram's Bot API through pyTelegramBotAPI.
- **Channel membership verification:** Requires users to join a designated Telegram channel.
- **Spam controls:** Implements message rate limiting and user blocking.
- **Fallback API keys:** Attempts alternative Gemini API credentials when quota limits are reached.
- **Privacy command:** Allows users to request deletion of their stored conversation history with `/forgetme`.
- **Administrative commands:** Includes functionality for managing stored chat history.

## Tech Stack

- Python
- Telegram Bot API
- Google Gemini API (`google-genai`)
- SQLite
- pyTelegramBotAPI

## Installation

1. Clone this repository.
2. Install the dependencies:

   `pip install -r requirements.txt`

3. Configure the required environment variables for your Telegram bot token and Gemini API keys.
4. Run the bot:

   `python bot.py`

## Configuration

Keep all credentials in environment variables. Never commit API keys, bot tokens, private user IDs, or production databases containing user conversations.

## Purpose

This project explores AI integration, conversational memory, database management, Telegram bot development, and automated handling of API quota errors.

## Author

Developed by Shapol.

GitHub: [@shapdl](https://github.com/shapdl)