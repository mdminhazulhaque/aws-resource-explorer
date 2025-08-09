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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
    QTableWidget, QTableWidgetItem, QWidget)

class Ui_Window(object):
    def setupUi(self, Window):
        if not Window.objectName():
            Window.setObjectName(u"Window")
        Window.resize(848, 434)
        self.centralwidget = QWidget(Window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 1, 1, 2)

        self.aws_profile = QComboBox(self.centralwidget)
        self.aws_profile.setObjectName(u"aws_profile")

        self.gridLayout.addWidget(self.aws_profile, 1, 1, 1, 2)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 2, 1, 1, 2)

        self.aws_region = QComboBox(self.centralwidget)
        self.aws_region.setObjectName(u"aws_region")

        self.gridLayout.addWidget(self.aws_region, 3, 1, 1, 2)

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 4, 1, 1, 1)

        self.filter = QLineEdit(self.centralwidget)
        self.filter.setObjectName(u"filter")

        self.gridLayout.addWidget(self.filter, 5, 1, 1, 2)

        self.verticalSpacer = QSpacerItem(28, 467, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 6, 2, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.load = QPushButton(self.centralwidget)
        self.load.setObjectName(u"load")

        self.horizontalLayout.addWidget(self.load)

        self.close = QPushButton(self.centralwidget)
        self.close.setObjectName(u"close")

        self.horizontalLayout.addWidget(self.close)


        self.gridLayout.addLayout(self.horizontalLayout, 7, 1, 1, 2)

        self.resources = QTableWidget(self.centralwidget)
        self.resources.setObjectName(u"resources")

        self.gridLayout.addWidget(self.resources, 0, 0, 8, 1)

        Window.setCentralWidget(self.centralwidget)
        self.statusBar = QStatusBar(Window)
        self.statusBar.setObjectName(u"statusBar")
        Window.setStatusBar(self.statusBar)

        self.retranslateUi(Window)

        QMetaObject.connectSlotsByName(Window)
    # setupUi

    def retranslateUi(self, Window):
        Window.setWindowTitle(QCoreApplication.translate("Window", u"Window", None))
        self.label.setText(QCoreApplication.translate("Window", u"AWS_PROFILE", None))
        self.label_2.setText(QCoreApplication.translate("Window", u"AWS_REGION", None))
        self.label_3.setText(QCoreApplication.translate("Window", u"Filter", None))
        self.load.setText(QCoreApplication.translate("Window", u"Load", None))
        self.close.setText(QCoreApplication.translate("Window", u"Close", None))
    # retranslateUi

