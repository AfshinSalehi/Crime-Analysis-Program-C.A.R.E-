import socket
import time

import care_main
from reportlab.graphics import charts
from reportlab.graphics.charts import piecharts
from reportlab.graphics.shapes import *
# for importing new fonts
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

pdfmetrics.registerFont(TTFont('Symbol', 'Symbol.ttf'))  # adds up new font
pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
PLUGIN_PATH = os.path.expanduser('~/.qgis2/python/plugins/Care/')

def print_pdf(c, Inputs, Outputs):
    # FIRST PAGE
    # set font and get page number
    output1 = care_main.output
    c.setFont("Times-Italic", 6, leading=5)
    pn = c.getPageNumber()

    # print page number and page top icon
    c.drawString(55, 25, "Page %s" % (pn))
    c.drawImage(PLUGIN_PATH+'CARE_LOGO.png', 300, 750, 239,
                60, mask='auto')

    # for extra decoration of the PDF,
    c.setFillColor(colors.gray)  # import lib => colors
    c.rect(0, 0, 50, 850, stroke=0, fill=1)
    c.rect(550, 0, 50, 850, stroke=0, fill=1)
    c.line(50, 50, 550, 50)

    # set font again
    c.setFont("Times-Italic", 8, leading=5)

    # sot color by color module and the color name
    c.setFillColor(colors._PCMYK_black)

    # draw the top information string
    c.drawString(55, 790, "This is a generated report using { %s } machine." % (
        socket.gethostname()))  # needs import socket to print machine name
    c.drawString(55, 770, "generated report number: %s" % ('no. %s' % (time.time())))
    c.drawString(55, 760, "generated report name: %s" % (output1))
    c.drawString(55, 750, "generation date: %s" % (time.asctime()))
    # set the line style dashed - so it must change next time...
    c.setDash(array=[5, 0.8], phase=9)
    c.line(550, 735, 200, 735)
    c.line(550, 732, 200, 732)

    # additional information of lower page
    print c.getAvailableFonts()
    c.setFont("Times-Roman", 7, leading=5)
    c.drawRightString(545, 40,
                      'Crime analysis software made by A.Salehi under the scientific abbreviated name of  C.A.R.E  \xc2\xa9')
    c.drawImage(PLUGIN_PATH+'email.png', 465, 27.2, 10, 10, mask='auto')
    c.drawRightString(545, 30, '  Salehi@consultant.com')

    # some main parts no. 0 ( first ring cumulative layers)
    # report of first loop
    c.setDash(array=[1, 0], phase=1)
    c.setLineWidth(0.1)
    c.setFont('Times-Bold', 8)
    c.drawString(55, 710, '+ This page is dedicated to crime analysis using *actual intervention:')
    c.setFont('Times-Roman', 8)
    c.line(55, 700, 155, 700)
    c.drawString(55, 680,
                 '\xe2\x91\xa0 - The following results are due to analysing the *main sphere of influence and using below layers and details as main factor :', c.setFont('Times-Bold', 7))
    c.drawString(65, 670, ' \xe2\x86\x92 - Using "%s" as the polygon layer, "%s" as the name field and "%s" as Q-factor.' % (str(Inputs[0]),str(Inputs[1]),str(Inputs[2])), c.setFont('Times-Roman', 8))
    c.drawString(65, 660, ' \xe2\x86\x92 - Using "%s" as the polyline layer, "%s" as the name field and "%s" as Q-factor.' % (str(Inputs[3]),str(Inputs[4]),str(Inputs[5])))
    c.drawString(65, 650, ' \xe2\x86\x92 - Using "%s" as the point layer, "%s" as the name field and "%s" as Q-factor.' % (str(Inputs[6]),str(Inputs[7]),str(Inputs[8 ])))

    c.drawString(60 ,635 , " \xe2\x96\xba NOTE: Using at least three layers is a must in this version of the program.")

    # region USING SOME OF REPORT GENERATION CODES HERE
    ycoord = 620
    veryOutIdx = 0
    outIdx = 0
    inIdx = 0
    list_of_featType = ['polygonal', 'linear', 'pointwise','polygonal', 'linear', 'pointwise','polygonal', 'linear', 'pointwise','polygonal', 'linear', 'pointwise']
    list_of_featTypeIdx = 0

    for ind, list in enumerate(Outputs[:9]):

        for lol in list :

            c.drawString(70, ycoord, ' \xe2\x86\x92 - the impact of %s elements is "%s" with the Q-factor of "%s".' % ( list_of_featType[list_of_featTypeIdx], lol[0], lol[1]), c.setFont('Times-Bold', 5.5))
            ycoord = ycoord - 10
        list_of_featTypeIdx+=1

        # if ind ==2 or ind ==5 or ind ==8:
        #     ycoord = ycoord - 140
        if ind == 2 :
            ycoord = 438
        if ind == 5 :
            ycoord = 235


    # # the sphere changer
    # for bigLoop in range(3):
    #     # the layer changer
    #     for smallLoop in range(3):
    #         # the feature changer
    #         for verysmaloop in range(3):
    #             try:
    #                 for super in Outputs[veryOutIdx]:
    #                     c.drawString(65, ycoord,
    #                                  ' \xe2\x86\x92 - the first impact of %s elements is "%s" with the Q-factor of "%s".' % (
    #                                  list_of_featType[list_of_featTypeIdx], Outputs[veryOutIdx][outIdx][0],
    #                                  Outputs[veryOutIdx][outIdx][1]), c.setFont('Times-Roman', 8))
    #                     # outIdx = outIdx+1
    #                 list_of_featTypeIdx = list_of_featTypeIdx + 1
    #                 veryOutIdx = veryOutIdx + 1
    #                 ycoord = ycoord - 20
    #             except IndexError:
    #                 pass
    #
    #         list_of_featTypeIdx = 0
    #         ycoord = ycoord - 150
    # y[0:3]

    def charter(OutputList, data, label):
        for i in OutputList:
            for p in i:
                data.append(p[2])
                x = '%s, %s' % (str(p[0]), str(p[1]))
                label.append(x)

    # endregion

    # region chart of first loop
    d = Drawing(400, 200)
    pc = charts.piecharts.Pie()
    pc.x = 150
    pc.y = 50
    pc.width = 50
    pc.height = 50
    pc.data = []
    pc.labels = []
    pc.sideLabels = 1
    charter(Outputs[0:3], pc.data, pc.labels) # chart drawer
    pc.slices.strokeWidth = 0.5
    pc.slices.fontSize = 5
    pc.slices[(pc.data).index(max(pc.data))].popout = 5
    pc.slices[(pc.data).index(max(pc.data))].strokeWidth = 2
    # pc.slices[3].strokeDashArray = [2, 2]  # this code will make popup part's store hashed...( - - - - )like this
    pc.slices[(pc.data).index(max(pc.data))].labelRadius = 1.5
    pc.slices[(pc.data).index(max(pc.data))].fontColor = colors.blue
    d.add(pc, '')  # adds chart to drawing

    d.drawOn(c, 280, 500)  # adds up the drawing to cnavas
    # endregion


    # region again for another chart and drawing no 1 ( second ring cumulative layers)
    c.drawString(55, 450,
                 '\xe2\x91\xa1 - The following results are due to analysing the *intermediate sphere of influence and using same layers and Quality (Q) factors:')
    d_1 = Drawing(400, 200)
    pc_1 = charts.piecharts.Pie()
    pc_1.x = 150
    pc_1.y = 50
    pc_1.width = 50
    pc_1.height = 50
    pc_1.data = []
    pc_1.labels = []
    pc_1.sideLabels = 1
    charter(Outputs[3:6], pc_1.data, pc_1.labels)  # chart drawer
    pc_1.slices.strokeWidth = 0.5
    pc_1.slices.fontSize = 5
    pc_1.checkLabelOverlap = 1
    pc_1.slices[(pc_1.data).index(max(pc_1.data))].popout = 5
    pc_1.slices[(pc_1.data).index(max(pc_1.data))].strokeWidth = 1
    pc_1.slices[(pc_1.data).index(max(pc_1.data))].labelRadius = 1.5
    pc_1.slices[(pc_1.data).index(max(pc_1.data))].fontColor = colors.red
    d_1.add(pc_1, '')  # adds chart to drawing

    d_1.drawOn(c, 280, 300)  # adds up the drawing to cnavas
    # endregion


    # again for another chart and drawing no 2 ( third ring cumulative layers)
    c.drawString(55, 250,
                 '\xe2\x91\xa2 - The following results are due to analysing the *pervasive sphere of influence and using same layers and Quality (Q) factors:')
    d_2 = Drawing(400, 200)
    pc_2 = charts.piecharts.Pie()
    pc_2.x = 150
    pc_2.y = 50
    pc_2.width = 50
    pc_2.height = 50
    pc_2.data = []
    pc_2.labels = []
    pc_2.sideLabels = 1
    charter(Outputs[6:9], pc_2.data, pc_2.labels)  # chart drawer
    pc_2.slices.strokeWidth = 0.5
    pc_2.slices.fontSize  = 5
    pc_2.checkLabelOverlap = 1
    pc_2.slices[(pc_2.data).index(max(pc_2.data))].popout = 5
    pc_2.slices[(pc_2.data).index(max(pc_2.data))].strokeWidth = 1
    pc_2.slices[(pc_2.data).index(max(pc_2.data))].labelRadius = 1.75
    pc_2.slices[(pc_2.data).index(max(pc_2.data))].fontColor = colors.orange


    d_2.add(pc_2, '')  # adds chart to drawing

    d_2.drawOn(c, 261, 105)  # adds up the drawing to canvas

    # NEXT PAGE
    c.showPage()
    c.drawString(100, 100, "End")

    # AGAIN AS FIRST PAGE ...
    # set font and get page number
    c.setFont("Times-Italic", 6, leading=5)
    pn = c.getPageNumber()

    # print page number and page top icon
    c.drawString(55, 25, "Page %s" % (pn))
    c.drawImage(PLUGIN_PATH+'CARE_LOGO.png', 300, 750, 239,
                60, mask='auto')

    # for extra decoration of the PDF,
    c.setFillColor(colors.gray)  # import lib => colors
    c.rect(0, 0, 50, 850, stroke=0, fill=1)
    c.rect(550, 0, 50, 850, stroke=0, fill=1)
    c.line(50, 50, 550, 50)

    # set font again
    c.setFont("Times-Italic", 8, leading=5)

    # sot color by color module and the color name
    c.setFillColor(colors._PCMYK_black)

    # draw the top information string
    c.drawString(55, 790, "This is a generated report using { %s } machine." % (
        socket.gethostname()))  # needs import socket to print machine name
    c.drawString(55, 770, "generated report number: %s" % ('no. %s' % (time.time())))
    c.drawString(55, 760, "generated report name: %s" % (output1))
    c.drawString(55, 750, "generation date: %s" % (time.asctime()))
    # set the line style dashed - so it must change next time...
    c.setDash(array=[5, 0.8], phase=9)
    c.line(550, 735, 200, 735)
    c.line(550, 732, 200, 732)

    # additional information of lower page

    c.setFont("Times-Roman", 7, leading=5)
    c.drawRightString(545, 40,
                      'Crime analysis software made by A.Salehi under the scientific abbreviated name of  C.A.R.E  \xc2\xa9')

    c.drawRightString(545, 30, '  Salehi@consultant.com')

    # Charts will be

    # region second page generative logic
    ycoord = 660
    for ind, list in enumerate(Outputs[9:12]):

        for lol in list :

            c.drawString(65, ycoord, ' \xe2\x86\x92 - the impact of %s elements is "%s" with the Q-factor of "%s".' % ( list_of_featType[list_of_featTypeIdx], lol[0], lol[1]), c.setFont('Times-Roman', 5.5))
            ycoord = ycoord - 11
        list_of_featTypeIdx+=1
    # endregion
    # again for another chart and drawing: OVERALL ( Overall, cumulative layers)
    c.setDash(array=[1, 0], phase=1)
    c.setLineWidth(0.1)
    c.setFont('Times-Bold', 8)
    c.drawString(55, 710, '+ This page is dedicated to crime analysis using **overall intervention:')
    c.setFont('Times-Roman', 8)
    c.line(55, 700, 155, 700)
    c.drawString(55, 680,
                 '\xe2\x91\xa0 - The following results are due to analysing the *overall sphere of influence and using below layers and details as main factor :',
                 c.setFont('Times-Bold', 7))
    # chart =>
    d_ov = Drawing(400, 200)
    pc_ov = charts.piecharts.Pie()
    pc_ov.x = 150
    pc_ov.y = 50
    pc_ov.width = 50
    pc_ov.height = 50
    pc_ov.data = []
    pc_ov.labels = []
    charter(Outputs[9:], pc_ov.data, pc_ov.labels)  # chart drawer
    pc_ov.slices.strokeWidth = 0.8
    pc_ov.sideLabels = 1
    pc_ov.checkLabelOverlap = 1
    pc_ov.slices.fontSize = 5
    pc_ov.slices[(pc_ov.data).index(max(pc_ov.data))].popout = 5
    pc_ov.slices[(pc_ov.data).index(max(pc_ov.data))].strokeWidth = 2
    pc_ov.slices[(pc_ov.data).index(max(pc_ov.data))].labelRadius = 1.5
    pc_ov.slices[(pc_ov.data).index(max(pc_ov.data))].fontColor = colors.red
    d_ov.add(pc_ov, '')  # adds chart to drawing

    d_ov.drawOn(c, 270, 500)  # adds up the drawing to cnavas




print ('\xc9\x90')