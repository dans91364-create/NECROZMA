# Telegram Notifications Setup Guide

## Overview

NECROZMA now supports comprehensive Telegram notifications throughout the analysis process. This allows you to monitor long-running analyses remotely via Telegram messages.

## Setup Instructions

### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the prompts to:
   - Choose a name for your bot (e.g., "NECROZMA Analyzer")
   - Choose a username for your bot (e.g., "necrozma_analyzer_bot")
4. BotFather will give you a **Bot Token** - save this for later

### 2. Get Your Chat ID

1. Send a message to your new bot (any message)
2. Visit this URL in your browser (replace `YOUR_BOT_TOKEN` with your actual token):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
3. Look for the `"chat":{"id":` field in the JSON response
4. Save this **Chat ID** number for later

### 3. Set Environment Variables

#### On Linux/Mac:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
```

To make these permanent, add them to your `~/.bashrc` or `~/.zshrc`:

```bash
echo 'export TELEGRAM_BOT_TOKEN="your_bot_token_here"' >> ~/.bashrc
echo 'export TELEGRAM_CHAT_ID="your_chat_id_here"' >> ~/.bashrc
source ~/.bashrc
```

#### On Windows (PowerShell):

```powershell
$env:TELEGRAM_BOT_TOKEN="your_bot_token_here"
$env:TELEGRAM_CHAT_ID="your_chat_id_here"
```

To make these permanent on Windows:
1. Search for "Environment Variables" in Windows
2. Click "Edit the system environment variables"
3. Click "Environment Variables" button
4. Add new User variables:
   - `TELEGRAM_BOT_TOKEN` = your bot token
   - `TELEGRAM_CHAT_ID` = your chat ID

### 4. Test the Setup

Run NECROZMA with a simple test:

```bash
python main.py --test --sequential
```

You should receive Telegram notifications for:
- 🌟 System Initialization
- 🔍 System Check
- 📊 Data Loading
- ✅ Data Loaded
- ⚡ Analysis Phase Start
- 📊 Universe Progress (every 5 universes)

## Notification Types

### System Initialization
Sent when NECROZMA starts, includes Python version and timestamp.

### System Check
Sent during dependency verification.

### Data Loading
Sent before loading data files, includes filename and file size.

### Data Loaded Successfully
Comprehensive notification after data load with:
- Row count and memory usage
- Load time and processing speed
- Date range and price range

### Analysis Phase Start
Sent when analysis begins, includes:
- Number of universes to process
- Worker count
- Evolution stages

### Universe Progress
Sent every 5 universes (or at 20% intervals), includes:
- Completion percentage
- Universes processed
- Total patterns found
- Current evolution stage and power level

## Disabling Notifications

To run NECROZMA without Telegram notifications:

```bash
python main.py --skip-telegram
```

This is useful for:
- Testing locally
- Running in CI/CD pipelines
- When you don't have Telegram credentials configured

## Troubleshooting

### "Telegram credentials not found in environment"

This warning means the environment variables are not set. Either:
1. Set the environment variables as described above
2. Run with `--skip-telegram` flag

### "Failed to send Telegram message"

Possible causes:
1. Invalid bot token or chat ID
2. Bot has been blocked or deleted
3. Network connectivity issues
4. Rate limiting (too many messages sent)

The program will continue running even if Telegram fails - notifications are non-blocking.

### No messages received

1. Verify your bot token and chat ID are correct
2. Make sure you've sent at least one message to your bot
3. Check that your bot hasn't been blocked
4. Verify environment variables are set correctly:
   ```bash
   echo $TELEGRAM_BOT_TOKEN
   echo $TELEGRAM_CHAT_ID
   ```

## Security Notes

⚠️ **Never commit your bot token or chat ID to git!**

- Use environment variables only
- Add `.env` files to `.gitignore` if you use them
- Consider using a secrets manager for production deployments

## Message Format

All messages use HTML formatting for better readability:
- **Bold** for headers
- `Monospace` for values
- *Italic* for status messages
- Emoji for visual categorization

## Example Notification Flow

```
🌟 ULTRA NECROZMA AWAKENING 🌟
⚡ System initializing...
🐍 Python 3.12.3
📅 2026-01-11 04:49:25

🔍 SYSTEM CHECK IN PROGRESS
✅ Verifying dependencies...
⚙️ NumPy, Pandas, PyArrow, SciPy
💎 Preparing prismatic cores...

💎 CRYSTAL LOADING INITIATED
📊 Dataset: EURUSD_2025.csv
💾 Size: 1.23 GB
⏱️ Loading in progress...

✅ CRYSTAL LOADED SUCCESSFULLY
📊 Rows: 1,234,567
💾 Memory: 0.85 GB
⏱️ Time: 12.3s
⚡ Speed: 100,372 rows/sec

⚡ ANALYSIS PHASE INITIATED
🌌 Universes to process: 25
⚡ Workers: 16
💎 Evolution stages: 5

📊 ANALYSIS PROGRESS: 20%
🌌 Universes processed: 5/25
🎯 Patterns found: 1,234
⚡ Evolution: Dusk Mane
💎 Light Power: 25.0%

... (more progress updates)

📊 ANALYSIS PROGRESS: 100%
🌌 Universes processed: 25/25
🎯 Patterns found: 8,456
⚡ Evolution: Ultra Necrozma
💎 Light Power: 100.0%
```

## Advanced Configuration

Currently, notifications are sent at predefined points. Future enhancements could include:
- Configurable notification frequency
- Custom notification templates
- Multiple notification channels
- Alert levels (info, warning, error)
- Digest mode (single summary message instead of multiple)

## Support

If you encounter issues with Telegram notifications:
1. Check the troubleshooting section above
2. Verify your environment variables
3. Test with `--skip-telegram` to isolate Telegram issues
4. Check the console output for warning messages
