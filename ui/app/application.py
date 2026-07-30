from PySide6.QtWidgets import QApplication
from utils.constants import APP_NAME, APP_VERSION

class MyPassApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName(APP_NAME)
        self.setApplicationVersion(APP_VERSION)
        self.setOrganizationName("MyPassOrg")
        self.setOrganizationDomain("mypass.local")
        
        # We will load resources, styles, and high DPI configuration here
        # High DPI scaling is enabled by default in Qt6, but we can set specific attributes if needed
        
