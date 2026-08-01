from ui.resources.styles.spacing import Spacing
from ui.resources.styles.metrics import Metrics

class Layout:
    # Pane Margins
    TOOLBAR_MARGIN = Spacing.XL      # 24
    SIDEBAR_MARGIN = Spacing.XL      # 24
    CONTENT_MARGIN = Spacing.XL      # 24
    DETAILS_MARGIN = Spacing.XL      # 24
    DIALOG_PADDING = Spacing.XL      # 24
    
    # Constraints
    CONTENT_MAX_WIDTH = 1440
    DETAILS_MIN_WIDTH = 360
    SIDEBAR_MIN_WIDTH = 240
    
    # Components
    CARD_PADDING = Metrics.CARD_PADDING
    DETAILS_CARD_PADDING = 20
    DETAILS_CARD_RADIUS = 12
    DETAILS_SECTION_GAP = 24
    DETAILS_ROW_GAP = 12
    
    # Vertical Rhythm
    SECTION_SPACING = Spacing.XL     # 24
    TITLE_TO_SUBTITLE = Spacing.L    # 16
    SUBTITLE_TO_CONTENT = Spacing.XL # 24
    
    # Generic Alignments
    LIST_ITEM_GAP = Spacing.S        # 8
    BUTTON_GROUP_GAP = Spacing.M     # 12
    INLINE_GAP = Spacing.S           # 8
    GRID_GAP = Spacing.L             # 16
