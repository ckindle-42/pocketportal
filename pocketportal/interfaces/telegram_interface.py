"""
Telegram Interface - Adapter for AgentCore
==========================================

This is a thin adapter that connects Telegram to the unified AgentCore.
All the AI logic lives in the core - this just handles Telegram-specific stuff.

Architecture:
    Telegram Updates → TelegramInterface → AgentCore → Response → Telegram
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.constants import ChatAction

# Import the unified core
from pocketportal.core import AgentCoreV2, ProcessingResult

# Import existing config and security
from pocketportal.config import load_config
from pocketportal.security.security_module import RateLimiter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramInterface:
    """
    Telegram Bot Interface using AgentCore
    
    This class handles all Telegram-specific concerns:
    - Authorization
    - Rate limiting  
    - Message formatting
    - Media handling
    
    The actual AI processing is delegated to AgentCore.
    """
    
    def __init__(self):
        """Initialize Telegram interface"""
        
        logger.info("=" * 60)
        logger.info("Initializing Telegram Interface")
        logger.info("=" * 60)
        
        # Load and validate configuration
        self.config = load_and_validate_config()
        if not self.config:
            raise ValueError("Invalid configuration - please fix .env file")
        
        # Telegram-specific config
        self.bot_token = self.config.telegram_bot_token
        self.authorized_user_id = self.config.telegram_user_id
        
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
            'model_preferences': {
                'trivial': [m.strip() for m in self.config.model_pref_trivial.split(',') if m.strip()],
                'simple': [m.strip() for m in self.config.model_pref_simple.split(',') if m.strip()],
                'moderate': [m.strip() for m in self.config.model_pref_moderate.split(',') if m.strip()],
                'complex': [m.strip() for m in self.config.model_pref_complex.split(',') if m.strip()],
                'expert': [m.strip() for m in self.config.model_pref_expert.split(',') if m.strip()],
                'code': [m.strip() for m in self.config.model_pref_code.split(',') if m.strip()]
            }
        }
        
        # Initialize the unified core
        logger.info("Initializing AgentCore...")
        self.agent_core = AgentCore(core_config)
        
        # Telegram application
        self.application = None
        
        logger.info("=" * 60)
        logger.info("Telegram Interface ready!")
        logger.info(f"  Bot token: {self.bot_token[:20]}...")
        logger.info(f"  Authorized user: {self.authorized_user_id}")
        logger.info("=" * 60)
    
    # ========================================================================
    # AUTHORIZATION & SECURITY
    # ========================================================================
    
    def _is_authorized(self, update: Update) -> bool:
        """Check if user is authorized"""
        return update.effective_user.id == self.authorized_user_id
    
    def _check_rate_limit(self, user_id: int) -> tuple[bool, Optional[str]]:
        """Check rate limiting"""
        return self.rate_limiter.check_limit(user_id)
    
    # ========================================================================
    # COMMAND HANDLERS
    # ========================================================================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not self._is_authorized(update):
            await update.message.reply_text("⛔ Unauthorized")
            return
        
        welcome = (
            "🤖 **PocketPortal Agent v3.1**\n\n"
            "🧠 Unified core architecture\n"
            "🔧 11+ tools ready\n"
            "🚀 Intelligent routing\n\n"
            "**Commands:**\n"
            "• `/help` - Show help\n"
            "• `/tools` - List tools\n"
            "• `/stats` - Show stats\n"
            "• `/health` - System health\n\n"
            "Just send me a message to get started!"
        )
        
        await update.message.reply_text(welcome, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not self._is_authorized(update):
            await update.message.reply_text("⛔ Unauthorized")
            return
        
        help_text = (
            "**Available Commands:**\n\n"
            "• `/start` - Welcome message\n"
            "• `/help` - This help message\n"
            "• `/tools` - List available tools\n"
            "• `/stats` - Processing statistics\n"
            "• `/health` - System health check\n\n"
            "**How to use:**\n"
            "Just send me a message with your request. "
            "I'll automatically select the best model and tools to help you!"
        )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def tools_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /tools command"""
        if not self._is_authorized(update):
            await update.message.reply_text("⛔ Unauthorized")
            return
        
        tools = self.agent_core.get_tool_list()
        
        message = f"**Available Tools ({len(tools)}):**\n\n"
        
        # Group by category
        by_category = {}
        for tool in tools:
            cat = tool['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(tool)
        
        for category, cat_tools in sorted(by_category.items()):
            message += f"**{category.upper()}:**\n"
            for tool in cat_tools:
                confirm = "🔒" if tool['requires_confirmation'] else ""
                message += f"  • {confirm} {tool['name']}: {tool['description']}\n"
            message += "\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        if not self._is_authorized(update):
            await update.message.reply_text("⛔ Unauthorized")
            return
        
        stats = self.agent_core.get_stats()
        
        message = (
            "**📊 Processing Statistics:**\n\n"
            f"• Messages processed: {stats['messages_processed']}\n"
            f"• Tools executed: {stats['tools_executed']}\n"
            f"• Avg execution time: {stats['avg_execution_time']:.2f}s\n"
            f"• Uptime: {stats['uptime_seconds']:.0f}s\n\n"
            "**By Interface:**\n"
        )
        
        for interface, count in stats['by_interface'].items():
            message += f"  • {interface}: {count}\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def health_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /health command"""
        if not self._is_authorized(update):
            await update.message.reply_text("⛔ Unauthorized")
            return
        
        # Get stats
        stats = self.agent_core.get_stats()
        tools = self.agent_core.get_tool_list()
        
        health = (
            "**🏥 System Health:**\n\n"
            f"✅ Core: Running\n"
            f"✅ Tools: {len(tools)} loaded\n"
            f"✅ Models: Available\n"
            f"✅ Messages: {stats['messages_processed']} processed\n"
            f"✅ Uptime: {stats['uptime_seconds']:.0f}s\n\n"
            "All systems operational! 🚀"
        )
        
        await update.message.reply_text(health, parse_mode='Markdown')
    
    # ========================================================================
    # MESSAGE HANDLER
    # ========================================================================
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages - the main interaction"""
        
        # Authorization check
        if not self._is_authorized(update):
            await update.message.reply_text("⛔ Unauthorized")
            return
        
        # Rate limiting check
        user_id = update.effective_user.id
        allowed, error_msg = self._check_rate_limit(user_id)
        if not allowed:
            await update.message.reply_text(error_msg)
            return
        
        message = update.message.text
        chat_id = f"telegram_{update.effective_chat.id}"
        
        logger.info(f"Received message from user {user_id}: {message[:50]}...")
        
        # Show typing indicator
        await update.message.chat.send_action(ChatAction.TYPING)
        
        try:
            # Process with unified core
            result: ProcessingResult = await self.agent_core.process_message(
                chat_id=chat_id,
                message=message,
                interface="telegram",
                user_context={'user_id': user_id}
            )
            
            # Show warnings if any
            if result.warnings:
                warning_text = "⚠️ Security warnings:\n" + "\n".join(result.warnings)
                await update.message.reply_text(warning_text)
            
            # Format response for Telegram
            response_text = result.response
            
            # Add footer with model info if verbose mode
            if self.config.verbose_routing:
                footer = (
                    f"\n\n_Model: {result.model_used} "
                    f"({result.execution_time:.2f}s)"
                )
                if result.tools_used:
                    footer += f" | Tools: {', '.join(result.tools_used)}"
                footer += "_"
                response_text += footer
            
            # Send response (handle long messages)
            if len(response_text) > 4096:
                # Split into chunks
                chunks = [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]
                for chunk in chunks:
                    await update.message.reply_text(chunk, parse_mode='Markdown')
            else:
                await update.message.reply_text(response_text, parse_mode='Markdown')
        
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            await update.message.reply_text(
                f"⚠️ Error processing your request: {str(e)}"
            )
    
    # ========================================================================
    # STARTUP & RUN
    # ========================================================================
    
    def run(self):
        """Start the Telegram bot"""
        
        logger.info("Building Telegram application...")
        
        # Create application
        self.application = Application.builder().token(self.bot_token).build()
        
        # Register command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("tools", self.tools_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("health", self.health_command))
        
        # Register message handler
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message)
        )
        
        logger.info("=" * 60)
        logger.info("🚀 Telegram Bot Starting!")
        logger.info("=" * 60)
        
        # Start polling
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    
    # Ensure required directories exist
    Path("logs").mkdir(exist_ok=True)
    Path("screenshots").mkdir(exist_ok=True)
    Path("browser_data").mkdir(exist_ok=True)
    
    # Create and run interface
    interface = TelegramInterface()
    interface.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
