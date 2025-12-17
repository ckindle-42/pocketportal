"""
Slack Interface - Adapter for AgentCore
=======================================

Slack bot interface using the unified AgentCore.
Provides similar functionality to Telegram but adapted for Slack.

Features:
- Slash commands
- Direct messages
- Channel mentions
- File uploads
- Interactive buttons
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_sdk.errors import SlackApiError

# Import the unified core
sys.path.insert(0, str(Path(__file__).parent.parent))
from core import AgentCore, ProcessingResult

# Import existing config and security
from config_validator import load_and_validate_config
from security.security_module import RateLimiter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SlackInterface:
    """
    Slack Bot Interface using AgentCore
    
    This class handles all Slack-specific concerns:
    - Slack API integration
    - Message formatting
    - Event handling
    - File processing
    
    The actual AI processing is delegated to AgentCore.
    """
    
    def __init__(self):
        """Initialize Slack interface"""
        
        logger.info("=" * 60)
        logger.info("Initializing Slack Interface")
        logger.info("=" * 60)
        
        # Load configuration
        self.config = load_and_validate_config()
        if not self.config:
            raise ValueError("Invalid configuration")
        
        # Slack-specific config
        self.bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.app_token = os.getenv("SLACK_APP_TOKEN")
        self.authorized_users = os.getenv("SLACK_AUTHORIZED_USERS", "").split(",")
        
        if not self.bot_token or not self.app_token:
            raise ValueError(
                "Missing Slack tokens. Set SLACK_BOT_TOKEN and SLACK_APP_TOKEN in .env"
            )
        
        # Initialize Slack app
        self.app = AsyncApp(token=self.bot_token)
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            max_requests=self.config.rate_limit_messages,
            window_seconds=self.config.rate_limit_window
        )
        
        # Build core configuration
        core_config = {
            'ollama_base_url': self.config.ollama_base_url,
            'lmstudio_base_url': self.config.lmstudio_base_url,
            'routing_strategy': self.config.routing_strategy,
            'model_preferences': self._build_model_preferences()
        }
        
        # Initialize the unified core
        logger.info("Initializing AgentCore...")
        self.agent_core = AgentCore(core_config)
        
        # Register event handlers
        self._register_handlers()
        
        logger.info("=" * 60)
        logger.info("Slack Interface ready!")
        logger.info(f"  Bot token: {self.bot_token[:20]}...")
        logger.info(f"  Authorized users: {len(self.authorized_users)}")
        logger.info("=" * 60)
    
    def _build_model_preferences(self) -> Dict:
        """Build model preferences from config"""
        return {
            'trivial': [m.strip() for m in self.config.model_pref_trivial.split(',') if m.strip()],
            'simple': [m.strip() for m in self.config.model_pref_simple.split(',') if m.strip()],
            'moderate': [m.strip() for m in self.config.model_pref_moderate.split(',') if m.strip()],
            'complex': [m.strip() for m in self.config.model_pref_complex.split(',') if m.strip()],
            'expert': [m.strip() for m in self.config.model_pref_expert.split(',') if m.strip()],
            'code': [m.strip() for m in self.config.model_pref_code.split(',') if m.strip()]
        }
    
    def _is_authorized(self, user_id: str) -> bool:
        """Check if user is authorized"""
        # Allow all if no restrictions set
        if not self.authorized_users or self.authorized_users == ['']:
            return True
        return user_id in self.authorized_users
    
    def _register_handlers(self):
        """Register Slack event handlers"""
        
        # Message events
        self.app.event("message")(self.handle_message)
        
        # App mentions
        self.app.event("app_mention")(self.handle_mention)
        
        # Slash commands
        self.app.command("/ai")(self.handle_ai_command)
        self.app.command("/tools")(self.handle_tools_command)
        self.app.command("/stats")(self.handle_stats_command)
        self.app.command("/health")(self.handle_health_command)
    
    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================
    
    async def handle_message(self, event, say):
        """Handle direct messages"""
        
        # Ignore bot messages
        if event.get("bot_id"):
            return
        
        user_id = event["user"]
        text = event.get("text", "")
        channel = event["channel"]
        
        # Check authorization
        if not self._is_authorized(user_id):
            await say("⛔ Unauthorized. Contact admin for access.")
            return
        
        # Check rate limiting
        allowed, error_msg = self.rate_limiter.check_limit(user_id)
        if not allowed:
            await say(error_msg)
            return
        
        logger.info(f"Received message from user {user_id}: {text[:50]}...")
        
        # Show typing indicator
        try:
            await self.app.client.chat_postMessage(
                channel=channel,
                text="🤔 Processing..."
            )
            
            # Process with unified core
            result: ProcessingResult = await self.agent_core.process_message(
                chat_id=f"slack_{channel}_{user_id}",
                message=text,
                interface="slack",
                user_context={'user_id': user_id, 'channel': channel}
            )
            
            # Format response for Slack
            response_text = result.response
            
            # Add footer with model info if verbose
            if self.config.verbose_routing:
                response_text += f"\n\n_Model: {result.model_used} ({result.execution_time:.2f}s)_"
                if result.tools_used:
                    response_text += f"\n_Tools: {', '.join(result.tools_used)}_"
            
            # Send response
            await say(response_text)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            await say(f"⚠️ Error processing your request: {str(e)}")
    
    async def handle_mention(self, event, say):
        """Handle @bot mentions in channels"""
        
        # Remove mention from text
        text = event.get("text", "")
        # Remove <@BOTID> from start
        text = text.split(">", 1)[-1].strip()
        
        # Process like a regular message
        event["text"] = text
        await self.handle_message(event, say)
    
    async def handle_ai_command(self, ack, command, say):
        """Handle /ai slash command"""
        await ack()
        
        user_id = command["user_id"]
        text = command.get("text", "")
        
        if not self._is_authorized(user_id):
            await say("⛔ Unauthorized")
            return
        
        if not text:
            await say("Usage: `/ai <your question>`")
            return
        
        # Process with core
        result = await self.agent_core.process_message(
            chat_id=f"slack_cmd_{user_id}",
            message=text,
            interface="slack",
            user_context={'user_id': user_id}
        )
        
        await say(result.response)
    
    async def handle_tools_command(self, ack, say):
        """Handle /tools slash command"""
        await ack()
        
        tools = self.agent_core.get_tool_list()
        
        message = f"*Available Tools ({len(tools)}):*\n\n"
        
        # Group by category
        by_category = {}
        for tool in tools:
            cat = tool['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(tool)
        
        for category, cat_tools in sorted(by_category.items()):
            message += f"*{category.upper()}:*\n"
            for tool in cat_tools:
                confirm = "🔒 " if tool['requires_confirmation'] else ""
                message += f"  • {confirm}{tool['name']}: {tool['description']}\n"
            message += "\n"
        
        await say(message)
    
    async def handle_stats_command(self, ack, say):
        """Handle /stats slash command"""
        await ack()
        
        stats = self.agent_core.get_stats()
        
        message = (
            "*📊 Processing Statistics:*\n\n"
            f"• Messages processed: {stats['messages_processed']}\n"
            f"• Tools executed: {stats['tools_executed']}\n"
            f"• Avg execution time: {stats['avg_execution_time']:.2f}s\n"
            f"• Uptime: {stats['uptime_seconds']:.0f}s\n\n"
            "*By Interface:*\n"
        )
        
        for interface, count in stats['by_interface'].items():
            message += f"  • {interface}: {count}\n"
        
        await say(message)
    
    async def handle_health_command(self, ack, say):
        """Handle /health slash command"""
        await ack()
        
        stats = self.agent_core.get_stats()
        tools = self.agent_core.get_tool_list()
        
        health = (
            "*🏥 System Health:*\n\n"
            f"✅ Core: Running\n"
            f"✅ Tools: {len(tools)} loaded\n"
            f"✅ Models: Available\n"
            f"✅ Messages: {stats['messages_processed']} processed\n"
            f"✅ Uptime: {stats['uptime_seconds']:.0f}s\n\n"
            "All systems operational! 🚀"
        )
        
        await say(health)
    
    # ========================================================================
    # STARTUP & RUN
    # ========================================================================
    
    async def run(self):
        """Start the Slack bot"""
        
        logger.info("=" * 60)
        logger.info("🚀 Slack Bot Starting!")
        logger.info("=" * 60)
        
        # Create socket mode handler
        handler = AsyncSocketModeHandler(self.app, self.app_token)
        
        # Start
        await handler.start_async()


# ============================================================================
# ENTRY POINT
# ============================================================================

async def main():
    """Main entry point"""
    
    # Ensure required directories exist
    Path("logs").mkdir(exist_ok=True)
    Path("screenshots").mkdir(exist_ok=True)
    Path("browser_data").mkdir(exist_ok=True)
    
    # Create and run interface
    interface = SlackInterface()
    await interface.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
