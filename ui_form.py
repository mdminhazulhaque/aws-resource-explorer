# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.9.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QGridLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QProgressBar, QPushButton,
    QSizePolicy, QSpacerItem, QSplitter, QStatusBar,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_Window(object):
    def setupUi(self, Window):
        if not Window.objectName():
            Window.setObjectName(u"Window")
        Window.resize(800, 600)
        self.centralwidget = QWidget(Window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.resources = QTableWidget(self.splitter)
        self.resources.setObjectName(u"resources")
        self.splitter.addWidget(self.resources)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBox = QGroupBox(self.layoutWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.aws_profile = QComboBox(self.groupBox)
        self.aws_profile.setObjectName(u"aws_profile")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.aws_profile)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.aws_region = QComboBox(self.groupBox)
        self.aws_region.setObjectName(u"aws_region")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.aws_region)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.layoutWidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.filter = QLineEdit(self.groupBox_2)
        self.filter.setObjectName(u"filter")

        self.verticalLayout_2.addWidget(self.filter)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.progressBar = QProgressBar(self.layoutWidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)
        self.progressBar.setTextVisible(False)
        self.progressBar.setOrientation(Qt.Horizontal)
        self.progressBar.setInvertedAppearance(False)

        self.verticalLayout.addWidget(self.progressBar)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.load = QPushButton(self.layoutWidget)
        self.load.setObjectName(u"load")

        self.horizontalLayout.addWidget(self.load)

        self.close = QPushButton(self.layoutWidget)
        self.close.setObjectName(u"close")

        self.horizontalLayout.addWidget(self.close)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.splitter.addWidget(self.layoutWidget)

        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        Window.setCentralWidget(self.centralwidget)
        self.statusBar = QStatusBar(Window)
        self.statusBar.setObjectName(u"statusBar")
        Window.setStatusBar(self.statusBar)

        self.retranslateUi(Window)

        QMetaObject.connectSlotsByName(Window)
    # setupUi

    def retranslateUi(self, Window):
        Window.setWindowTitle(QCoreApplication.translate("Window", u"AWS Resource Explorer", None))
        self.groupBox.setTitle(QCoreApplication.translate("Window", u"Settings", None))
        self.label.setText(QCoreApplication.translate("Window", u"AWS_PROFILE", None))
        self.label_2.setText(QCoreApplication.translate("Window", u"AWS_REGION", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Window", u"Filter", None))
        self.load.setText(QCoreApplication.translate("Window", u"Load", None))
        self.close.setText(QCoreApplication.translate("Window", u"Close", None))
    # retranslateUi

