import calendar
from datetime import datetime, date, timedelta
from decimal import Decimal
from PIL import Image, ImageDraw, ImageFont, ImageOps

img_width = 640
img_height = 480
ext_field = 50
int_field = 20
dash = 5

#----------------------------------
class Plot():

    def __init__(self, path, name, min_value, max_value, min_date, max_date):
        self.path = path
        self.name = name
        self.min_value = min_value
        self.max_value = max_value
        self.min_date  = min_date 
        self.max_date  = max_date 
        self.im = Image.new('RGBA', (img_width, img_height), 'white')
        d = ImageDraw.Draw(self.im)
        d.rectangle([ext_field, ext_field, img_width-ext_field, img_height-ext_field], fill = 'gray')
        d.rectangle([ext_field+1, ext_field+1, img_width-ext_field-1, img_height-ext_field-1], fill = 'white')

        if not (min_value and max_value and min_date and max_date):
            return

        # x-axis
        if ((max_date - min_date).days > 730):
            for i in range(min_date.year + 1, max_date.year + 1):
                self.draw_date(date(i, 1, 1), '%Y')
        elif ((max_date - min_date).days > 60):
            if (min_date.day == 1):
                dt = min_date
            else:
                dt = next_month(date(min_date.year, min_date.month, 1))
            while (dt <= max_date):
                self.draw_date(dt, '%m.%Y')
                dt = next_month(dt)
        else:
            dt = min_date
            delta = round((max_date - min_date).days / 10, 0)
            while (dt <= max_date):
                self.draw_date(dt, '%d.%m.%Y')
                dt = dt + timedelta(delta)

        # y-axis
        delta = (max_value - min_value) / 5
        if (delta < 1):
            rd = 1
            step = Decimal(round(delta, 1))
        else:
            rd = 0
            step = Decimal(round(delta))
        vl = round(min_value, rd)
        while (vl <= max_value):
            y = self.get_y_pos(vl)
            d.line(((ext_field-dash, y), (ext_field, y)), 'gray')
            if (rd == 1):
                 value = '{:.1f}'.format(vl)
            else:
                 value = '{:.0f}'.format(vl)
            font = ImageFont.truetype("arial.ttf", 12)
            d.text((ext_field-dash-3, y), value, fill = (0,0,0), font = font, anchor = 'rm')
            vl += step

    def draw_date(self, dt, fmt):
        x = self.get_x_pos(dt)
        
        d = ImageDraw.Draw(self.im)
        d.line(((x, img_height-ext_field), (x, img_height-ext_field+dash)), 'gray')

        w = Image.new('RGBA', (100, 100))
        d = ImageDraw.Draw(w)
        font = ImageFont.truetype("arial.ttf", 12)
        d.text((99, 50), dt.strftime(fmt), fill = (0,0,0), font = font, anchor = 'rt')
        w = w.rotate(25)
        px, py = x-90, img_height-ext_field-20
        sx, sy = w.size
        self.im.paste(w, (px, py, px + sx, py + sy), w)

    def get_x_pos(self, dt):
        if not (self.min_date and self.max_date):
            return 0

        draw_width = img_width - 2*ext_field - 2*int_field
        return int((dt - self.min_date).days / (self.max_date - self.min_date).days * draw_width + ext_field + int_field)

    def get_y_pos(self, value):
        if not (self.min_value and self.max_value):
            return 0

        draw_height = img_height - 2*ext_field - 2*int_field
        return int(draw_height - (value - self.min_value) / (self.max_value - self.min_value) * draw_height + ext_field + int_field)

    def plot(self, x, y, color, linestyle = None):
        d = ImageDraw.Draw(self.im)
        x1 = y1 = x2 = y2 = None
        for i in range(len(x)):
            if not x1:
                x1 = self.get_x_pos(x[i])
                y1 = self.get_y_pos(y[i])
            else:
                x2 = self.get_x_pos(x[i])
                y2 = self.get_y_pos(y[i])
                d.line(((x1, y1), (x2, y2)), fill = color, width = 2)
                x1 = x2
                y1 = y2

    def scatter(self, x, y, color):
        d = ImageDraw.Draw(self.im)
        for i in range(len(x)):
            x1 = self.get_x_pos(x[i])
            y1 = self.get_y_pos(y[i])
            d.ellipse(((x1-4, y1-4), (x1+4, y1+4)), fill = color)

    def save(self):
        self.im.save(self.path + self.name + '.png')


def next_month(dt):
    if (dt.month == 12):
        return date(dt.year + 1, 1, 1)
    else:
        return date(dt.year, dt.month + 1, 1)

