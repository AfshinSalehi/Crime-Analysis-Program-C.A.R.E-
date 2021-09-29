# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Care
                                 A QGIS plugin
 Crime analysis using radial effectiveness
                              -------------------
        begin                : 2016-04-17
        git sha              : $Format:%H$
        copyright         : (C) 2016-18 by Afshin Salehi
        email                : Salehi@consultant.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is NOT a free software; you CANNOT redistribute it and/or modify  *

"""
import os.path

import processing
import qgis.core
import qgis.utils
# Initialize Qt resources from file resources.py
import resources
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Import the code for the dialog
from care_main_dialog import CareDialog
import DecisionMaker as DM
import PrintList
import ReportGenerator as RG
import reportlab
from reportlab.pdfgen import canvas
from reportlab.graphics import charts
from reportlab.graphics.charts import piecharts
from reportlab.graphics.shapes import *
# for importing new fonts
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
# must change in final version
output = 'print_pdf-1'
output_path = os.path.expanduser('~/Desktop/x')
PLUGIN_PATH = os.path.expanduser('~/.qgis2/python/plugins/Care/')
class Care:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        qgis.core.QgsApplication.initQgis()
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Care_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&C.A.R.E')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Care')
        self.toolbar.setObjectName(u'Care')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Care', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = CareDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Care/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'C.A.R.E'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&C.A.R.E'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def run(self):
        """Run method that performs all the real work"""
        # region adding vector layers
        layers = [layer for layer in self.iface.legendInterface().layers() if
                  layer.type() == qgis.core.QgsMapLayer.VectorLayer]
        layer_list = []
        for layer in layers:
            if layer.type() == qgis.core.QgsMapLayer.VectorLayer:
                layer_list.append(layer.name())
            else:
                continue
        # endregion

        # region polygon combo boxes
        self.pgInput = self.dlg.comboBox_input_polygon
        self.pgInput.clear()
        self.pgInput.addItems(layer_list)
        self.pgFactor = self.dlg.comboBox__factor_polygon
        self.pgLyr = self.dlg.comboBox_layer_polygon

        def pgField_select():
            self.pgFactor.clear()
            self.pgLyr.clear()
            fields = [field.name() for field in layers[self.pgInput.currentIndex()].pendingFields()]
            self.pgFactor.addItems(fields)
            self.pgLyr.addItems(fields)

        self.pgInput.currentIndexChanged.connect(pgField_select)
        # endregion

        # region polyline '' ''
        self.plInput = self.dlg.comboBox__input_polyline
        self.plInput.clear()
        self.plInput.addItems(layer_list)
        self.plFactor = self.dlg.comboBox__factor_polyline
        self.plLyr = self.dlg.comboBox__layer_polyline

        def plField_select():
            self.plFactor.clear()
            self.plLyr.clear()
            fields = [field.name() for field in layers[self.plInput.currentIndex()].pendingFields()]
            self.plFactor.addItems(fields)
            self.plLyr.addItems(fields)

        self.plInput.currentIndexChanged.connect(plField_select)
        # endregion

        # region point
        self.pInput = self.dlg.comboBox_input_point
        self.pInput.clear()
        self.pInput.addItems(layer_list)
        self.pFactor = self.dlg.comboBox_factor_point
        self.pLyr = self.dlg.comboBox__layer_point

        def pField_select():
            self.pFactor.clear()
            self.pLyr.clear()
            selectedLayerIndex = self.pInput.currentIndex()
            selectedLayer = layers[selectedLayerIndex]
            fields = [field.name() for field in selectedLayer.pendingFields()]
            self.pFactor.addItems(fields)
            self.pLyr.addItems(fields)

        self.pInput.currentIndexChanged.connect(pField_select)
        # endregion

        # region crime inputs and crime instance
        self.cInput = self.dlg.comboBox_input_Crime
        self.cInput.clear()
        self.cInput.addItems(layer_list)
        # endregion

        # region horizontal sliders and all the actions
        self.flr = self.dlg.horizontalSlider_firstloop

        self.slr = self.dlg.horizontalSlider_secondloop

        self.tlr = self.dlg.horizontalSlider_thirdloop
        # endregion

        # line edit instance
        self.le = self.dlg.lineEdit_output

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # get crime points as list
            self.pic = self.cInput.currentIndex()  # selected crime layer inside combo-box

            # region creation of all buffers buff, buff2, buff 3
            buff = processing.runalg('qgis:fixeddistancebuffer', layers[self.pic],
                                     10 + (10 * (int(self.dlg.lcdNumber_1.value())) / 100), 5, True, None)
            self.buffLyr = qgis.core.QgsVectorLayer(buff['OUTPUT'], "buffer- 1", "ogr")
            # qgis.core.QgsMapLayerRegistry.instance().addMapLayer(self.buffLyr) #SHOWS BUFFER 1

            buff2 = processing.runalg('qgis:fixeddistancebuffer', layers[self.pic],
                                      30 + (30 * (int(self.dlg.lcdNumber_2.value())) / 100), 5, True, None)

            buff3 = processing.runalg('qgis:fixeddistancebuffer', layers[self.pic],
                                      60 + (60 * (int(self.dlg.lcdNumber_3.value())) / 100), 5, True, None)
            # endregion

            # region select elements by first ring (buffLyr) and save the selected elements to lists
            buf_1_PolygonSel = processing.runalg("qgis:selectbylocation", layers[self.pgInput.currentIndex()],
                                                 self.buffLyr, ['touches', 'intersects'], 0, 0)
            buf_1_Polygon = []
            self.saveToList(layers[self.pgInput.currentIndex()], buf_1_Polygon,
                            self.pgLyr.currentText(), self.pgFactor.currentText())


            buf_1_PolylineSel = processing.runalg("qgis:selectbylocation", layers[self.plInput.currentIndex()],
                                                  self.buffLyr, ['touches', 'crosses', 'intersects'], 0, 0)
            buf_1_Polyline = []
            self.saveToList(layers[self.plInput.currentIndex()], buf_1_Polyline,
                            self.plLyr.currentText(), self.plFactor.currentText())

            buf_1_PointSel = processing.runalg("qgis:selectbylocation", layers[self.pInput.currentIndex()],
                                               self.buffLyr, ['within'], 0, 0)
            buf_1_Point = []
            self.saveToList(layers[self.pInput.currentIndex()], buf_1_Point,
                            self.pLyr.currentText(), self.pFactor.currentText())
            # endregion

            # region select elements by second ring (ringLyr2) and save the selected elements to lists
            dif2 = processing.runalg('qgis:difference', buff2['OUTPUT'], buff['OUTPUT'], False, None)
            self.ringLyr2 = qgis.core.QgsVectorLayer(dif2['OUTPUT'], "Ring- 2", "ogr")
            # qgis.core.QgsMapLayerRegistry.instance().addMapLayer(self.ringLyr2) #SHOWS Ring 2

            buf_2_PolygonSel = processing.runalg("qgis:selectbylocation", layers[self.pgInput.currentIndex()],
                                                 self.ringLyr2, ['touches', 'intersects'], 0, 0)
            buf_2_Polygon = []
            self.saveToList(layers[self.pgInput.currentIndex()], buf_2_Polygon,
                            self.pgLyr.currentText(), self.pgFactor.currentText())

            buf_2_PolylineSel = processing.runalg("qgis:selectbylocation", layers[self.plInput.currentIndex()],
                                                  self.ringLyr2, ['touches', 'crosses', 'intersects'], 0, 0)
            buf_2_Polyline = []
            self.saveToList(layers[self.plInput.currentIndex()], buf_2_Polyline,
                            self.plLyr.currentText(), self.plFactor.currentText())

            buf_2_PointSel = processing.runalg("qgis:selectbylocation", layers[self.pInput.currentIndex()],
                                               self.ringLyr2, ['within'], 0, 0)
            buf_2_Point = []
            self.saveToList(layers[self.pInput.currentIndex()], buf_2_Point,
                            self.pLyr.currentText(), self.pFactor.currentText())
            # endregion

            # region select elements by second ring (ringLyr3) and save the selected elements to lists
            dif3 = processing.runalg('qgis:difference', buff3['OUTPUT'], buff2['OUTPUT'], False, None)
            self.ringLyr3 = qgis.core.QgsVectorLayer(dif3['OUTPUT'], "Ring- 3", "ogr")
            # qgis.core.QgsMapLayerRegistry.instance().addMapLayer(self.ringLyr3) #SHOWS Ring 3

            buf_3_PolygonSel = processing.runalg("qgis:selectbylocation", layers[self.pgInput.currentIndex()],
                                                 self.ringLyr3, ['touches', 'intersects'], 0, 0)
            buf_3_Polygon = []
            self.saveToList(layers[self.pgInput.currentIndex()], buf_3_Polygon,
                            self.pgLyr.currentText(), self.pgFactor.currentText())

            buf_3_PolylineSel = processing.runalg("qgis:selectbylocation", layers[self.plInput.currentIndex()],
                                                  self.ringLyr3, ['touches', 'crosses', 'intersects'], 0, 0)
            buf_3_Polyline = []
            self.saveToList(layers[self.plInput.currentIndex()], buf_3_Polyline,
                            self.plLyr.currentText(), self.plFactor.currentText())

            buf_3_PointSel = processing.runalg("qgis:selectbylocation", layers[self.pInput.currentIndex()],
                                               self.ringLyr3, ['within'], 0, 0)
            buf_3_Point = []
            self.saveToList(layers[self.pInput.currentIndex()], buf_3_Point,
                            self.pLyr.currentText(), self.pFactor.currentText())
            # endregion

            # region select elements by overall buffer and save the selected elements to lists
            self.overall = qgis.core.QgsVectorLayer(buff3['OUTPUT'], "Overall buffer", "ogr")
            # qgis.core.QgsMapLayerRegistry.instance().addMapLayer(self.Overall) #SHOWS Overall buffer

            overall_PolygonSel = processing.runalg("qgis:selectbylocation", layers[self.pgInput.currentIndex()],
                                                 self.overall, ['touches', 'intersects'], 0, 0)
            overall_Polygon = []
            self.saveToList(layers[self.pgInput.currentIndex()], overall_Polygon,
                            self.pgLyr.currentText(), self.pgFactor.currentText())

            overall_PolylineSel = processing.runalg("qgis:selectbylocation", layers[self.plInput.currentIndex()],
                                                  self.overall, ['touches', 'crosses', 'intersects'], 0, 0)
            overall_Polyline = []
            self.saveToList(layers[self.plInput.currentIndex()], overall_Polyline,
                            self.plLyr.currentText(), self.plFactor.currentText())

            overall_PointSel = processing.runalg("qgis:selectbylocation", layers[self.pInput.currentIndex()],
                                               self.overall, ['within'], 0, 0)
            overall_Point = []
            self.saveToList(layers[self.pInput.currentIndex()], overall_Point,
                            self.pLyr.currentText(), self.pFactor.currentText())
            # endregion

            # region canvas/output initialization

            # IF THE DIRECTORY NOT EXISTED CREATES A NEW ONE AND BACKWARDS.
            try:
                os.makedirs(output_path)
            except OSError:
                pass
            c = canvas.Canvas(output_path + '/' + output + '.pdf')
            # endregion

            # self.le.setText(str(buf_1_Point)) #debugging
            listOfAllFeatures = [buf_1_Polygon, buf_1_Polyline, buf_1_Point, buf_2_Polygon, buf_2_Polyline, buf_2_Point, buf_3_Polygon, buf_3_Polyline, buf_3_Point, overall_Polygon, overall_Polyline, overall_Point]


            self.DMFeatures(listOfAllFeatures)
            self.list_of_outputs = []

            self.DMFeatures_desicion(listOfAllFeatures)
            self.DMFeatures_final(self.list_of_outputs)

            self.le.setText(str(self.list_of_outputs))#debugging

            PrintList.printList(self.list_of_outputs)#debugging



            # region deselect all
            for layer in layers:
                if layer.type() == layer.VectorLayer:
                    layer.removeSelection()
            # endregion

            # region input for pdf generation
            PluginInput = [self.pgInput.currentText(), self.pgLyr.currentText(),self.pgFactor.currentText(),
                           self.plInput.currentText(), self.plLyr.currentText(), self.plFactor.currentText(),
                           self.pInput.currentText(), self.pLyr.currentText(), self.pFactor.currentText()]
            RG.print_pdf(c, PluginInput, self.list_of_outputs)#debugging
            # region Report Generation

            c.showPage()
            c.save()
            #endregion

    def saveToList(self, layer, EmptyList, LyrCombo, FactorCombo):
        for feat in layer.selectedFeatures():
            layerField = feat[LyrCombo].encode('utf-8', 'ignore')
            factorField = str(feat[FactorCombo])
            EmptyList.append([layerField, factorField])

    def DMFeatures(self, ListOfFeatures): # problem
        for i in ListOfFeatures:
            if not i:
                i.append(['nothing', 'none'])


    def DMFeatures_desicion(self, ListOfFeatures): # problem
        for i in ListOfFeatures:
            self.list_of_outputs.append(DM.radialStat(i))

    def DMFeatures_final(self, list_of_outputs):
        for i in list_of_outputs:
            if i == []:
                i.append(["nothing", "none",0])
