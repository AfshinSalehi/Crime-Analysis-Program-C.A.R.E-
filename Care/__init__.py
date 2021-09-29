# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Care
                                 A QGIS plugin
 Crime analysis using radial effectiveness

        copyright            : (C) 2017 by Afshin Salehi
        email                : Salehi@consultant.com

 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Care class from file Care.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .care_main import Care
    return Care(iface)
