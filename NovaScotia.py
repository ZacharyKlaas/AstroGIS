######################################################
# AstroGIS                                           #
# A system for manipulating maps in 3 dimensions.    #
# -------------------------------------------------- #
# Original concept by Zachary Klaas                  #
# Free for open source use, so long as attribution   #
# of AstroGIS concept is identified with the author  #
######################################################

######################################################
# Code for geodetic2ecef function and the geodetic   #
# constants provided in David Parunakian's PySatel   #
# framework:  https://code.google.com/p/pysatel/     #
# source/browse/trunk/coord.py?r=22                  #
######################################################

# Imported graphical user interface elements used by the program.
import Tkinter
from Tkinter import *

# Imported geometric concepts used by the program.
from math import degrees, radians

# Imported math concepts used by the program.
from scipy import cos, sin, sqrt

# An imported library the program utilises to read lat,lon,alt entries from a
# text file in as "string literals" so Python will understand them as
# tuples and not individual variables.
import ast

# Constants defined by the World Geodetic System 1984 (WGS84).
# Can be edited to another geodetic standard if necessary.
a = 6378.137
b = 6356.7523142
esq = 6.69437999014 * 0.001
e1sq = 6.73949674228 * 0.001
f = 1 / 298.257223563

# The datafile that will be read by the program.  The file needs to have
# the following structure:
# 1: <number of geographic objects to draw (points, lines or polygons)><cr>
# 2: <number of vertices for first object><cr>
# 3: <lon,lat,alt values, separated by commas, for first vertex><cr>
# 4: <repeat 3 for each vertex>
# 5: <repeat 2 for each object>
# The "datafile" variable is set to "unitedkingdom.txt", provided with this
# program as an example dataset - however, this program can read any file 
# similarly structured, simply by changing the value to which the "datafile" 
# variable is set below.
datafile = "novascotiaridings.txt"

# Default values that can be set for each individual file or left as zero
# (for the spin and displace values) and one (for the size value).  There
# must be three values for spin, two for displace and one for size.
spin = 180,0,0
displace = 0,0
size = 1

# Normal changes in magnitude used by the program, which can be changed
# if the user wants buttons to cause program to zoom, pan or rotate by
# larger magnitudes.
zoom = 1.25
pan = 50
rotate = 20

# Function to convert from lon,lat,alt to xyz in the ECEF system.
def geodetic2ecef(lon, lat, alt):
    """Convert geodetic coordinates to ECEF."""
    lat, lon = radians(lat), radians(lon)
    xi = sqrt(1 - esq * sin(lat))
    x = ((a / xi + alt) * cos(lat) * cos(lon))
    y = ((a / xi + alt) * cos(lat) * sin(lon))
    z = ((a / xi * (1 - esq) + alt) * sin(lat))
    return x, y, z

# Function to convert from an ECEF value another ECEF value give angular
# rotation.  This function allows the roll, pitch and yaw buttons to work.
def rotatedecef(xvalue, yvalue, zvalue, phi, theta, psi, diffx, diffy,
                diffz, scale):
     """Convert ECEF transformations into rotated ECEF transformations"""
     phi, theta, psi = radians(phi), radians(theta), radians(psi)
     term1 = cos(theta)*cos(psi)
     term2 = cos(phi)*sin(psi)
     term3 = sin(phi)*sin(theta)*cos(psi)
     term4 = sin(phi)*sin(psi)
     term5 = cos(phi)*sin(theta)*cos(psi)
     sum1 = xvalue*term1
     sum2 = (yvalue*term2)+term3
     sum3 = (zvalue*term4)-term5
     rotatedx = ((sum1+sum2+sum3) * scale) - diffx
     term6 = -cos(theta)*sin(psi)
     term7 = cos(phi)*cos(psi)
     term8 = sin(phi)*sin(theta)*sin(psi)
     term9 = sin(phi)*cos(psi)
     term10 = cos(phi)*sin(theta)*sin(psi)
     sum4 = xvalue*term6
     sum5 = (yvalue*term7)-term8
     sum6 = (zvalue*term9)+term10
     rotatedy = ((sum4+sum5+sum6) * scale) - diffy
     term11 = sin(theta)
     term12 = -sin(phi)*cos(theta)
     term13 = cos(phi)*cos(theta)
     sum7 = xvalue*term11
     sum8 = yvalue*term12
     sum9 = zvalue*term13
     rotatedz = ((sum7+sum8+sum9) * scale) - diffz
     return rotatedx, rotatedy, rotatedz

# Sets initial values for the GUI window and map drawing canvas.
xcoords = []
ycoords = []
allcoords = []

canvas_width = 800
canvas_height = 600

master = Tkinter.Tk()
master.title("AstroGIS")

# This sets the window canvas so it is prepared to draw the map data.
w = Tkinter.Canvas(master, width=canvas_width, height=canvas_height,
                   background="black")

# This function draws the geographic objects identified in the "datafile".
def drawit():
    global xcoords, ycoords, allcoords, move, spin, extentroid, displace
    
    move = 0,0,0

    infile = open(datafile,"r")
    objnumber = int(infile.readline())
    for objcount in range(objnumber):
        vertnumber = int(infile.readline())
        for vertcount in range(vertnumber):
            vertex = ast.literal_eval(infile.readline())
            xlocation = vertex[0]
            ylocation = vertex[1]
            ecefvertex = geodetic2ecef(vertex[0],vertex[1],vertex[2])
            rotatedvertex = rotatedecef(ecefvertex[0],ecefvertex[1],ecefvertex[2],
                               spin[0],spin[1],spin[2],move[0],move[1],
                               move[2],size)
            xcoords.append(rotatedvertex[0])
            ycoords.append(rotatedvertex[1])
            allcoords.append(rotatedvertex[0])
            allcoords.append(rotatedvertex[1])
        allcoords = []
    
        minx = min(xcoords)
        miny = min(ycoords)
        maxx = max(xcoords)
        maxy = max(ycoords)

    xcoords = []
    ycoords = []

    extentroid = [(minx+maxx)/2,(miny+maxy)/2]

    move = [-(400 - extentroid[0]),-(300 - extentroid[1]),0]
    
    infile = open(datafile,"r")
    objnumber = int(infile.readline())
    for objcount in range(objnumber):
        vertnumber = int(infile.readline())
        for vertcount in range(vertnumber):
            vertex = ast.literal_eval(infile.readline())
            xlocation = vertex[0]
            ylocation = vertex[1]
            ecefvertex = geodetic2ecef(vertex[0],vertex[1],vertex[2])
            rotatedvertex = rotatedecef(ecefvertex[0],ecefvertex[1],ecefvertex[2],
                               spin[0],spin[1],spin[2],move[0]+displace[0],
                                move[1]+displace[1],move[2],size)
            xcoords.append(rotatedvertex[0])
            ycoords.append(rotatedvertex[1])
            allcoords.append(rotatedvertex[0])
            allcoords.append(rotatedvertex[1])
        w.create_polygon(allcoords, outline="blue", fill='yellow', width=3)
        allcoords = []

    xcoords = []
    ycoords = []

    w.create_rectangle(extentroid[0]-move[0]-5,extentroid[1]-move[1]-5,
                       extentroid[0]-move[0]+5,extentroid[1]-move[1]+5,
                       fill="red")

# These functions allow the two-dimensional "zoom and pan" functions permitted
# by most GIS systems to manipulate the geographic objects.
def callback():
    global spin
    global displace
    global size
    spin = [float(e11.get()),float(e12.get()),float(e13.get())]
    displace = [float(e21.get()),float(e22.get())]
    size = float(e3.get())
    w.delete(ALL)
    drawit()

def zoomin():
    global size
    global zoom
    global w
    size = size * zoom
    w.delete(ALL)
    drawit()

def zoomout():
    global size
    global zoom
    global w
    size = size / zoom
    w.delete(ALL)
    drawit()

def panleft():
    global displace
    global pan
    global w
    displace = [(displace[0]-pan), displace[1]]
    w. delete(ALL)
    drawit()

def panright():
    global displace
    global pan
    global w
    displace = [(displace[0]+pan), displace[1]]
    w. delete(ALL)
    drawit()

def panup():
    global displace
    global pan
    global w
    displace = [displace[0], (displace[1]-pan)]
    w. delete(ALL)
    drawit()

def pandown():
    global displace
    global pan
    global w
    displace = [displace[0], (displace[1]+pan)]
    w. delete(ALL)
    drawit()

# These functions permit the geographic objects to be manipulated in three
# dimensions, spinning the image in the x, y and z directions relative to
# the ECEF coordinates.
def rollforward():
    global spin
    global rotate
    global w
    spin = spin[0] + rotate, spin[1], spin[2]
    w.delete(ALL)
    drawit()

def rollback():
    global spin
    global rotate
    global w
    spin = spin[0] - rotate, spin[1], spin[2]
    w.delete(ALL)
    drawit()

def pitchforward():
    global spin
    global rotate
    global w
    spin = spin[0], spin[1] + rotate, spin[2]
    w.delete(ALL)
    drawit()

def pitchback():
    global spin
    global rotate
    global w
    spin = spin[0], spin[1] - rotate, spin[2]
    w.delete(ALL)
    drawit()

def yawforward():
    global spin
    global rotate
    global w
    spin = spin[0], spin[1], spin[2] + rotate
    w.delete(ALL)
    drawit()

def yawback():
    global spin
    global rotate
    global w
    spin = spin[0], spin[1], spin[2] - rotate
    w.delete(ALL)
    drawit()

# These button controls access the above functions for manipulating the
# geographic objects in both the conventional 2D sense and the relative to
# the ECEF coordinates in 3D.
w.pack(side=TOP)
b1 = Button(master, text ="Zoom In", command = zoomin).pack(side=LEFT)
b2 = Button(master, text ="Zoom Out", command = zoomout).pack(side=LEFT)
b3 = Button(master, text ="Pan Left", command = panleft).pack(side=LEFT)
b4 = Button(master, text ="Pan Right", command = panright).pack(side=LEFT)
b5 = Button(master, text ="Pan Up", command = panup).pack(side=LEFT)
b6 = Button(master, text ="Pan Down", command = pandown).pack(side=LEFT)
b7 = Button(master, text ="Roll Forward", command = rollforward).pack(side=LEFT)
b8 = Button(master, text ="Roll Back", command = rollback).pack(side=LEFT)
b9 = Button(master, text ="Pitch Forward", command = pitchforward).pack(side=LEFT)
b10 = Button(master, text ="Pitch Back", command = pitchback).pack(side=LEFT)
b11 = Button(master, text ="Yaw Forward", command = yawforward).pack(side=LEFT)
b12 = Button(master, text ="Yaw Back", command = yawback).pack(side=LEFT)

l11 = Label(master,text="Spin-X")
e11 = Entry(master)
e11.insert(0,spin[0])
l12 = Label(master,text="Spin-Y")
e12 = Entry(master)
e12.insert(0,spin[1])
l13 = Label(master,text="Spin-Z")
e13 = Entry(master)
e13.insert(0,spin[2])
l11.pack()
e11.pack()
l12.pack()
e12.pack()
l13.pack()
e13.pack()
l21 = Label(master,text="Displace-X")
e21 = Entry(master)
e21.insert(0,displace[0])
l22 = Label(master,text="Displace-Y")
e22 = Entry(master)
e22.insert(0,displace[1])
l21.pack()
e21.pack()
l22.pack()
e22.pack()
l3 = Label(master,text="Size")
e3 = Entry(master)
e3.insert(0,size)
l3.pack()
e3.pack()

e11.focus_set()
e12.focus_set()
e13.focus_set()
e21.focus_set()
e22.focus_set()
e3.focus_set()

b = Button(master, text="New Defaults", width=10, command=callback)
b.pack()

# This accesses the drawing function at the time of the program's initial
# activation.
drawit()

# This activates the program.
master.mainloop()
