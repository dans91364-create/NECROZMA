# Enhanced Telegram Notifications for NECROZMA

## Overview

NECROZMA now provides real-time Telegram notifications from the very beginning of execution, giving users complete visibility into the analysis process.

## Features

### Early-Stage Notifications

1. **System Initialization** 🌟
   - Sent immediately after the Ultra Necrozma banner
   - Includes Python version and timestamp
   - Confirms system is starting up

2. **System Check** 🔍
   - Sent during dependency verification
   - Reports pass/fail status
   - Lists verified dependencies

3. **Data Loading Start** 💎
   - Sent before loading data
   - Shows filename and file size
   - Indicates temporal shift is beginning

4. **Data Loaded Complete** ✅
   - Sent after successful data load
   - Comprehensive statistics:
     - Row count
     - Memory usage
     - Load time and speed
     - Date range
     - Price range

5. **Analysis Phase Start** ⚡
   - Sent at the beginning of universe processing
   - Shows number of universes to process
   - Displays worker count
   - Confirms light is piercing dimensions

6. **Universe Progress Updates** 📊
   - Sent every 5 universes or 20% progress
   - Real-time progress percentage
   - Universes completed/total
   - Patterns found count
   - Current evolution stage
   - Light power percentage
   - Estimated time remaining

## Usage

### Enable Telegram Notifications

By default, Telegram notifications are **enabled**. To use them:

1. Set environment variables:
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
```

2. Or create a `telegram_config.json` file:
```json
{
  "bot_token": "your_bot_token_here",
  "chat_id": "your_chat_id_here"
}
```

3. Run NECROZMA normally:
```bash
python main.py
```

### Disable Telegram Notifications

To disable Telegram notifications, use the `--skip-telegram` flag:

```bash
python main.py --skip-telegram
```

### Getting Telegram Credentials

#### Bot Token
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Copy the bot token provided

#### Chat ID
1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Copy the ID it sends you

## Message Format

All messages follow the NECROZMA theme with deity-specific formatting:

- **ARCEUS** (⚪) - System initialization and checks
- **NECROZMA** (🌟) - Data and analysis events
- **DIALGA** (🔵) - Time-related progress
- **PALKIA** (🟣) - Spatial analysis
- **GIRATINA** (⚫) - Warnings and errors

### Example Messages

#### System Initialization
```
🌟 ULTRA NECROZMA AWAKENING 🌟

⚡ System initializing...
🐍 Python 3.12.3
📅 2026-01-11 04:43:45

The Blinding One prepares to analyze the markets...
```

#### System Check (Pass)
```
🔍 SYSTEM CHECK COMPLETE

✅ All dependencies verified
⚙️ NumPy, Pandas, PyArrow, SciPy ready
💎 Prismatic cores online

Status: PASS
```

#### Data Loaded Successfully
```
✅ CRYSTAL LOADED SUCCESSFULLY

📊 Rows: 1,234,567
💾 Memory: 2.45 GB
⏱️ Time: 3.21s
⚡ Speed: 384,567 rows/sec

Period: 2024-01-01 → 2024-12-31
Price Range: 1.08450 - 1.12340
```

#### Analysis Progress
```
📊 ANALYSIS PROGRESS: 40%

🌌 Universes processed: 10/25
🎯 Patterns found: 5,432
⚡ Evolution: Dawn Wings
💎 Light Power: 40%

2.5 minutes estimated remaining...
```

## Error Handling

The notification system is designed to be **non-blocking** and **fault-tolerant**:

- **Missing Credentials**: Shows a single warning, continues execution
- **Network Errors**: Logs warning, doesn't crash the application
- **Invalid Configuration**: Gracefully degrades to disabled state
- **Telegram API Failures**: Retries up to 3 times, then continues

All Telegram operations are wrapped in try/except blocks to ensure the main analysis continues uninterrupted.

## Technical Details

### Architecture

1. **LoreSystem** (`lore.py`)
   - Manages event broadcasting
   - Routes events to appropriate deities
   - Integrates with TelegramNotifier

2. **TelegramNotifier** (`telegram_notifier.py`)
   - Handles asynchronous message sending
   - Implements rate limiting (20 messages/second)
   - Manages message queue with background worker thread
   - Lazy initialization to avoid circular imports

3. **Event Types** (New)
   - `SYSTEM_INIT` - System initialization
   - `SYSTEM_CHECK` - Dependency verification
   - `DATA_LOADING` - Data loading start
   - `DATA_LOADED` - Data loading complete
   - `ANALYSIS_START` - Analysis phase start
   - `UNIVERSE_PROGRESS` - Universe processing progress

### Integration Points

Notifications are integrated at these locations:

1. **main.py**
   - After banner display (SYSTEM_INIT)
   - During system check (SYSTEM_CHECK)
   - Before/after data loading (DATA_LOADING, DATA_LOADED)
   - At analysis phase start (ANALYSIS_START)

2. **analyzer.py**
   - During universe processing (UNIVERSE_PROGRESS)
   - In both sequential and parallel processing modes
   - Every 5 universes or 20% progress milestones

### Rate Limiting

- Maximum 20 messages per second
- 50ms delay between messages
- Up to 3 retry attempts on failures
- 1 second delay between retries

## Testing

The notification system includes comprehensive tests:

```bash
# Run all tests
python -m pytest tests/

# Run notification tests specifically
python -m pytest tests/test_telegram_notifications.py -v

# Manual test
python tests/test_telegram_notifications.py
```

All 28 tests pass:
- 23 existing feature tests
- 5 new notification tests

## Troubleshooting

### No notifications received

1. Check credentials are set correctly
2. Verify bot token is valid
3. Ensure chat ID is correct
4. Check bot has been started (send `/start` to your bot)
5. Look for warning messages in console output

### Too many notifications

Progress notifications are sent every 5 universes or 20% progress. This is by design to provide real-time visibility without overwhelming the user.

### Notifications arrive late

Notifications are sent asynchronously with rate limiting. There may be a small delay (< 1 second) between event and notification due to:
- Message queue processing
- Rate limiting delays
- Network latency

## Future Enhancements

Potential improvements for future versions:

- Configurable notification frequency
- Notification templates customization
- Support for multiple chat IDs
- Rich media attachments (charts, plots)
- Interactive buttons for pause/resume
- Notification priority levels
- Alternative notification channels (Discord, Slack, email)

## License

Same as NECROZMA project license.
