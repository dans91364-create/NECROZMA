#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - TELEGRAM NOTIFIER 💎🌟⚡

Asynchronous Telegram Notification System
"Bringing divine messages to mortals in real-time"

Features:
- Non-blocking async notifications
- Lore integration for personality
- Rate limit handling
- Image and document support
- Queue-based message system
"""

import os
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any
from queue import Queue
from threading import Thread
import warnings

warnings.filterwarnings("ignore")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  requests not available. Install with: pip install requests")

from lore import LoreSystem, EventType


# ═══════════════════════════════════════════════════════════════
# 🔧 CONFIGURATION
# ═══════════════════════════════════════════════════════════════

class TelegramConfig:
    """Telegram configuration"""
    
    def __init__(self):
        # Try environment variables first
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        
        # Try config file if env vars not set
        if not self.bot_token or not self.chat_id:
            self._load_from_file()
        
        # API settings
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.rate_limit_delay = 0.05  # 50ms between messages (max 20/sec)
        self.retry_attempts = 3
        self.retry_delay = 1.0
        
        # Feature flags
        self.enabled = bool(self.bot_token and self.chat_id)
        self.parse_mode = "Markdown"  # or "HTML"
        
    def _load_from_file(self):
        """Load config from telegram_config.json if exists"""
        config_file = Path("telegram_config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    self.bot_token = data.get("bot_token", "")
                    self.chat_id = data.get("chat_id", "")
            except Exception as e:
                print(f"⚠️  Failed to load telegram_config.json: {e}")
    
    def is_configured(self) -> bool:
        """Check if Telegram is properly configured"""
        return self.enabled and REQUESTS_AVAILABLE


# ═══════════════════════════════════════════════════════════════
# 📨 TELEGRAM NOTIFIER
# ═══════════════════════════════════════════════════════════════

class TelegramNotifier:
    """
    Asynchronous Telegram notification system
    
    Usage:
        notifier = TelegramNotifier()
        notifier.send_message("NECROZMA", EventType.AWAKENING)
        notifier.send_discovery("Pattern found!", sharpe=2.5)
    """
    
    def __init__(self, config: Optional[TelegramConfig] = None, 
                 lore_enabled: bool = True):
        """
        Initialize Telegram notifier
        
        Args:
            config: TelegramConfig instance (creates default if None)
            lore_enabled: Whether to use lore system for messages
        """
        self.config = config or TelegramConfig()
        self.lore = LoreSystem(enabled=lore_enabled)
        self.enabled = self.config.is_configured()
        
        # Message queue for async sending
        self.message_queue = Queue()
        self.worker_thread = None
        self.running = False
        
        # Rate limiting
        self.last_send_time = 0.0
        
        if self.enabled:
            self._start_worker()
            print(f"✅ Telegram notifier enabled (Chat ID: {self.config.chat_id})")
        else:
            if not REQUESTS_AVAILABLE:
                print("⚠️  Telegram disabled: requests library not installed")
            elif not self.config.bot_token:
                print("⚠️  Telegram disabled: TELEGRAM_BOT_TOKEN not set")
            elif not self.config.chat_id:
                print("⚠️  Telegram disabled: TELEGRAM_CHAT_ID not set")
            else:
                print("⚠️  Telegram disabled: unknown configuration issue")
    
    def _start_worker(self):
        """Start background worker thread for async sending"""
        if not self.enabled:
            return
        
        self.running = True
        self.worker_thread = Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
    
    def _worker_loop(self):
        """Background worker that processes message queue"""
        while self.running:
            try:
                # Get message from queue (blocks with timeout)
                message_data = self.message_queue.get(timeout=1.0)
                
                # Rate limiting
                elapsed = time.time() - self.last_send_time
                if elapsed < self.config.rate_limit_delay:
                    time.sleep(self.config.rate_limit_delay - elapsed)
                
                # Send message
                self._send_message_sync(message_data)
                self.last_send_time = time.time()
                
                # Mark as done
                self.message_queue.task_done()
                
            except Exception as e:
                # Queue timeout or error, continue
                if not isinstance(e, Exception):
                    raise  # Re-raise system exits
                continue
    
    def _send_message_sync(self, message_data: Dict[str, Any]):
        """
        Synchronously send a message to Telegram
        
        Args:
            message_data: Dictionary with message parameters
        """
        if not self.enabled or not REQUESTS_AVAILABLE:
            return
        
        msg_type = message_data.get("type", "text")
        
        for attempt in range(self.config.retry_attempts):
            try:
                if msg_type == "text":
                    self._send_text(message_data)
                elif msg_type == "photo":
                    self._send_photo(message_data)
                elif msg_type == "document":
                    self._send_document(message_data)
                
                return  # Success
                
            except Exception as e:
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay)
                else:
                    print(f"⚠️  Telegram send failed after {self.config.retry_attempts} attempts: {e}")
    
    def _send_text(self, data: Dict[str, Any]):
        """Send text message"""
        url = f"{self.config.api_url}/sendMessage"
        payload = {
            "chat_id": self.config.chat_id,
            "text": data["text"],
            "parse_mode": self.config.parse_mode,
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    
    def _send_photo(self, data: Dict[str, Any]):
        """Send photo message"""
        url = f"{self.config.api_url}/sendPhoto"
        
        with open(data["photo_path"], 'rb') as photo:
            files = {"photo": photo}
            payload = {
                "chat_id": self.config.chat_id,
                "caption": data.get("caption", ""),
                "parse_mode": self.config.parse_mode,
            }
            response = requests.post(url, data=payload, files=files, timeout=30)
            response.raise_for_status()
    
    def _send_document(self, data: Dict[str, Any]):
        """Send document message"""
        url = f"{self.config.api_url}/sendDocument"
        
        with open(data["document_path"], 'rb') as doc:
            files = {"document": doc}
            payload = {
                "chat_id": self.config.chat_id,
                "caption": data.get("caption", ""),
                "parse_mode": self.config.parse_mode,
            }
            response = requests.post(url, data=payload, files=files, timeout=30)
            response.raise_for_status()
    
    def send_message(self, deity_name: str, event_type: EventType, 
                    custom_message: str = None, **kwargs):
        """
        Send a lore-based message
        
        Args:
            deity_name: Deity who speaks (ARCEUS, DIALGA, PALKIA, GIRATINA, NECROZMA)
            event_type: Type of event
            custom_message: Optional custom message (overrides lore)
            **kwargs: Variables for lore formatting
        """
        if not self.enabled:
            return
        
        # Generate message
        if custom_message:
            deity = self.lore.deities.get(deity_name.upper())
            text = f"{deity.emoji} {deity.name}: {custom_message}" if deity else custom_message
        else:
            text = self.lore.speak(deity_name, event_type, **kwargs)
        
        if not text:
            return
        
        # Queue for sending
        self.message_queue.put({
            "type": "text",
            "text": text,
        })
    
    def send_awakening(self):
        """Convenience: Send awakening message"""
        self.send_message("ARCEUS", EventType.AWAKENING)
    
    def send_progress(self, deity: str, progress: float, **kwargs):
        """Convenience: Send progress update"""
        self.send_message(deity, EventType.PROGRESS, progress=progress, **kwargs)
    
    def send_discovery(self, pattern: str, deity: str = "NECROZMA"):
        """Convenience: Send discovery message"""
        self.send_message(deity, EventType.DISCOVERY, pattern=pattern)
    
    def send_light_found(self, strategy: str, score: float):
        """Convenience: Send light found message"""
        self.send_message("NECROZMA", EventType.LIGHT_FOUND, 
                         strategy=strategy, score=score)
    
    def send_top_strategy(self, strategy: str, sharpe: float, rank: int):
        """Convenience: Send top strategy message"""
        self.send_message("NECROZMA", EventType.TOP_STRATEGY,
                         strategy=strategy, sharpe=sharpe, rank=rank)
    
    def send_regime_change(self, old_regime: str, new_regime: str):
        """Convenience: Send regime change message"""
        self.send_message("GIRATINA", EventType.REGIME_CHANGE,
                         old_regime=old_regime, new_regime=new_regime)
    
    def send_warning(self, warning: str, deity: str = "GIRATINA"):
        """Convenience: Send warning message"""
        self.send_message(deity, EventType.WARNING, warning=warning)
    
    def send_milestone(self, milestone: str, deity: str = "ARCEUS", **kwargs):
        """Convenience: Send milestone message"""
        self.send_message(deity, EventType.MILESTONE, milestone=milestone, **kwargs)
    
    def send_completion(self, deity: str = "NECROZMA"):
        """Convenience: Send completion message"""
        self.send_message(deity, EventType.COMPLETION)
    
    def send_system_init(self, python_version: str = None, timestamp: str = None):
        """Convenience: Send system initialization message"""
        from lore import EventType
        self.send_message("ARCEUS", EventType.SYSTEM_INIT,
                         python_version=python_version, timestamp=timestamp)
    
    def send_system_check(self, status: str = "checking", dependencies: list = None):
        """Convenience: Send system check message"""
        from lore import EventType
        deps_str = ", ".join(dependencies) if dependencies else "core dependencies"
        self.send_message("ARCEUS", EventType.SYSTEM_CHECK,
                         status=status, dependencies=deps_str)
    
    def send_data_loading(self, filename: str = None, size_gb: float = None):
        """Convenience: Send data loading start message"""
        from lore import EventType
        self.send_message("NECROZMA", EventType.DATA_LOADING,
                         filename=filename, size_gb=size_gb)
    
    def send_data_loaded(self, rows: int = None, memory_gb: float = None, 
                        load_time: float = None, **kwargs):
        """Convenience: Send data loaded complete message"""
        from lore import EventType
        self.send_message("NECROZMA", EventType.DATA_LOADED,
                         rows=rows, memory_gb=memory_gb, load_time=load_time, **kwargs)
    
    def send_analysis_start(self, num_universes: int = None, num_workers: int = None, **kwargs):
        """Convenience: Send analysis phase start message"""
        from lore import EventType
        self.send_message("NECROZMA", EventType.ANALYSIS_START,
                         num_universes=num_universes, num_workers=num_workers, **kwargs)
    
    def send_universe_progress(self, completed: int, total: int, percentage: float, 
                              power: float = None, **kwargs):
        """Convenience: Send universe processing progress message"""
        from lore import EventType
        self.send_message("NECROZMA", EventType.UNIVERSE_PROGRESS,
                         completed=completed, total=total, percentage=percentage,
                         power=power, **kwargs)
    
    def send_photo(self, photo_path: str, caption: str = ""):
        """
        Send a photo
        
        Args:
            photo_path: Path to image file
            caption: Optional caption
        """
        if not self.enabled:
            return
        
        if not Path(photo_path).exists():
            print(f"⚠️  Photo not found: {photo_path}")
            return
        
        self.message_queue.put({
            "type": "photo",
            "photo_path": photo_path,
            "caption": caption,
        })
    
    def send_document(self, document_path: str, caption: str = ""):
        """
        Send a document
        
        Args:
            document_path: Path to document file
            caption: Optional caption
        """
        if not self.enabled:
            return
        
        if not Path(document_path).exists():
            print(f"⚠️  Document not found: {document_path}")
            return
        
        self.message_queue.put({
            "type": "document",
            "document_path": document_path,
            "caption": caption,
        })
    
    def wait_for_queue(self, timeout: Optional[float] = None):
        """
        Wait for all queued messages to be sent
        
        Args:
            timeout: Maximum time to wait in seconds (None = wait forever)
        """
        if not self.enabled:
            return
        
        if timeout:
            start_time = time.time()
            while not self.message_queue.empty():
                if time.time() - start_time > timeout:
                    break
                time.sleep(0.1)
        else:
            self.message_queue.join()
    
    def shutdown(self):
        """Shutdown the notifier gracefully"""
        if not self.enabled:
            return
        
        # Wait for queue to empty
        self.wait_for_queue(timeout=10.0)
        
        # Stop worker
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)


# ═══════════════════════════════════════════════════════════════
# 🧪 TESTING
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║           📱 TELEGRAM NOTIFIER TEST 📱                       ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Create notifier
    notifier = TelegramNotifier()
    
    print(f"\nTelegram enabled: {notifier.enabled}")
    print(f"Bot token configured: {bool(notifier.config.bot_token)}")
    print(f"Chat ID configured: {bool(notifier.config.chat_id)}")
    
    if notifier.enabled:
        print("\n📤 Sending test messages...\n")
        
        # Test messages
        notifier.send_awakening()
        time.sleep(0.5)
        
        notifier.send_progress("DIALGA", progress=50, timeframe="5m")
        time.sleep(0.5)
        
        notifier.send_discovery("Golden Cross Pattern")
        time.sleep(0.5)
        
        notifier.send_light_found("TrendFollower", score=95)
        time.sleep(0.5)
        
        notifier.send_top_strategy("MeanReversion", sharpe=2.5, rank=1)
        time.sleep(0.5)
        
        notifier.send_completion()
        
        # Wait for all messages to send
        print("⏳ Waiting for messages to send...")
        notifier.wait_for_queue()
        
        print("✅ Test messages sent!")
        
        notifier.shutdown()
    else:
        print("""
⚠️  Telegram is not configured.

To enable Telegram notifications, set environment variables:
    export TELEGRAM_BOT_TOKEN="your_bot_token"
    export TELEGRAM_CHAT_ID="your_chat_id"

Or create a telegram_config.json file:
    {
        "bot_token": "your_bot_token",
        "chat_id": "your_chat_id"
    }

To get a bot token:
    1. Message @BotFather on Telegram
    2. Send /newbot and follow instructions
    3. Copy the token provided

To get your chat ID:
    1. Message @userinfobot on Telegram
    2. Copy the ID it sends you
        """)
    
    print("\n✅ Test complete!")
