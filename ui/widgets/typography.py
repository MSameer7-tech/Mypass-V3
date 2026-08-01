from ui.widgets.base import BaseLabel
from ui.resources.styles.typography import Typography, TypographyToken
from PySide6.QtGui import QFont, QTextDocument

def apply_typography(widget, token: TypographyToken):
    # Base QFont configuration
    font = QFont(token.family)
    font.setPixelSize(token.size)
    font.setWeight(token.weight)
    
    if token.letter_spacing > 0:
        font.setLetterSpacing(QFont.AbsoluteSpacing, token.letter_spacing)
        
    widget.setFont(font)
    
    # Optional: We could handle line_height here if needed using QTextDocument on QLabel, 
    # but for simple labels, QFont is often sufficient. 
    # For now, we apply the core font properties.

class DisplayLabel(BaseLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        apply_typography(self, Typography.Display)

class TitleLabel(BaseLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        apply_typography(self, Typography.Title)

class HeadlineLabel(BaseLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        apply_typography(self, Typography.Headline)

class BodyLabel(BaseLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        apply_typography(self, Typography.Body)

class CaptionLabel(BaseLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        apply_typography(self, Typography.Caption)

class OverlineLabel(BaseLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        apply_typography(self, Typography.Overline)

# Backwards-compatible aliases
DisplayText = DisplayLabel
Title = TitleLabel
Headline = HeadlineLabel
Body = BodyLabel
Caption = CaptionLabel
Overline = OverlineLabel
Label = BodyLabel
