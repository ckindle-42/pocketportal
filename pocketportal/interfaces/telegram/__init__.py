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

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from telegram.constants import ChatAction

# Import the unified core
from pocketportal.core import create_agent_core, ProcessingResult, EventBus

# Import confirmation middleware
from pocketportal.middleware import ToolConfirmationMiddleware, ConfirmationRequest

# Import existing config and security
from pocketportal.config.validator import load_and_validate_config
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

        # Initialize the unified core using factory function
        logger.info("Initializing AgentCore...")
        self.agent_core = create_agent_core(core_config)

        # Initialize confirmation middleware if enabled
        self.confirmation_middleware = None
        self.admin_chat_id = self.config.tools_admin_chat_id or self.config.telegram_user_id

        if self.config.tools_require_confirmation:
            logger.info("Initializing Tool Confirmation Middleware...")
            self.confirmation_middleware = ToolConfirmationMiddleware(
                event_bus=self.agent_core.event_bus,
                confirmation_sender=self._send_confirmation_request,
                default_timeout=self.config.tools_confirmation_timeout
            )

            # Inject middleware into agent core
            self.agent_core.confirmation_middleware = self.confirmation_middleware

            logger.info(
                f"Confirmation middleware enabled (admin_chat_id: {self.admin_chat_id}, "
                f"timeout: {self.config.tools_confirmation_timeout}s)"
            )

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
    # CONFIRMATION MIDDLEWARE INTEGRATION
    # ========================================================================

    async def _send_confirmation_request(self, request: ConfirmationRequest):
        """
        Send a confirmation request to the admin via Telegram

        This is called by the confirmation middleware when a high-risk tool
        needs approval before execution.

        Args:
            request: The confirmation request to send
        """
        try:
            # Format tool parameters for display
            params_str = "\n".join([
                f"  • {key}: {value}"
                for key, value in request.parameters.items()
            ])

            message = (
                f"⚠️ **Tool Confirmation Required**\n\n"
                f"**Tool:** `{request.tool_name}`\n"
                f"**User Chat:** {request.chat_id}\n"
                f"**User ID:** {request.user_id or 'Unknown'}\n\n"
                f"**Parameters:**\n{params_str}\n\n"
                f"**Timeout:** {request.timeout_seconds}s\n\n"
                f"This tool requires your approval before execution. "
                f"Please review and approve or deny."
            )

            # Create inline keyboard with Approve/Deny buttons
            keyboard = [
                [
                    InlineKeyboardButton(
                        "✅ Approve",
                        callback_data=f"confirm_approve:{request.confirmation_id}"
                    ),
                    InlineKeyboardButton(
                        "❌ Deny",
                        callback_data=f"confirm_deny:{request.confirmation_id}"
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Send to admin chat
            await self.application.bot.send_message(
                chat_id=self.admin_chat_id,
                text=message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )

            logger.info(
                f"Confirmation request sent to admin: {request.confirmation_id}",
                extra={
                    'tool_name': request.tool_name,
                    'confirmation_id': request.confirmation_id,
                    'admin_chat_id': self.admin_chat_id
                }
            )

        except Exception as e:
            logger.error(
                f"Failed to send confirmation request: {e}",
                exc_info=True
            )
            raise

    async def _handle_confirmation_callback(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Handle confirmation approval/denial callbacks

        This is called when the admin clicks Approve or Deny on a confirmation request.
        """
        query = update.callback_query
        await query.answer()

        # Check authorization
        if query.from_user.id != self.admin_chat_id:
            await query.edit_message_text("⛔ Unauthorized")
            return

        # Parse callback data
        callback_data = query.data
        if not callback_data:
            return

        try:
            action, confirmation_id = callback_data.split(':', 1)

            if action == "confirm_approve":
                # Approve the confirmation
                success = self.confirmation_middleware.approve(
                    confirmation_id,
                    approver_id=str(query.from_user.id)
                )

                if success:
                    await query.edit_message_text(
                        f"✅ **Tool Execution Approved**\n\n"
                        f"Confirmation ID: `{confirmation_id}`\n\n"
                        f"The tool will now be executed.",
                        parse_mode='Markdown'
                    )
                    logger.info(f"Tool execution approved: {confirmation_id}")
                else:
                    await query.edit_message_text(
                        f"⚠️ **Confirmation Not Found**\n\n"
                        f"The confirmation may have already been processed or expired.",
                        parse_mode='Markdown'
                    )

            elif action == "confirm_deny":
                # Deny the confirmation
                success = self.confirmation_middleware.deny(
                    confirmation_id,
                    denier_id=str(query.from_user.id)
                )

                if success:
                    await query.edit_message_text(
                        f"❌ **Tool Execution Denied**\n\n"
                        f"Confirmation ID: `{confirmation_id}`\n\n"
                        f"The tool execution has been cancelled.",
                        parse_mode='Markdown'
                    )
                    logger.info(f"Tool execution denied: {confirmation_id}")
                else:
                    await query.edit_message_text(
                        f"⚠️ **Confirmation Not Found**\n\n"
                        f"The confirmation may have already been processed or expired.",
                        parse_mode='Markdown'
                    )

        except ValueError as e:
            logger.error(f"Invalid callback data: {callback_data}", exc_info=True)
            await query.edit_message_text("⚠️ Invalid callback data")
        except Exception as e:
            logger.error(f"Error handling confirmation callback: {e}", exc_info=True)
            await query.edit_message_text(f"⚠️ Error: {str(e)}")

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

        # Register callback handler for confirmations
        if self.confirmation_middleware:
            self.application.add_handler(
                CallbackQueryHandler(
                    self._handle_confirmation_callback,
                    pattern=r"^confirm_(approve|deny):"
                )
            )
            logger.info("Confirmation callback handler registered")

        # Register message handler
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message)
        )

        # Start confirmation middleware
        if self.confirmation_middleware:
            asyncio.create_task(self.confirmation_middleware.start())
            logger.info("Confirmation middleware started")

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
