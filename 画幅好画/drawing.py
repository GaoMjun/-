
from urllib import urlopen
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import *
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.textlabels import Label

url = "http://services.swpc.noaa.gov/text/predicted-sunspot-radio-flux.txt"
comment_chars = "#:"

drawing = Drawing(400, 200)
data = []

for line in urlopen(url).readlines():
    if not line.isspace() and not line[0] in comment_chars:
        data.append([float(n) for n in line.split()])

pred = [row[2] for row in data]
hign = [row[3] for row in data]
low = [row[4] for row in data]
times = [row[0] + row[1]/12.0 for row in data]

lp = LinePlot()
lp.x = 50
lp.y = 50
lp.height = 125
lp.width = 300

lp.data = [zip(times, pred), zip(times, hign), zip(times, low)]
# lp.line[0].strokeColor = colors.blue
# lp.line[1].strokeColor = colors.red
# lp.line[2].strokeColor = colors.green

drawing.add(lp)
drawing.add(String(250, 150, 'Sunspots', fontSize = 14, fillColor = colors.red))
renderPDF.drawToFile(drawing, 'report2.pdf', 'Sunspots')
