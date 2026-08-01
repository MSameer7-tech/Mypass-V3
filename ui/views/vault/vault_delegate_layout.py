from dataclasses import dataclass
from PySide6.QtCore import QRect
from ui.views.vault.vault_delegate_metrics import VaultDelegateMetrics
from ui.resources.styles.typography import Typography

@dataclass
class VaultDelegateLayout:
    """
    Precomputed geometry for a vault list item.
    Ensures paint() is purely rendering logic.
    """
    bounds: QRect
    card_rect: QRect
    icon_rect: QRect
    title_rect: QRect
    username_rect: QRect
    url_rect: QRect
    favorite_star_rect: QRect
    
    @classmethod
    def calculate(cls, rect: QRect, has_favorite: bool) -> 'VaultDelegateLayout':
        # Card bounds inset
        card_rect = rect.adjusted(
            VaultDelegateMetrics.CARD_MARGIN_X,
            VaultDelegateMetrics.CARD_MARGIN_Y,
            -VaultDelegateMetrics.CARD_MARGIN_X,
            -VaultDelegateMetrics.CARD_MARGIN_Y
        )
        
        x = card_rect.x() + VaultDelegateMetrics.CARD_PADDING_X
        y = card_rect.y() + VaultDelegateMetrics.CARD_PADDING_Y
        
        # Icon (40x40 container)
        icon_y = card_rect.y() + (card_rect.height() - VaultDelegateMetrics.ICON_CONTAINER_SIZE) // 2
        icon_rect = QRect(x, icon_y, VaultDelegateMetrics.ICON_CONTAINER_SIZE, VaultDelegateMetrics.ICON_CONTAINER_SIZE)
        
        x += VaultDelegateMetrics.ICON_CONTAINER_SIZE + VaultDelegateMetrics.ICON_MARGIN_RIGHT
        
        # Favorite Star (Right aligned inside card)
        star_rect = QRect()
        right_margin = card_rect.right() - VaultDelegateMetrics.CARD_PADDING_X
        
        if has_favorite:
            star_size = VaultDelegateMetrics.FAVORITE_STAR_SIZE
            star_y = card_rect.y() + VaultDelegateMetrics.CARD_PADDING_Y
            star_rect = QRect(right_margin - star_size, star_y, star_size, star_size)
            right_margin -= (star_size + 8)
            
        # Title, Username, and URL (3 lines)
        title_rect = QRect(x, y, right_margin - x, Typography.Headline.size + 4)
        
        username_y = title_rect.bottom() + VaultDelegateMetrics.TITLE_TO_SUBTITLE_GAP
        username_rect = QRect(x, username_y, right_margin - x, Typography.Body.size + 4)
        
        url_y = username_rect.bottom() + VaultDelegateMetrics.SUBTITLE_TO_META_GAP
        url_rect = QRect(x, url_y, right_margin - x, Typography.Caption.size + 4)
        
        return cls(
            bounds=rect,
            card_rect=card_rect,
            icon_rect=icon_rect,
            title_rect=title_rect,
            username_rect=username_rect,
            url_rect=url_rect,
            favorite_star_rect=star_rect
        )
