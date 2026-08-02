from PySide6.QtWidgets import QStyledItemDelegate, QStyle
from PySide6.QtCore import Qt, QRect, QPoint, QSize
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QIcon, QPixmap, QPainterPath

from ui.models.roles import VaultRoles
from ui.views.vault.vault_delegate_metrics import VaultDelegateMetrics
from ui.views.vault.vault_delegate_layout import VaultDelegateLayout
from ui.resources.styles.themes import ThemeManager
from ui.resources.styles.typography import Typography

class VaultItemDelegate(QStyledItemDelegate):
    """
    Highly performant delegate for painting vault list items.
    Contains strictly no business logic.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def sizeHint(self, option, index) -> QSize:
        return QSize(option.rect.width(), VaultDelegateMetrics.ROW_HEIGHT)
        
    def paint(self, painter: QPainter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 1. Fetch Data
        title = index.data(VaultRoles.TitleRole) or ""
        username = index.data(VaultRoles.UsernameRole) or ""
        url = index.data(VaultRoles.UrlRole) or ""
        icon_val = index.data(VaultRoles.IconRole)
        is_favorite = index.data(VaultRoles.FavoriteRole) or False
        highlighted_ranges = index.data(VaultRoles.HighlightedRangesRole) or {}
        
        # 2. Precompute Layout
        layout = VaultDelegateLayout.calculate(option.rect, is_favorite)
        
        # 3. Visual State
        is_selected = option.state & QStyle.State_Selected
        is_hovered = option.state & QStyle.State_MouseOver
        is_focused = option.state & QStyle.State_HasFocus
        
        card_bg_color = QColor("#18191F")
        border_color = Qt.NoPen
        
        if is_selected:
            card_bg_color = QColor("#2B2D38")
        elif is_hovered:
            card_bg_color = QColor("#20222B")
            
        # Draw Card Background (Borderless)
        painter.setPen(Qt.NoPen)
        painter.setBrush(card_bg_color)
        painter.drawRoundedRect(layout.card_rect, VaultDelegateMetrics.CARD_RADIUS, VaultDelegateMetrics.CARD_RADIUS)
            
        if is_focused and not is_selected:
            pen = QPen(QColor(ThemeManager.colors().accent), 2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(layout.card_rect.adjusted(1, 1, -1, -1), VaultDelegateMetrics.CARD_RADIUS, VaultDelegateMetrics.CARD_RADIUS)
            
        # 4. Draw Icon / Favicon Container (44x44, radius 10)
        painted_icon = False

        if icon_val:
            if isinstance(icon_val, QIcon):
                pixmap = icon_val.pixmap(layout.icon_rect.size())
            elif isinstance(icon_val, QPixmap):
                pixmap = icon_val
            else:
                pixmap = None
                
            if pixmap and not pixmap.isNull():
                painter.save()
                clip_path = QPainterPath()
                clip_path.addRoundedRect(layout.icon_rect, VaultDelegateMetrics.ICON_RADIUS, VaultDelegateMetrics.ICON_RADIUS)
                painter.setClipPath(clip_path)
                painter.drawPixmap(layout.icon_rect, pixmap)
                painter.restore()
                painted_icon = True
                
        if not painted_icon:
            # Fallback Monogram
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(ThemeManager.colors().background))
            painter.drawRoundedRect(layout.icon_rect, VaultDelegateMetrics.ICON_RADIUS, VaultDelegateMetrics.ICON_RADIUS)
            first_char = title[0].upper() if title else "?"
            icon_font = QFont(Typography.Headline.family, 15, QFont.Bold)
            painter.setFont(icon_font)
            painter.setPen(QColor(ThemeManager.colors().text_secondary))
            painter.drawText(layout.icon_rect, Qt.AlignCenter, first_char)
        
        # 5. Helper to draw highlighted text
        def draw_highlighted_text(rect, text, ranges, font, default_color):
            painter.setFont(font)
            text_color = default_color
            if not ranges:
                painter.setPen(text_color)
                painter.drawText(rect, Qt.AlignLeft | Qt.AlignVCenter, text)
                return
                
            fm = painter.fontMetrics()
            highlight_bg = QColor(ThemeManager.colors().warning)
            
            for start_idx, length in ranges:
                prefix = text[:start_idx]
                match_text = text[start_idx:start_idx+length]
                prefix_width = fm.horizontalAdvance(prefix)
                match_width = fm.horizontalAdvance(match_text)
                bg_rect = QRect(rect.x() + prefix_width, rect.y() + (rect.height() - fm.height()) // 2, match_width, fm.height())
                
                painter.setPen(Qt.NoPen)
                painter.setBrush(highlight_bg)
                painter.drawRect(bg_rect)
            
            painter.setPen(text_color)
            painter.drawText(rect, Qt.AlignLeft | Qt.AlignVCenter, text)

        # 6. Draw Title (14px SemiBold)
        title_font = QFont(Typography.Headline.family, 14, QFont.DemiBold)
        t_color = QColor("#FFFFFF") if is_selected else QColor("#E2E8F0")
        draw_highlighted_text(layout.title_rect, title, highlighted_ranges.get(VaultRoles.TitleRole, []), title_font, t_color)
        
        # 7. Draw Username (13px Regular)
        user_font = QFont(Typography.Body.family, 13, QFont.Normal)
        u_color = QColor("#9498A6")
        draw_highlighted_text(layout.username_rect, username, highlighted_ranges.get(VaultRoles.UsernameRole, []), user_font, u_color)
        
        # 8. Draw Timestamp (12px Muted: Always "Last used, X ago")
        modified_at = index.data(VaultRoles.ModifiedRole) or ""
        created_at = index.data(VaultRoles.CreatedRole) or ""
        timestamp_text = "Last used, 2 min ago"
        if modified_at and "min" in str(modified_at):
            timestamp_text = f"Last used, {modified_at}"
        elif created_at:
            timestamp_text = f"Last used, 2 min ago"
            
        meta_font = QFont(Typography.Caption.family, 12, QFont.Normal)
        meta_color = QColor("#71717A")
        painter.setFont(meta_font)
        painter.setPen(meta_color)
        painter.drawText(layout.url_rect, Qt.AlignLeft | Qt.AlignVCenter, timestamp_text)
        
        # 9. Draw Favorite Star Badge (Upper-right corner, 14px size)
        if is_favorite:
            star_font = QFont(Typography.Body.family, 12)
            painter.setFont(star_font)
            painter.setPen(QColor("#F59E0B"))
            painter.drawText(layout.favorite_star_rect, Qt.AlignCenter, "★")
            
        painter.restore()
