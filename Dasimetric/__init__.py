# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Dasimetric
                                 A QGIS plugin
 The plugin calculate population using a dasimetric approach
                             -------------------
        begin                : 2018-03-07
        copyright            : (C) 2018 by Nelson Mileu/IGOT
        email                : nmileu@campus.ul.pt
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Dasimetric class from file Dasimetric.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .dasimetric import Dasimetric
    return Dasimetric(iface)
