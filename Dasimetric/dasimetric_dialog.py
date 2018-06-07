# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DasimetricDialog
                                 A QGIS plugin
 The plugin calculate population using a dasimetric approach
                             -------------------
        begin                : 2018-03-07
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Nelson Mileu/IGOT
        email                : nmileu@campus.ul.pt
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from PyQt4 import QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from dasimetricdialogbase import Ui_DasimetricDialog
from qgiscombomanager import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dasimetric_dialog_base.ui'))


class DasimetricDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(DasimetricDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
	self.layerComboManager1 = VectorLayerCombo(self.LayercomboBox1,"",{"hasGeometry": True})
	self.fieldComboManager1 = FieldCombo(self.FieldcomboBox1, self.layerComboManager1)
	self.fieldComboManager3 = FieldCombo(self.FieldcomboBox3, self.layerComboManager1)
	self.layerComboManager2 = VectorLayerCombo(self.LayercomboBox2,"",{"hasGeometry": True})
	self.fieldComboManager2 = FieldCombo(self.FieldcomboBox2, self.layerComboManager2)
		
	self.browseButton.clicked.connect(self.browse)

    def browse(self):
        directory = QtGui.QFileDialog.getExistingDirectory(self, self.trUtf8(u"Base directory"))
        if directory:
            self.baseDirectory.setText(directory)
	
