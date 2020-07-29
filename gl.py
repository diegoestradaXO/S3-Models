#Escritor de Imagenes BMP
#Author: Diego Estrada

# Errores comunes:
# "index out of range" puede suceder cuando el vertex esta fuera del viewport

import struct
from obj import Obj


def char(c):
    return struct.pack('=c', c.encode('ascii'))

def word(c):
    return struct.pack('=h', c)

def dword(c):
    return struct.pack('=l', c)

def color(r, g, b):
    return bytes([b,g,r])

class Render(object):
    def __init__(self):
        self.clear_color = color(0,0,0)
        self.draw_color = color(255,255,255)
    
    def glClear(self):
        self.framebuffer = [
            [self.clear_color for x in range(self.width)]
            for y in range(self.height)
        ]

    def glCreateWindow(self, width, height): #el width y height del window es el del Render()
        self.width = width
        self.height = height
        self.framebuffer = []
        self.glClear()
    
    def point(self, x,y):
        self.framebuffer[y][x] = self.draw_color

    def glInit(self):
        pass

    def glViewPort(self, x, y, width, height):
        self.x_VP = x
        self.y_VP = y
        self.width_VP = width
        self.height_VP = height

    def glClearColor(self, r, g, b):
        self.clear_color = color(int(round(r*255)),int(round(g*255)),int(round(b*255)))

    def glColor(self, r,g,b):
        self.draw_color = color(int(round(r*255)),int(round(g*255)),int(round(b*255)))

    def glVertex(self, x, y):
        xPixel = round((x+1)*(self.width_VP/2)+self.x_VP)
        yPixel = round((y+1)*(self.height_VP/2)+self.y_VP)
        self.point(xPixel, yPixel)
    
    def glLine(self,x1, y1, x2, y2):
        x1 = int(round((x1+1) * self.width / 2))
        y1 = int(round((y1+1) * self.height / 2))
        x2 = int(round((x2+1) * self.width / 2))
        y2 = int(round((y2+1) * self.height / 2))
        steep=abs(y2 - y1)>abs(x2 - x1)
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        if x1>x2:
            x1,x2 = x2,x1
            y1,y2 = y2,y1

        dy = abs(y2 - y1)
        dx = abs(x2 - x1)
        y = y1
        offset = 0
        threshold = dx

        for x in range(x1, x2):
            if offset>=threshold:
                y += 1 if y1 < y2 else -1
                threshold += 2*dx
            if steep:
                self.framebuffer[x][y] = self.draw_color
            else:
                self.framebuffer[y][x] = self.draw_color
            offset += 2*dy

    def load(self, filename, translate, scale):
        model = Obj(filename)
        
        for face in model.faces:
            vcount = len(face)

            for j in range(vcount):
                f1 = face[j][0]
                f2 = face[(j + 1) % vcount][0]

                v1 = model.vertices[f1 - 1]
                v2 = model.vertices[f2 - 1]
                
                x1 = round((v1[0] + translate[0]) * scale[0])
                y1 = round((v1[1] + translate[1]) * scale[1])
                x2 = round((v2[0] + translate[0]) * scale[0])
                y2 = round((v2[1] + translate[1]) * scale[1])

                x1 = ((2*x1)/self.width)-1
                y1 = ((2*y1)/self.height)-1
                x2 = ((2*x2)/self.width)-1
                y2 = ((2*y2)/self.height)-1
                self.glLine(x1, y1, x2, y2)

    def glFinish(self, filename):
        f = open(filename, 'bw')

        #file header
        f.write(char('B'))
        f.write(char('M'))
        f.write(dword(14 + 40 + self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(14 + 40))

        #image header
        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))   
        f.write(dword(0))
        f.write(dword(24))
        f.write(dword(self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0)) 
        f.write(dword(0))

        # pixel data

        for x in range(self.width):
            for y in range(self.height):
                f.write(self.framebuffer[y][x])
        
        f.close()
    
    def glFill(self, polygon):
        for y in range(self.height):
            for x in range(self.width):
                i = 0
                j = len(polygon) - 1
                inside = False
                for i in range(len(polygon)):
                    if (polygon[i][1] < y and polygon[j][1] >= y) or (polygon[j][1] < y and polygon[i][1] >= y):
                        if polygon[i][0] + (y - polygon[i][1]) / (polygon[j][1] - polygon[i][1]) * (polygon[j][0] - polygon[i][0]) < x:
                            inside = not inside
                    j = i
                if inside:
                    self.point(y,x)


r = Render()
r.glCreateWindow(800,800)
r.load('./jordan1.obj', (10, 10), (40, 40))
r.glFinish('out.bmp')