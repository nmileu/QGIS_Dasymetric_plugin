from qgis.core import *
from qgis.core import QgsRasterLayer
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
from PyQt4.QtCore import QFileInfo, QVariant
import sys
import math
import csv
import processing
import os, gdal

def grassExtent(vector1):
	#Set GRASS extent
	fileInfo0 = QFileInfo(vector1)
	path0 = fileInfo0.filePath()
	baseName0 = fileInfo0.baseName()
	layer0 = QgsVectorLayer("%s" % (vector1),"vector1","ogr")
	ext = layer0.extent()
	(xmin, xmax, ymin, ymax) = (ext.xMinimum(), ext.xMaximum(), ext.yMinimum(), ext.yMaximum())
	grassExtent = str(xmin) + "," + str(xmax) + "," + str(ymin) + "," + str(ymax)
	return grassExtent

def Convert2rasterInputs(vector1,vector2,extent,resolucao,diretorioOut,plugin_dir,campoID,campoPOP,campoUSOSOLO):
	try:
		#Convert 2 raster statistical blocks using @ROWNUMBER as value
		resultado1 = diretorioOut + r"\input1.asc"
		processing.runalg("grass7:v.to.rast.attribute",vector1,0,campoID,extent,resolucao,-1,0.0001,resultado1)
		#Convert 2 raster statistical blocks using POPULATION as value
		resultado2 = diretorioOut + r"\pop.asc"
		processing.runalg("grass7:v.to.rast.attribute",vector1,0,campoPOP,extent,resolucao,-1,0.0001,resultado2)
		#Convert 2 raster land use using CLC as value
		resultado3 = diretorioOut + r"\inputCLC.asc"
		processing.runalg("grass7:v.to.rast.attribute",vector2,0,campoUSOSOLO,extent,resolucao,-1,0.0001,resultado3)
		#Reclass land use raster using dasimetric land use model: 6 classes
		reclass1 = plugin_dir + r"/rulesCLC2CLCreclass.txt"
		resultado4 = diretorioOut + r"\input2.asc"
		#processing.runalg("grass7:r.reclass",resultado3,reclass1,"",extent,0,resultado4)
		processing.runalg("grass7:r.reclass",resultado3,reclass1,"",extent,0,resultado4)
		#Reclass land use dasimetric model raster 2 rdensity
		reclass2 = plugin_dir + r"/rulesCLCreclass2Density.txt"
		#resultado5 = diretorioOut +'\\' + "rdensity.asc"
		resultado5 = diretorioOut + r"\rdensity.asc"
		print resultado4, reclass2, extent, resultado5
		processing.runalg("grass7:r.reclass",resultado4,reclass2,"",extent,0,resultado5)
	except ConversionError:
		print "Error converting to raster!"
	finally:
		print 'Vector2Raster conversion was successfully!'
	
def Convert2rasterTOTALE(vector1,extent,resolucao,diretorioOut):
	try:
		#Convert 2 raster statistical blocks using TOTAL as value
		resultado6 = diretorioOut + r"\outputT.asc"
		processing.runalg("grass7:v.to.rast.attribute",vector1,0,"TOTAL",extent,resolucao,-1,0.0001,resultado6)
		#Convert 2 raster statistical blocks using E as value
		resultado7 = diretorioOut + r"\outputE.asc"
		processing.runalg("grass7:v.to.rast.attribute",vector1,0,"E",extent,resolucao,-1,0.0001,resultado7)
	except ConversionError:
		print "Error converting to raster!"
	finally:
		print "Convert2rasterTOTALE was successfully!"
	
def DasimetricCalculator(diretorioOut,resolucao):
	try:
		raster1 = diretorioOut + r"\pop.asc"
		popLayer = QgsRasterLayer(raster1, "pop")
		raster2 = diretorioOut + r"\rdensity.asc"
		rdensityLayer = QgsRasterLayer(raster2, "rdensity")
		raster3 = diretorioOut + r"\outputE.asc"
		eLayer = QgsRasterLayer(raster3, "e")
		raster4 = diretorioOut + r"\outputT.asc"
		tLayer = QgsRasterLayer(raster4, "t")

		entries = []
		pop = QgsRasterCalculatorEntry()
		pop.ref = 'pop@1'
		pop.raster = popLayer
		pop.bandNumber = 1
		entries.append( pop )

		rdensity = QgsRasterCalculatorEntry()
		rdensity.ref = 'rdensity@1'
		rdensity.raster = rdensityLayer
		rdensity.bandNumber = 1
		entries.append( rdensity )

		e = QgsRasterCalculatorEntry()
		e.ref = 'e@1'
		e.raster = eLayer
		e.bandNumber = 1
		entries.append( e )

		t = QgsRasterCalculatorEntry()
		t.ref = 't@1'
		t.raster = tLayer
		t.bandNumber = 1
		entries.append( t )

		resultado = diretorioOut + r"\dasimetric.tif"
		resolucao2 = int(resolucao) * int(resolucao)
		expression = '(pop@1 * rdensity@1 *{})/(e@1 * t@1)'.format(resolucao2)
		print expression

		calc = QgsRasterCalculator(expression, 
								   resultado, 
								   'GTiff', 
								   popLayer.extent(), 
								   popLayer.width(), 
								   popLayer.height(), 
								   entries )

		calc.processCalculation()

		fileInfo5 = QFileInfo(resultado)
		path5 = fileInfo5.filePath()
		baseName5 = fileInfo5.baseName()
		layer5 = QgsRasterLayer(path5, baseName5)
		QgsMapLayerRegistry.instance().addMapLayer(layer5)
		if layer5.isValid() is True:
			print "Dasimetric result was loaded successfully!"
		else:
			print "Unable to read basename and file path - Your string is probably invalid"

	except CalculationError:
		print "Dasimetric calculation error!"
	finally:
		print "Dasimetric calculation was successfully!"
	
def CrossTab(raster1, raster2, vector1, diretorioOut,resolucao,campoID,weight111,weight112,weight121,weight122,weight199,weight299,weight399,weight499599):
	fileInfo1 = QFileInfo(raster1)
	path1 = fileInfo1.filePath()
	baseName1 = fileInfo1.baseName()
	layer1 = QgsRasterLayer(path1, baseName1)
	QgsMapLayerRegistry.instance().addMapLayer(layer1)
	if layer1.isValid() is True:
		print "Layer1 was loaded successfully!"
	else:
		print "Unable to read basename and file path - Your string is probably invalid"
	provider1 = layer1.dataProvider()
	extent1 = provider1.extent()
	rows1 = layer1.height()
	cols1 = layer1.width()
	block1 = provider1.block(1, extent1, cols1, rows1)
	
	fileInfo2 = QFileInfo(raster2)
	path2 = fileInfo2.filePath()
	baseName2 = fileInfo2.baseName()
	layer2 = QgsRasterLayer(path2, baseName2)
	QgsMapLayerRegistry.instance().addMapLayer(layer2)
	if layer2.isValid() is True:
		print "Layer2 was loaded successfully!"
	else:
		print "Unable to read basename and file path - Your string is probably invalid"
	provider2 = layer2.dataProvider()
	extent2 = provider2.extent()
	rows2 = layer2.height()
	cols2 = layer2.width()
	block2 = provider2.block(1, extent2, cols2, rows2)
	
	fileInfo3 = QFileInfo(vector1)
	path3 = fileInfo3.filePath()
	baseName3 = fileInfo3.baseName()
	layer3 = QgsVectorLayer("%s" % (vector1),"vector1","ogr")
	QgsMapLayerRegistry.instance().addMapLayer(layer3)
	feats_count = layer3.featureCount()
	if layer3.isValid() is True:
		print "Layer3 was loaded successfully!"
	else:
		print "Unable to read basename and file path - Your string is probably invalid"
		
	valoresBGRI = []
	valoresBGRIunicos = []
	# lista de valores BGRI unicos
	for feature in layer3.getFeatures():
		objectid = feature.attributes()[layer3.fieldNameIndex(campoID)]
		valoresBGRI.append(objectid)
		for v in valoresBGRI:
			if v not in valoresBGRIunicos:
				valoresBGRIunicos.append(v)
	a = len(valoresBGRIunicos)
	print a
	feats_count = layer3.featureCount()
	print feats_count
	
	valoresCLCunicos = [111, 112, 121, 122, 199, 299, 399, 499, 599]
	b = len(valoresCLCunicos)
	print b
	
	crossTabMatrix = [[0 for y in range(b+1)] for x in range(a+1)]
	for y in range(b):
		crossTabMatrix[0][y+1] = valoresCLCunicos[y]
	for x in range(a):
		crossTabMatrix[x+1][0] = valoresBGRIunicos[x]
	#print crossTabMatrix
	
	#crosstab
	for i in range( rows1 ):
		for j in range( cols1 ):
			cell_value1 = int(block1.value(i,j))
			cell_value2 = int(block2.value(i,j))
			for y in range(b):
				for x in range(a):
					if cell_value1 == crossTabMatrix[x+1][0] and cell_value2 == crossTabMatrix[0][y+1]:
						crossTabMatrix[x+1][y+1] += 1
						
	#print crossTabMatrix
	#exportar a tabulacao para csv
	csvfile = diretorioOut + r"\crosstab.csv"
	print csvfile
	with open(csvfile, "w") as output:
		writer = csv.writer(output, lineterminator='\n')
		writer.writerows(crossTabMatrix)
		
	# Adicionar campos para calculo (Campo1, Campo 2)
	shp_uri = vector1
	shp =  QgsVectorLayer(shp_uri, 'bgri', 'ogr')
	caps = shp.dataProvider().capabilities()
	if caps & QgsVectorDataProvider.AddAttributes:
		res = shp.dataProvider().addAttributes([QgsField("E", QVariant.Double), QgsField("TOTAL", QVariant.Double)])
	#if caps & QgsVectorDataProvider.DeleteAttributes:
	#	res = shp.dataProvider().deleteAttributes([0])
	shp.updateFields()
	
	QgsMapLayerRegistry.instance().addMapLayer(shp)
	# Get input (csv) and target (Shapefile) layers
	csv_uri = 'file:///' + diretorioOut + r'/crosstab.csv?delimiter=,'
	print csv_uri
	csvlayer = QgsVectorLayer(csv_uri, "crosstab", "delimitedtext")
	QgsMapLayerRegistry.instance().addMapLayer(csvlayer)
		
	# Set properties for the join
	shpField = campoID
	csvField = '0_1'
	joinObject = QgsVectorJoinInfo()
	joinObject.joinLayerId = csvlayer.id()
	joinObject.joinFieldName = csvField
	joinObject.targetFieldName = shpField
	joinObject.memoryCache = True
	shp.addJoin(joinObject)
	
	# Calcular pesos, TOTAL e E
	# Update do campo TOTAL no shapefile
	resolucao2 = int(resolucao) * int(resolucao)
	expressionT = QgsExpression("(crosstab_111_1+crosstab_112_1+crosstab_121_1+crosstab_122_1+crosstab_199_1+crosstab_299_1+crosstab_399_1+crosstab_499_1+crosstab_599_1)*{}".format(resolucao2))
	indexT = shp.fieldNameIndex("TOTAL")	
	expressionT.prepare(shp.pendingFields())
	shp.startEditing()
	for feature in shp.getFeatures():
		valueT = expressionT.evaluate(feature)
		shp.changeAttributeValue(feature.id(), indexT, valueT)
	shp.commitChanges()
	# Update do campo E no shapefile
	expressionE = QgsExpression("((crosstab_111_1*{})/TOTAL)*{}+((crosstab_112_1*{})/TOTAL)*{}+((crosstab_121_1*{})/TOTAL)*{}+((crosstab_122_1*{})/TOTAL)*{}+((crosstab_199_1*{})/TOTAL)*{}+((crosstab_299_1*{})/TOTAL)*{}+((crosstab_399_1*{})/TOTAL)*{}".format(resolucao2,weight111,resolucao2,weight112,resolucao2,weight121,resolucao2,weight122,resolucao2,weight199,resolucao2,weight299,resolucao2,weight399))
	indexE = shp.fieldNameIndex("E")
	expressionE.prepare(shp.pendingFields())
	shp.startEditing()
	for feature in shp.getFeatures():
		valueE = expressionE.evaluate(feature)
		shp.changeAttributeValue(feature.id(), indexE, valueE)
	shp.commitChanges()
	
