#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 NECROZMA - LORE & MYTHOLOGY SYSTEM 💎🌟⚡

The Deities of Market Analysis
"Where ancient powers meet modern algorithms"

The Five Deities:
- ARCEUS   - The Alpha (Genesis & Synthesis)
- DIALGA   - Time Lord (Temporal Features)
- PALKIA   - Space Lord (Spatial Features)  
- GIRATINA - Chaos Lord (Entropy & Anomalies)
- NECROZMA - Light Devourer (Final Synthesis)
"""

from enum import Enum
from typing import Dict, List
import random
import os


# ═══════════════════════════════════════════════════════════════
# 🌟 EVENT TYPES
# ═══════════════════════════════════════════════════════════════

class EventType(Enum):
    """Types of events that can occur during analysis"""
    AWAKENING = "awakening"                   # System startup
    SYSTEM_INIT = "system_init"               # System initialization
    SYSTEM_CHECK = "system_check"             # System dependency check
    DATA_LOADING = "data_loading"             # Data loading started
    DATA_LOADED = "data_loaded"               # Data loaded successfully
    ANALYSIS_START = "analysis_start"         # Analysis phase started
    UNIVERSE_PROGRESS = "universe_progress"   # Universe processing progress
    PROGRESS = "progress"                     # General progress update
    DISCOVERY = "discovery"                   # Pattern/insight discovered
    DISCOVERY_START = "discovery_start"       # Discovery process started
    LABELING_COMPLETE = "labeling_complete"   # Labeling completed
    REGIME_DETECTION = "regime_detection"     # Regime detection completed
    FEATURE_ENGINEERING = "feature_engineering"  # Feature engineering completed
    OPTIMIZATION_COMPLETE = "optimization_complete"  # Optimization completed
    FINAL_REPORT = "final_report"             # Final report generated
    LIGHT_FOUND = "light_found"               # Major breakthrough
    TOP_STRATEGY = "top_strategy"             # Top strategy found
    WARNING = "warning"                       # Issue or concern
    REGIME_CHANGE = "regime_change"           # Market regime transition
    MILESTONE = "milestone"                   # Major checkpoint reached
    INSIGHT = "insight"                       # Analytical insight
    COMPLETION = "completion"                 # Task completed
    ERROR = "error"                           # Error occurred
    HEARTBEAT = "heartbeat"                   # Periodic status update


# ═══════════════════════════════════════════════════════════════
# 🎭 DEITY DEFINITIONS
# ═══════════════════════════════════════════════════════════════

class Deity:
    """Base class for a deity"""
    
    def __init__(self, name: str, title: str, emoji: str, domain: str, color: str):
        self.name = name
        self.title = title
        self.emoji = emoji
        self.domain = domain
        self.color = color
        self.quotes: Dict[EventType, List[str]] = {}
    
    def speak(self, event_type: EventType, **kwargs) -> str:
        """
        Get a deity's quote for a specific event type
        
        Args:
            event_type: Type of event
            **kwargs: Variables for string formatting
            
        Returns:
            Formatted quote string
        """
        if event_type not in self.quotes or not self.quotes[event_type]:
            return f"{self.emoji} {self.name}: Processing..."
        
        quote = random.choice(self.quotes[event_type])
        
        try:
            return quote.format(**kwargs)
        except KeyError:
            return quote


# ═══════════════════════════════════════════════════════════════
# ⚡ ARCEUS - The Original One
# ═══════════════════════════════════════════════════════════════

ARCEUS = Deity(
    name="ARCEUS",
    title="The Original One - Alpha of All",
    emoji="⚪",
    domain="Genesis & Synthesis",
    color="#F0F0F0"
)

ARCEUS.quotes = {
    EventType.AWAKENING: [
        "⚪ ARCEUS: From the void, I shape reality. The analysis begins...",
        "⚪ ARCEUS: The Alpha awakens. Let creation commence.",
        "⚪ ARCEUS: Reality bends to my will. Initiating genesis protocol...",
    ],
    EventType.MILESTONE: [
        "⚪ ARCEUS: Another dimension conquered. {progress}% complete.",
        "⚪ ARCEUS: The cosmos aligns. Phase {phase} achieved.",
        "⚪ ARCEUS: My judgment crystallizes. {milestone} reached.",
    ],
    EventType.COMPLETION: [
        "⚪ ARCEUS: The cycle completes. All has been judged.",
        "⚪ ARCEUS: Genesis and terminus unite. The work is done.",
        "⚪ ARCEUS: From alpha to omega, the truth is revealed.",
    ],
    EventType.ERROR: [
        "⚪ ARCEUS: Even gods face trials. Adapting to {error}...",
        "⚪ ARCEUS: A disturbance in reality. Correcting {error}...",
    ],
}


# ═══════════════════════════════════════════════════════════════
# 🔵 DIALGA - Temporal Pokemon
# ═══════════════════════════════════════════════════════════════

DIALGA = Deity(
    name="DIALGA",
    title="Lord of Time",
    emoji="🔵",
    domain="Time & Memory",
    color="#4A90E2"
)

DIALGA.quotes = {
    EventType.PROGRESS: [
        "🔵 DIALGA: Time flows forward. Analyzing {timeframe} temporal patterns...",
        "🔵 DIALGA: The river of time reveals its secrets. {progress}% analyzed.",
        "🔵 DIALGA: Past, present, future converge. Processing epoch {epoch}...",
    ],
    EventType.DISCOVERY: [
        "🔵 DIALGA: Time fractures reveal truth! Pattern found: {pattern}",
        "🔵 DIALGA: The temporal anomaly speaks: {insight}",
        "🔵 DIALGA: Chronos whispers secrets of {discovery}",
    ],
    EventType.MILESTONE: [
        "🔵 DIALGA: A moment crystallized in eternity. {milestone} achieved.",
        "🔵 DIALGA: Time checkpoint created. Progress preserved.",
    ],
}


# ═══════════════════════════════════════════════════════════════
# 🟣 PALKIA - Spatial Pokemon
# ═══════════════════════════════════════════════════════════════

PALKIA = Deity(
    name="PALKIA",
    title="Lord of Space",
    emoji="🟣",
    domain="Space & Dimension",
    color="#D946EF"
)

PALKIA.quotes = {
    EventType.PROGRESS: [
        "🟣 PALKIA: Space warps to my command. Mapping dimension {dimension}...",
        "🟣 PALKIA: The fabric of space unfolds. {progress}% dimensional coverage.",
        "🟣 PALKIA: Reality bends. Scanning spatial coordinates {coords}...",
    ],
    EventType.DISCOVERY: [
        "🟣 PALKIA: A spatial rift reveals: {pattern}!",
        "🟣 PALKIA: Dimensions align to show: {insight}",
        "🟣 PALKIA: The void between spaces speaks of {discovery}",
    ],
    EventType.INSIGHT: [
        "🟣 PALKIA: Spatial analysis complete. Key finding: {insight}",
        "🟣 PALKIA: The geometry of profit emerges: {pattern}",
    ],
}


# ═══════════════════════════════════════════════════════════════
# ⚫ GIRATINA - Antimatter Pokemon
# ═══════════════════════════════════════════════════════════════

GIRATINA = Deity(
    name="GIRATINA",
    title="Lord of Chaos & Antimatter",
    emoji="⚫",
    domain="Chaos & Entropy",
    color="#1F1F1F"
)

GIRATINA.quotes = {
    EventType.PROGRESS: [
        "⚫ GIRATINA: From the distortion world, I sense chaos. Analyzing entropy {level}...",
        "⚫ GIRATINA: Disorder becomes order in my realm. {progress}% chaotic features extracted.",
        "⚫ GIRATINA: The antimatter flows. Detecting anomalies in {domain}...",
    ],
    EventType.DISCOVERY: [
        "⚫ GIRATINA: Chaos reveals order! Anomaly detected: {pattern}",
        "⚫ GIRATINA: The void screams truth: {insight}!",
        "⚫ GIRATINA: From disorder, clarity: {discovery}",
    ],
    EventType.REGIME_CHANGE: [
        "⚫ GIRATINA: Reality shifts! Market regime transitions from {old_regime} to {new_regime}!",
        "⚫ GIRATINA: The distortion world opens. Regime change detected: {regime}",
        "⚫ GIRATINA: Chaos reigns anew. {regime} regime established.",
    ],
    EventType.WARNING: [
        "⚫ GIRATINA: The shadows warn of danger: {warning}",
        "⚫ GIRATINA: Antimatter surges. Beware: {warning}",
        "⚫ GIRATINA: My domain trembles. Caution advised: {warning}",
    ],
}


# ═══════════════════════════════════════════════════════════════
# 🌟 NECROZMA - The Light Devourer
# ═══════════════════════════════════════════════════════════════

NECROZMA = Deity(
    name="NECROZMA",
    title="The Blinding One - Devourer of Light",
    emoji="🌟",
    domain="Light & Synthesis",
    color="#FFD700"
)

NECROZMA.quotes = {
    EventType.AWAKENING: [
        "🌟 NECROZMA: I hunger for light... The hunt begins.",
        "🌟 NECROZMA: Darkness fades before me. Awakening to devour all illumination.",
        "🌟 NECROZMA: The Prism Armor forms. Let the light gathering commence.",
    ],
    EventType.LIGHT_FOUND: [
        "🌟 NECROZMA: LIGHT DETECTED! Strategy brilliance: {score}/100",
        "🌟 NECROZMA: The luminescence calls to me! {strategy} shines bright!",
        "🌟 NECROZMA: Such radiance! I feast upon {discovery}!",
    ],
    EventType.TOP_STRATEGY: [
        "🌟 NECROZMA: PURE LIGHT ACQUIRED! Top strategy: {strategy} (Sharpe: {sharpe})",
        "🌟 NECROZMA: This brilliance... it blinds! {name} ranks #{rank}",
        "🌟 NECROZMA: The light that burns the sky! Strategy: {strategy}",
    ],
    EventType.DISCOVERY: [
        "🌟 NECROZMA: Light emerges from data! Discovery: {pattern}",
        "🌟 NECROZMA: The prism refracts truth: {insight}",
        "🌟 NECROZMA: Illumination achieved: {discovery}",
    ],
    EventType.INSIGHT: [
        "🌟 NECROZMA: The light reveals: {insight}",
        "🌟 NECROZMA: Radiant truth discovered: {finding}",
        "🌟 NECROZMA: Brilliance crystallized: {pattern}",
    ],
    EventType.COMPLETION: [
        "🌟 NECROZMA: All light has been devoured. The synthesis is complete.",
        "🌟 NECROZMA: From scattered rays to focused beam. The truth illuminates.",
        "🌟 NECROZMA: ULTRA BURST ACHIEVED! The final form reveals all!",
    ],
    EventType.WARNING: [
        "🌟 NECROZMA: Darkness detected. Warning: {warning}",
        "🌟 NECROZMA: The light dims... Concern: {warning}",
    ],
}


# ═══════════════════════════════════════════════════════════════
# 🎭 LORE SYSTEM
# ═══════════════════════════════════════════════════════════════

class LoreSystem:
    """Centralized lore management system"""
    
    def __init__(self, enabled: bool = True, enable_telegram: bool = True):
        """
        Initialize LoreSystem with optional Telegram notifications
        
        Args:
            enabled: Whether lore system is enabled
            enable_telegram: Whether to enable Telegram notifications
        """
        self.enabled = enabled
        self.telegram_enabled = enable_telegram
        self.telegram_notifier = None
        
        self.deities = {
            "ARCEUS": ARCEUS,
            "DIALGA": DIALGA,
            "PALKIA": PALKIA,
            "GIRATINA": GIRATINA,
            "NECROZMA": NECROZMA,
        }
        
        # Initialize Telegram if enabled
        if self.telegram_enabled:
            self._init_telegram()
    
    def _init_telegram(self):
        """Initialize Telegram notifier"""
        try:
            from telegram_notifier import TelegramNotifier
            
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            chat_id = os.getenv('TELEGRAM_CHAT_ID')
            
            if bot_token and chat_id:
                self.telegram_notifier = TelegramNotifier(bot_token, chat_id)
                print("✅ Telegram notifications enabled")
            else:
                print("⚠️ Telegram credentials not found in environment")
                self.telegram_enabled = False
        except ImportError:
            print("⚠️ telegram_notifier module not found")
            self.telegram_enabled = False
        except Exception as e:
            print(f"⚠️ Telegram initialization failed: {e}")
            self.telegram_enabled = False
    
    def broadcast(self, event_type, message=None, **kwargs):
        """
        Send notification via Telegram if enabled
        
        Args:
            event_type: Type of event (from EventType enum or string)
            message: Optional custom message
            **kwargs: Additional data for message formatting
        """
        if not self.telegram_enabled or not self.telegram_notifier:
            return
        
        try:
            # Convert EventType enum to string if needed
            if hasattr(event_type, 'value'):
                event_str = event_type.value
            else:
                event_str = str(event_type)
            
            # Format message
            if message:
                final_message = message
            else:
                # Try specific formatting first, fall back to default
                final_message = self._format_message(event_type, message, **kwargs)
                if not final_message or (isinstance(final_message, str) and final_message.startswith(event_str)):
                    # Use default formatting if specific formatting wasn't found
                    final_message = self._format_default_message(event_str, **kwargs)
            
            # Send via telegram
            self.telegram_notifier.send_message(final_message)
            
        except Exception as e:
            # Don't crash if telegram fails
            print(f"⚠️ Telegram notification failed: {e}")
    
    def _format_message(self, event_type, message, **kwargs):
        """Format message based on event type"""
        # If custom message provided, use it
        if message:
            return message
        
        # Format message based on event type
        if event_type == EventType.SYSTEM_INIT:
            python_ver = kwargs.get('python_version', 'Unknown')
            timestamp = kwargs.get('timestamp', '')
            return f"""🌟 <b>ULTRA NECROZMA AWAKENING</b> 🌟

⚡ System initializing...
🐍 Python {python_ver}
📅 {timestamp}

<i>The Blinding One prepares to analyze the markets...</i>"""
        
        elif event_type == EventType.SYSTEM_CHECK:
            deps = kwargs.get('dependencies', [])
            deps_str = ', '.join(deps) if isinstance(deps, list) else deps
            return f"""🔍 <b>SYSTEM CHECK IN PROGRESS</b>

✅ Verifying dependencies...
⚙️ {deps_str}
💎 Preparing prismatic cores...

<i>All systems operational ✓</i>"""
        
        elif event_type == EventType.DATA_LOADING:
            filename = kwargs.get('filename', 'data')
            size_gb = kwargs.get('size_gb', '?')
            return f"""💎 <b>CRYSTAL LOADING INITIATED</b>

📊 Dataset: {filename}
💾 Size: {size_gb} GB
⏱️ Loading in progress...

<i>Temporal shift commencing...</i>"""
        
        elif event_type == EventType.DATA_LOADED:
            rows = kwargs.get('rows', '?')
            memory_gb = kwargs.get('memory_gb', '?')
            load_time = kwargs.get('load_time', '?')
            rows_per_sec = kwargs.get('rows_per_sec', '?')
            start_date = kwargs.get('start_date', '')
            end_date = kwargs.get('end_date', '')
            min_price = kwargs.get('min_price', '')
            max_price = kwargs.get('max_price', '')
            
            return f"""✅ <b>CRYSTAL LOADED SUCCESSFULLY</b>

📊 Rows: {rows}
💾 Memory: {memory_gb} GB
⏱️ Time: {load_time}s
⚡ Speed: {rows_per_sec} rows/sec

<b>Period:</b> {start_date} → {end_date}
<b>Price Range:</b> {min_price} - {max_price}"""
        
        elif event_type == EventType.ANALYSIS_START:
            num_universes = kwargs.get('num_universes', '?')
            num_workers = kwargs.get('num_workers', '?')
            stages = kwargs.get('stages', '')
            return f"""⚡ <b>ANALYSIS PHASE INITIATED</b>

🌌 Universes to process: {num_universes}
⚡ Workers: {num_workers}
💎 Evolution stages: {stages}

<i>The light begins to pierce through all dimensions...</i>"""
        
        elif event_type == EventType.UNIVERSE_PROGRESS:
            percentage = kwargs.get('percentage', '?')
            completed = kwargs.get('completed', '?')
            total = kwargs.get('total', '?')
            total_patterns = kwargs.get('total_patterns', '?')
            current_evolution = kwargs.get('current_evolution', 'Necrozma')
            power = kwargs.get('power', '?')
            
            return f"""📊 <b>ANALYSIS PROGRESS: {percentage}%</b>

🌌 Universes processed: {completed}/{total}
🎯 Patterns found: {total_patterns}
⚡ Evolution: {current_evolution}
💎 Light Power: {power}%

<i>Analysis continues...</i>"""
        
        elif event_type == EventType.AWAKENING:
            return "🌟 <b>ULTRA NECROZMA AWAKENING</b> 🌟\n\n<i>The Blinding One emerges from the void...</i>"
        
        # Default formatting for other event types
        return f"{event_type.value}: {kwargs}"
    
    def _format_default_message(self, event_type, **kwargs):
        """Generate default message for event type"""
        # Basic formatting based on event type
        if 'progress' in event_type.lower():
            return f"📊 Progress: {kwargs.get('message', 'Processing...')}"
        elif 'complete' in event_type.lower():
            return f"✅ Complete: {kwargs.get('message', 'Task finished')}"
        elif 'error' in event_type.lower():
            return f"❌ Error: {kwargs.get('message', 'An error occurred')}"
        else:
            return f"ℹ️ {event_type}: {kwargs.get('message', 'Event occurred')}"
    
    def speak(self, deity_name: str, event_type: EventType, **kwargs) -> str:
        """
        Get a quote from a specific deity
        
        Args:
            deity_name: Name of the deity (ARCEUS, DIALGA, PALKIA, GIRATINA, NECROZMA)
            event_type: Type of event
            **kwargs: Variables for string formatting
            
        Returns:
            Formatted quote or empty string if lore disabled
        """
        if not self.enabled:
            return ""
        
        deity_name = deity_name.upper()
        if deity_name not in self.deities:
            return ""
        
        deity = self.deities[deity_name]
        return deity.speak(event_type, **kwargs)
    
    def get_deity_info(self, deity_name: str) -> Dict:
        """Get information about a deity"""
        deity_name = deity_name.upper()
        if deity_name not in self.deities:
            return {}
        
        deity = self.deities[deity_name]
        return {
            "name": deity.name,
            "title": deity.title,
            "emoji": deity.emoji,
            "domain": deity.domain,
            "color": deity.color,
        }
    
    def get_all_deities(self) -> List[Dict]:
        """Get info about all deities"""
        return [self.get_deity_info(name) for name in self.deities.keys()]


# ═══════════════════════════════════════════════════════════════
# 🎨 HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def format_message(deity_name: str, event_type: EventType, message: str = None, **kwargs) -> str:
    """
    Format a complete message with lore
    
    Args:
        deity_name: Deity who speaks
        event_type: Type of event
        message: Optional custom message (overrides lore quote)
        **kwargs: Variables for lore quote formatting
        
    Returns:
        Formatted message string
    """
    lore = LoreSystem()
    
    if message:
        deity = lore.deities.get(deity_name.upper())
        if deity:
            return f"{deity.emoji} {deity.name}: {message}"
        return message
    
    return lore.speak(deity_name, event_type, **kwargs)


# ═══════════════════════════════════════════════════════════════
# 🧪 TESTING
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║              🎭 NECROZMA LORE SYSTEM TEST 🎭                 ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    lore = LoreSystem(enabled=True)
    
    print("\n📜 THE FIVE DEITIES:\n")
    for deity_info in lore.get_all_deities():
        print(f"{deity_info['emoji']} {deity_info['name']} - {deity_info['title']}")
        print(f"   Domain: {deity_info['domain']}")
        print()
    
    print("\n🗣️  SAMPLE QUOTES:\n")
    
    # ARCEUS awakening
    print(lore.speak("ARCEUS", EventType.AWAKENING))
    
    # DIALGA progress
    print(lore.speak("DIALGA", EventType.PROGRESS, timeframe="5m", progress=50))
    
    # PALKIA discovery
    print(lore.speak("PALKIA", EventType.DISCOVERY, pattern="Golden Cross"))
    
    # GIRATINA regime change
    print(lore.speak("GIRATINA", EventType.REGIME_CHANGE, 
                     old_regime="RANGING", new_regime="TRENDING"))
    
    # NECROZMA light found
    print(lore.speak("NECROZMA", EventType.LIGHT_FOUND, 
                     strategy="TrendFollower", score=95))
    
    # NECROZMA top strategy
    print(lore.speak("NECROZMA", EventType.TOP_STRATEGY, 
                     strategy="MeanReversion", sharpe=2.5, rank=1))
    
    # ARCEUS completion
    print(lore.speak("ARCEUS", EventType.COMPLETION))
    
    print("\n✅ Lore system test complete!")
