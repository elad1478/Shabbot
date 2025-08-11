"""
QR Code Generation Tool
"""
import qrcode
import os
from datetime import datetime
from langchain_core.tools import tool
from langchain_experimental.tools import PythonREPLTool
from dotenv import load_dotenv

load_dotenv()

class QRCodeTool:
    def __init__(self):
        self.output_dir = "outputs/qr_codes"
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Ensure the output directory exists"""
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_qr_code(self, data: str, filename: str = None) -> str:
        """
        Generate a QR code from the given data
        
        Args:
            data: The data to encode in the QR code (URL, text, etc.)
            filename: Optional filename for the QR code image
            send_to_slack: Whether to send the QR code to Slack
            slack_description: Description to include when sending to Slack
            
        Returns:
            Path to the generated QR code image
        """
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"qr_code_{timestamp}.png"
            
            # Ensure filename has .png extension
            if not filename.endswith('.png'):
                filename += '.png'
            
            # Save image
            filepath = os.path.join(self.output_dir, filename)
            img.save(filepath)
            
            result = f"QR code generated successfully: {filepath}"
            
            return result
            
        except Exception as e:
            return f"Error generating QR code: {e}"
    
    def generate_multiple_qr_codes(self, data_list: list, base_filename: str = "qr_code") -> str:
        """
        Generate multiple QR codes from a list of data
        
        Args:
            data_list: List of data to encode in QR codes
            base_filename: Base filename for the QR codes
            
        Returns:
            Summary of generated QR codes
        """
        results = []
        for i, data in enumerate(data_list, 1):
            filename = f"{base_filename}_{i}.png"
            result = self.generate_qr_code(data, filename)
            results.append(f"QR {i}: {result}")
        
        return "\n".join(results)


# Create global instance
qr_tool = QRCodeTool()


@tool
def generate_qr_code(data: str, filename: str = None) -> str:
    """
    Generate a QR code from the given data (URL, text, etc.).
    Use this tool when asked to create QR codes for websites, text, or other data.
    
    Args:
        data: The data to encode in the QR code (URL, text, etc.)
        filename: Optional filename for the QR code image
        
    Returns:
        Path to the generated QR code image
    """
    return qr_tool.generate_qr_code(data, filename)


@tool
def generate_multiple_qr_codes(data_list: str, base_filename: str = "qr_code") -> str:
    """
    Generate multiple QR codes from a list of data.
    Use this tool when asked to create multiple QR codes at once.
    
    Args:
        data_list: Comma-separated list of data to encode in QR codes
        base_filename: Base filename for the QR codes
        
    Returns:
        Summary of generated QR codes
    """
    # Parse comma-separated string into list
    data_items = [item.strip() for item in data_list.split(',') if item.strip()]
    return qr_tool.generate_multiple_qr_codes(data_items, base_filename)


# Python REPL tool for advanced QR code operations
python_repl_tool = PythonREPLTool() 