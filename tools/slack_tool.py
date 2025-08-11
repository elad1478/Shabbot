"""
Slack Tool for sending messages and files to Slack channels
Uses the standard Slack SDK for reliable messaging
"""
import os
from langchain_core.tools import tool
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()


class SlackTool:
    def __init__(self):
        self.client = None
        self.bot_token = os.environ.get("SLACK_BOT_TOKEN")
        self.channel_id = os.environ.get("SLACK_CHANNEL_ID")
        self._setup_slack()
    
    def _setup_slack(self):
        """Setup Slack client if credentials are available"""
        try:
            if self.bot_token:
                self.client = WebClient(token=self.bot_token)
                print("✅ Slack client initialized")
            else:
                print("⚠️  Slack bot token not found (SLACK_BOT_TOKEN)")
        except Exception as e:
            print(f"⚠️  Could not initialize Slack client: {e}")
    
    def send_message(self, message: str, channel: str = None) -> str:
        """
        Send a message to Slack channel
        
        Args:
            message: The message to send
            channel: Channel to send to (uses default if not specified)
            
        Returns:
            Confirmation message
        """
        if not self.client:
            return "Slack not available. Please set SLACK_BOT_TOKEN environment variable."
        
        try:
            target_channel = channel or self.channel_id
            if not target_channel:
                return "No channel specified. Please set SLACK_CHANNEL_ID or provide a channel parameter."
            
            result = self.client.chat_postMessage(
                channel=target_channel,
                text=message
            )
            
            return f"Message sent successfully to channel {target_channel}: {message}"
        except SlackApiError as e:
            error_msg = e.response['error']
            if error_msg == 'not_in_channel':
                return f"Error: Bot is not in the channel. Please invite the bot to channel {target_channel}"
            elif error_msg == 'missing_scope':
                return f"Error: Bot token missing required scopes. Need 'chat:write' and 'files:write' permissions"
            else:
                return f"Error sending message to Slack: {error_msg}"
        except Exception as e:
            return f"Error sending message to Slack: {e}"
    
    def send_file(self, file_path: str, message: str = "", channel: str = None) -> str:
        """
        Send a file to Slack channel
        
        Args:
            file_path: Path to the file to send
            message: Optional message to accompany the file
            channel: Channel to send to (uses default if not specified)
            
        Returns:
            Confirmation message
        """
        if not self.client:
            return "Slack not available. Please set SLACK_BOT_TOKEN environment variable."
        
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"
        
        try:
            target_channel = channel or self.channel_id
            if not target_channel:
                return "No channel specified. Please set SLACK_CHANNEL_ID or provide a channel parameter."
            
            # Upload file using the newer v2 method
            with open(file_path, 'rb') as file:
                result = self.client.files_upload_v2(
                    channel=target_channel,
                    file=file,
                    title=os.path.basename(file_path),
                    initial_comment=message if message else f"File: {os.path.basename(file_path)}"
                )
            
            return f"File sent successfully to channel {target_channel}: {os.path.basename(file_path)}"
        except SlackApiError as e:
            error_msg = e.response['error']
            if error_msg == 'not_in_channel':
                return f"Error: Bot is not in the channel. Please invite the bot to channel {target_channel}"
            elif error_msg == 'missing_scope':
                return f"Error: Bot token missing required scopes. Need 'chat:write' and 'files:write' permissions"
            else:
                return f"Error sending file to Slack: {error_msg}"
        except Exception as e:
            return f"Error sending file to Slack: {e}"
    
    def send_qr_code(self, qr_file_path: str, description: str = "", channel: str = None) -> str:
        """
        Send a QR code to Slack channel with description
        
        Args:
            qr_file_path: Path to the QR code image
            description: Description of what the QR code is for
            channel: Channel to send to (uses default if not specified)
            
        Returns:
            Confirmation message
        """
        if not os.path.exists(qr_file_path):
            return f"QR code file not found: {qr_file_path}"
        
        message = f"📱 QR Code Generated\n{description}" if description else "📱 QR Code Generated"
        
        return self.send_file(qr_file_path, message, channel)


# Create global instance
slack_tool = SlackTool()


@tool
def send_slack_message(message: str, channel: str = None) -> str:
    """
    Send a message to a Slack channel.
    
    Args:
        message: The message text to send to Slack
        channel: Optional channel ID (uses SLACK_CHANNEL_ID if not specified)
        
    Returns:
        Confirmation of message sent
    """
    return slack_tool.send_message(message, channel)


@tool
def send_slack_file(file_path: str, message: str = "", channel: str = None) -> str:
    """
    Send a file to a Slack channel.
    
    Args:
        file_path: Path to the file to send
        message: Optional message to accompany the file
        channel: Optional channel ID (uses SLACK_CHANNEL_ID if not specified)
        
    Returns:
        Confirmation of file sent
    """
    return slack_tool.send_file(file_path, message, channel)


@tool
def send_qr_code_to_slack(qr_file_path: str, description: str = "", channel: str = None) -> str:
    """
    Send a QR code to a Slack channel.
    Specialized tool for sending QR codes with descriptions.
    
    Args:
        qr_file_path: Path to the QR code image file
        description: Description of what the QR code is for
        channel: Optional channel ID (uses SLACK_CHANNEL_ID if not specified)
        
    Returns:
        Confirmation of QR code sent
    """
    return slack_tool.send_qr_code(qr_file_path, description, channel) 