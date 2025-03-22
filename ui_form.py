# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QHeaderView,
    QLabel, QMainWindow, QPushButton, QSizePolicy,
    QSpacerItem, QStatusBar, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_Window(object):
    def setupUi(self, Window):
        if not Window.objectName():
            Window.setObjectName(u"Window")
        Window.resize(800, 600)
        self.centralwidget = QWidget(Window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setFamilies([u"Fira Code"])
        font.setPointSize(14)
        self.label.setFont(font)

        self.horizontalLayout.addWidget(self.label)

        self.aws_profile = QComboBox(self.centralwidget)
        self.aws_profile.setObjectName(u"aws_profile")
        self.aws_profile.setFont(font)

        self.horizontalLayout.addWidget(self.aws_profile)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)

        self.horizontalLayout.addWidget(self.label_2)

        self.aws_region = QComboBox(self.centralwidget)
        self.aws_region.setObjectName(u"aws_region")
        self.aws_region.setFont(font)

        self.horizontalLayout.addWidget(self.aws_region)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.status = QLabel(self.centralwidget)
        self.status.setObjectName(u"status")

        self.horizontalLayout.addWidget(self.status)

        self.load = QPushButton(self.centralwidget)
        self.load.setObjectName(u"load")
        self.load.setFont(font)

        self.horizontalLayout.addWidget(self.load)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.resources = QTableWidget(self.centralwidget)
        self.resources.setObjectName(u"resources")
        self.resources.setFont(font)

        self.verticalLayout.addWidget(self.resources)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.close = QPushButton(self.centralwidget)
        self.close.setObjectName(u"close")
        self.close.setFont(font)

        self.horizontalLayout_2.addWidget(self.close)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        Window.setCentralWidget(self.centralwidget)
        self.status_bar = QStatusBar(Window)
        self.status_bar.setObjectName(u"status_bar")
        Window.setStatusBar(self.status_bar)

        self.retranslateUi(Window)

        QMetaObject.connectSlotsByName(Window)
    # setupUi

    def retranslateUi(self, Window):
        Window.setWindowTitle(QCoreApplication.translate("Window", u"Window", None))
        self.label.setText(QCoreApplication.translate("Window", u"AWS_PROFILE", None))
        self.label_2.setText(QCoreApplication.translate("Window", u"AWS_REGION", None))
        self.status.setText(QCoreApplication.translate("Window", u"...", None))
        self.load.setText(QCoreApplication.translate("Window", u"Load", None))
        self.close.setText(QCoreApplication.translate("Window", u"Close", None))
    # retranslateUi

