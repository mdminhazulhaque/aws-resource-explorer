# This Python file uses the following encoding: utf-8

import sys
import json
import boto3
import subprocess

from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QIcon

from ui_form import Ui_Window
import os

from config import AWS_REGIONS, AWS_ICON_REPLACEMENTS

class ResourceLoaderThread(QThread):
    resources_loaded = Signal(list)

    def __init__(self, profile_name, region_name):
        super().__init__()
        self.profile_name = profile_name
        self.region_name = region_name

    def run(self):
        boto3.setup_default_session(profile_name=self.profile_name)
        client = boto3.client('resourcegroupstaggingapi', region_name=self.region_name)
        try:
            resources = client.get_resources()['ResourceTagMappingList']
        except Exception as e:
            print(e)
            resources = []
        self.resources_loaded.emit(resources)

class CloneRepoThread(QThread):
    progress = Signal(str)
    finished = Signal(bool)

    def __init__(self, repo_url, clone_dir):
        super().__init__()
        self.repo_url = repo_url
        self.clone_dir = clone_dir
        os.makedirs(clone_dir, exist_ok=True)

    def run(self):
        try:
            # Check if the repository already exists
            self.progress.emit("Checking if repository already exists...")
            result = subprocess.run(['git', '-C', self.clone_dir, 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                self.progress.emit("Repository already cloned: awslabs/aws-icons-for-plantuml")
                self.finished.emit(True)
                return

            # Clone the repository if it doesn't exist
            self.progress.emit("Cloning repository...")
            subprocess.run(['git', 'clone', '--depth', '1', self.repo_url, self.clone_dir], check=True)
            self.progress.emit("Successfully cloned repository: awslabs/aws-icons-for-plantuml")
            self.finished.emit(True)
        except subprocess.CalledProcessError as e:
            self.progress.emit(f"An error occurred: {e}")
            self.finished.emit(False)

class Window(QMainWindow):
    def __init__(self, parent=None):
        self.AWS_ICONS_REPO = 'https://github.com/awslabs/aws-icons-for-plantuml'
        if os.name == 'nt':
            self.AWS_ICONS_PATH = os.path.join(os.getenv('APPDATA'), "aws-icons-for-plantuml")
        else:
            self.AWS_ICONS_PATH = os.path.join(os.path.expanduser("~"), ".aws-icons-for-plantuml")

        super().__init__(parent)
        self.ui = Ui_Window()
        self.ui.setupUi(self)
        self.setWindowTitle("AWS Resource Explorer")

        profiles = boto3.session.Session().available_profiles
        self.ui.aws_profile.addItems(profiles)
        self.ui.aws_region.addItems(AWS_REGIONS)

        self.ui.load.clicked.connect(self.load_resources)
        self.ui.close.clicked.connect(self.close)

        self.resource_loader = None

        self.clone_repo_thread = None
        self.clone_repo_thread = CloneRepoThread(self.AWS_ICONS_REPO, self.AWS_ICONS_PATH)
        self.clone_repo_thread.progress.connect(self.on_clone_update)
        self.clone_repo_thread.finished.connect(self.on_clone_finished)
        self.clone_repo_thread.start()

    def on_clone_update(self, message):
        self.statusBar().showMessage(message)

    def on_clone_finished(self, success):
        if success:
            self.statusBar().showMessage("Successfully cloned repository: awslabs/aws-icons-for-plantuml")
            self.icondb = self.load_icondb()
        else:
            self.statusBar().showMessage("Failed to clone repository: awslabs/aws-icons-for-plantuml")

    def load_icondb(self):
        with open(f"{self.AWS_ICONS_PATH}/dist/aws-icons-structurizr-theme.json", "r") as f:
            data = json.load(f)
            icons = {}
            for element in data["elements"]:
                if "icon" in element:
                    tag = element["tag"].lower()
                    icons[tag] = element["icon"]
                    # print("Loaded icon for:", tag)
            return icons

    def load_resources(self):
        self.ui.resources.clear()
        self.ui.resources.horizontalHeader().setVisible(False)
        self.ui.resources.horizontalHeader().setStretchLastSection(True)

        region_name = self.ui.aws_region.currentText().split(" ")[0]
        profile_name = self.ui.aws_profile.currentText()

        self.resource_loader = ResourceLoaderThread(profile_name, region_name)
        self.resource_loader.resources_loaded.connect(self.on_resources_loaded)
        self.resource_loader.start()
        self.ui.status.setText("Loading ...")

    def on_resources_loaded(self, resources):
        self.ui.resources.setRowCount(len(resources))
        self.ui.resources.setColumnCount(1)
        self.ui.resources.setHorizontalHeaderLabels(["Resource ARN"])
        self.ui.resources.setSortingEnabled(True)
        self.ui.resources.verticalHeader().setVisible(False)

        for i, resource in enumerate(resources):
            arn = resource['ResourceARN']
            item = QTableWidgetItem(arn)
            self.ui.resources.setItem(i, 0, item)

            service = arn.split(":")[2]
            service = AWS_ICON_REPLACEMENTS.get(service, service)

            icon = self.icondb.get(service)
            icon_path = f"{self.AWS_ICONS_PATH}/dist/{icon}"
            if icon:
                item.setIcon(QIcon(icon_path))

        self.ui.status.setText("Done!")

if __name__ == "__main__":    
    app = QApplication(sys.argv)
    window = Window()
    window.show()

    sys.exit(app.exec())
