"""
Gematria Tool for calculating numerical values of Hebrew text
Uses traditional Jewish Gematria values
"""
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()


class GematriaCalculator:
    def __init__(self):
        # Traditional Hebrew Gematria values
        self.hebrew_values = {
            # Alef to Yud (1-10)
            'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5,
            'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9, 'י': 10,
            
            # Kaf to Tzadi (20-90)
            'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60,
            'ע': 70, 'פ': 80, 'צ': 90,
            
            # Kuf to Tav (100-400)
            'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400,
            
            # Final letters (same values as regular letters)
            'ך': 20, 'ם': 40, 'ן': 50, 'ף': 80, 'ץ': 90
        }
    
    def calculate_gematria(self, hebrew_text: str) -> dict:
        """
        Calculate the Gematria value of Hebrew text
        
        Args:
            hebrew_text: Hebrew text to calculate
            
        Returns:
            Dictionary with calculation details
        """
        if not hebrew_text:
            return {
                "error": "No text provided",
                "value": 0,
                "breakdown": []
            }
        
        # Remove spaces and punctuation, keep only Hebrew characters
        cleaned_text = ''.join(char for char in hebrew_text if char in self.hebrew_values)
        
        if not cleaned_text:
            return {
                "error": "No Hebrew characters found in text",
                "value": 0,
                "breakdown": []
            }
        
        total_value = 0
        breakdown = []
        
        for char in cleaned_text:
            if char in self.hebrew_values:
                value = self.hebrew_values[char]
                total_value += value
                breakdown.append({
                    "character": char,
                    "value": value,
                    "name": self._get_hebrew_letter_name(char)
                })
        
        return {
            "text": hebrew_text,
            "cleaned_text": cleaned_text,
            "value": total_value,
            "breakdown": breakdown,
            "character_count": len(cleaned_text)
        }
    
    def _get_hebrew_letter_name(self, char: str) -> str:
        """Get the name of a Hebrew letter"""
        letter_names = {
            'א': 'Alef', 'ב': 'Bet', 'ג': 'Gimel', 'ד': 'Dalet', 'ה': 'He',
            'ו': 'Vav', 'ז': 'Zayin', 'ח': 'Chet', 'ט': 'Tet', 'י': 'Yud',
            'כ': 'Kaf', 'ל': 'Lamed', 'מ': 'Mem', 'נ': 'Nun', 'ס': 'Samech',
            'ע': 'Ayin', 'פ': 'Pe', 'צ': 'Tzadi', 'ק': 'Kuf', 'ר': 'Resh',
            'ש': 'Shin', 'ת': 'Tav', 'ך': 'Final Kaf', 'ם': 'Final Mem',
            'ן': 'Final Nun', 'ף': 'Final Pe', 'ץ': 'Final Tzadi'
        }
        return letter_names.get(char, char)
    
    def format_result(self, result: dict) -> str:
        """Format the Gematria calculation result as a readable string"""
        if "error" in result:
            return f"❌ {result['error']}"
        
        output = f"📊 Gematria Calculation for: {result['text']}\n"
        output += f"🔢 Total Value: {result['value']}\n"
        output += f"📝 Characters: {result['character_count']}\n\n"
        
        if result['breakdown']:
            output += "📋 Breakdown:\n"
            for item in result['breakdown']:
                output += f"  {item['character']} ({item['name']}) = {item['value']}\n"
        
        return output


# Create global instance
gematria_calculator = GematriaCalculator()


@tool
def calculate_gematria(hebrew_text: str, detailed: bool = True) -> str:
    """
    Calculate the Gematria (numerical value) of Hebrew text.
    Gematria is a Jewish tradition of assigning numerical values to Hebrew letters.
    
    Args:
        hebrew_text: Hebrew text to calculate (can include spaces and punctuation)
        detailed: If True, provides detailed breakdown. If False, returns simple value.
        
    Returns:
        Gematria calculation result - either detailed breakdown or simple value
        
    Examples:
        - "שלום" (peace) = 376
        - "אהבה" (love) = 13
        - "חיים" (life) = 68
    """
    result = gematria_calculator.calculate_gematria(hebrew_text)
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    if detailed:
        return gematria_calculator.format_result(result)
    else:
        return f"The Gematria value of '{hebrew_text}' is {result['value']}"


# Test function for development
def test_gematria():
    """Test the Gematria calculator with common Hebrew words"""
    test_words = [
        "שלום",  # peace
        "אהבה",  # love
        "חיים",  # life
        "אלוהים",  # God
        "תורה",  # Torah
        "משיח",  # Messiah
    ]
    
    print("🧮 Testing Gematria Calculator...\n")
    
    for word in test_words:
        result = gematria_calculator.calculate_gematria(word)
        print(gematria_calculator.format_result(result))
        print("-" * 40)


if __name__ == "__main__":
    test_gematria() 