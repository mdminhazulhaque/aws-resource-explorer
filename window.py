# This Python file uses the following encoding: utf-8

import sys
import boto3
import signal
import os

from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QKeySequence, QShortcut, QIcon

from ui_form import Ui_Window
import resources_rc  # Import the compiled resource file

# AWS Regions
AWS_REGIONS = [
    "us-east-1 (N. Virginia)",
    "us-east-2 (Ohio)",
    "us-west-1 (N. California)",
    "us-west-2 (Oregon)",
    "ap-south-1 (Mumbai)",
    "ap-northeast-3 (Osaka)",
    "ap-northeast-2 (Seoul)",
    "ap-southeast-1 (Singapore)",
    "ap-southeast-2 (Sydney)",
    "ap-northeast-1 (Tokyo)",
    "ca-central-1 (Central)",
    "eu-central-1 (Frankfurt)",
    "eu-west-1 (Ireland)",
    "eu-west-2 (London)",
    "eu-west-3 (Paris)",
    "eu-north-1 (Stockholm)",
    "sa-east-1 (São Paulo)",
]

class ResourceLoaderThread(QThread):
    resources_loaded = Signal(list)

    def __init__(self, profile_name, region_name):
        super().__init__()
        self.profile_name = profile_name
        self.region_name = region_name

    def run(self):
        boto3.setup_default_session(profile_name=self.profile_name)
        client = boto3.client('resourcegroupstaggingapi', region_name=self.region_name)
        
        all_resources = []
        pagination_token = None
        
        try:
            while True:
                # Prepare API call parameters
                params = {}
                if pagination_token:
                    params['PaginationToken'] = pagination_token
                
                # Make the API call
                response = client.get_resources(**params)
                
                # Add resources from this page
                page_resources = response.get('ResourceTagMappingList', [])
                all_resources.extend(page_resources)
                
                # Check if there are more pages
                pagination_token = response.get('PaginationToken')
                if not pagination_token:
                    break
                    
                print(f"Fetched {len(page_resources)} resources, total so far: {len(all_resources)}")
                
        except Exception as e:
            print(f"Error fetching resources: {e}")
            
        print(f"Total resources fetched: {len(all_resources)}")
        self.resources_loaded.emit(all_resources)

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Window()
        self.ui.setupUi(self)
        
        # Set window title after UI setup to ensure it's not overridden
        self.setWindowTitle("AWS Resource Explorer")
        
        # Set window icon from QRC resources with fallback
        icon = QIcon(":/icon.png")
        if icon.isNull():
            # Fallback to file system if QRC resource fails
            icon = QIcon("icon.png")
        
        self.setWindowIcon(icon)

        profiles = boto3.session.Session().available_profiles
        
        # Check if no profiles are available
        if not profiles:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("AWS Configuration Required")
            msg.setText("No AWS profiles found!")
            msg.setInformativeText("Please set up AWS configuration before using this application")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

        self.ui.aws_profile.addItems(profiles)
        self.ui.aws_region.addItems(AWS_REGIONS)

        self.ui.load.clicked.connect(self.load_resources)
        self.ui.close.clicked.connect(self.close)

        # Clear table when profile or region changes
        self.ui.aws_profile.currentTextChanged.connect(self.clear_table)
        self.ui.aws_region.currentTextChanged.connect(self.clear_table)

        self.resource_loader = None
        self.all_resources = []  # Store all resources for filtering

        # Connect filter box to search functionality
        self.ui.filter.textChanged.connect(self.filter_resources)

        # Setup keyboard shortcuts
        self.setup_shortcuts()
        
        # Setup signal handlers
        self.setup_signal_handlers()

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        print(f"Received signal {signum}, closing application...")
        self.close()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for the application"""
        # Platform-specific quit shortcuts
        if os.name == 'nt':  # Windows
            self.quit_shortcut = QShortcut(QKeySequence("Alt+F4"), self)
        else:  # macOS and Linux
            self.quit_shortcut = QShortcut(QKeySequence("Cmd+Q"), self)
        
        self.quit_shortcut.activated.connect(self.close)

    def clear_table(self):
        """Clear the resources table and filter"""
        self.ui.resources.clear()
        self.ui.resources.setRowCount(0)
        if hasattr(self, 'ui') and hasattr(self.ui, 'filter'):
            self.ui.filter.clear()
        self.all_resources = []
        self.statusBar().showMessage("Select profile and region, then click Load")

    def set_ui_enabled(self, enabled):
        """Enable or disable UI controls during loading"""
        self.ui.aws_profile.setEnabled(enabled)
        self.ui.aws_region.setEnabled(enabled)
        self.ui.filter.setEnabled(enabled)
        self.ui.load.setEnabled(enabled)

    def closeEvent(self, event):
        """Handle window close event and cleanup threads"""
        if self.resource_loader and self.resource_loader.isRunning():
            # Re-enable UI controls before closing
            self.set_ui_enabled(True)
            # Wait for the thread to finish before closing
            self.resource_loader.wait(3000)  # Wait up to 3 seconds
            if self.resource_loader.isRunning():
                # If still running, terminate it
                self.resource_loader.terminate()
                self.resource_loader.wait()
        event.accept()

    def load_resources(self):
        # Prevent starting multiple threads
        if self.resource_loader and self.resource_loader.isRunning():
            return
            
        # Disable UI controls during loading
        self.set_ui_enabled(False)
            
        # Clear filter box and resources
        self.ui.filter.clear()
        self.all_resources = []
                        
        self.ui.resources.clear()
        self.ui.resources.horizontalHeader().setVisible(False)
        self.ui.resources.horizontalHeader().setStretchLastSection(True)

        region_name = self.ui.aws_region.currentText().split(" ")[0]
        profile_name = self.ui.aws_profile.currentText()

        self.resource_loader = ResourceLoaderThread(profile_name, region_name)
        self.resource_loader.resources_loaded.connect(self.on_resources_loaded)
        self.resource_loader.finished.connect(self.on_thread_finished)
        self.resource_loader.start()
        self.statusBar().showMessage("Loading ...")

    def on_thread_finished(self):
        """Handle thread cleanup when finished"""
        # Re-enable UI controls
        self.set_ui_enabled(True)
        
        if self.resource_loader:
            self.resource_loader.deleteLater()
            self.resource_loader = None

    def on_resources_loaded(self, resources):
        # Store all resources for filtering
        self.all_resources = resources
        
        # Display all resources initially
        self.display_resources(resources)

    def display_resources(self, resources):
        """Display the given list of resources in the table"""
        self.ui.resources.setRowCount(len(resources))
        self.ui.resources.setColumnCount(1)
        self.ui.resources.setHorizontalHeaderLabels(["Resource ARN"])
        self.ui.resources.setSortingEnabled(True)
        self.ui.resources.verticalHeader().setVisible(False)

        for i, resource in enumerate(resources):
            arn = resource['ResourceARN']
            item = QTableWidgetItem(arn)
            self.ui.resources.setItem(i, 0, item)

        self.statusBar().showMessage(f"Done! ({len(resources)} resources)")

    def filter_resources(self):
        """Filter resources based on search text"""
        if not hasattr(self, 'all_resources') or not self.all_resources:
            return
            
        search_text = self.ui.filter.text().lower().strip()
        
        if not search_text:
            # Show all resources if search is empty
            filtered_resources = self.all_resources
        else:
            # Filter resources containing the search text
            filtered_resources = [
                resource for resource in self.all_resources
                if search_text in resource['ResourceARN'].lower()
            ]
        
        self.display_resources(filtered_resources)

if __name__ == "__main__":    
    app = QApplication(sys.argv)
    
    # Set application properties (this affects dock/taskbar name)
    app.setApplicationName("AWS Resource Explorer")
    app.setApplicationDisplayName("AWS Resource Explorer")
    app.setOrganizationName("Self")
    app.setApplicationVersion("1.0")
    
    # Set application icon (affects all windows and dock/taskbar)
    app_icon = QIcon(":/icon.png")
    if app_icon.isNull():
        app_icon = QIcon("icon.png")
    
    app.setWindowIcon(app_icon)
    
    window = Window()
    window.show()

    sys.exit(app.exec())
