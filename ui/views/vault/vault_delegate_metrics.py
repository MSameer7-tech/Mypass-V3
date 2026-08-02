from ui.resources.styles.layout_constants import Layout
from ui.resources.styles.metrics import Metrics

class VaultDelegateMetrics:
    """
    Design constants for rendering the VaultItemDelegate cards.
    Phase 2.2 Card Metrics: 74px card height (82px row height with 4px margins), 12px radius, 16px/12px padding.
    """
    ROW_HEIGHT = 82             # 74px card height + 8px gap
    CARD_MARGIN_X = 16          # 16px left & right margins
    CARD_MARGIN_Y = 4           # 4px top/bottom margin = 8px vertical gap
    CARD_RADIUS = 12
    CARD_PADDING_X = 16         # 16px horizontal internal padding
    CARD_PADDING_Y = 12         # 12px vertical internal padding
    
    ICON_CONTAINER_SIZE = 44
    ICON_SIZE = 26
    ICON_RADIUS = 10
    ICON_MARGIN_RIGHT = 12
    
    TITLE_TO_SUBTITLE_GAP = 2
    SUBTITLE_TO_META_GAP = 2
    
    FAVORITE_STAR_SIZE = 14     # Upper right star icon size
    FAVORITE_MARGIN_LEFT = 8
