import pygame
from math import *
def font(size, text,color=(0,0,0),font=None):
  return pygame.font.Font(font, size).render(text, True, color)
def getcolor(color):
  if color > 1530:
    color = color % 1530
  if color >= 0 and color < 255: # Red to yellow
    colorout = (255,color,0)
  if color >= 255 and color < 510: # Yellow to green
    colorout = (255-(color-255),255,0)
  if color >= 510 and color < 765: # Green to teal
    colorout = (0,255,color-510)
  if color >= 765 and color < 1020: # Teal to blue
    colorout = (0,255-(color-765),255)
  if color >= 1020 and color < 1275: # Blue to purple
    colorout = (color-1020,0,255)
  if color >= 1275 and color < 1530: # Purple to red
    colorout = (255,0,255-(color-1275))
  return colorout
class Camera:
  def __init__(self,(x,y,z),(dh,dv),(sx,sy),fov):
    """Creates a Camera"""
    self.x=x
    self.y=y
    self.z=z
    
    self.dh=dh
    self.dv=dv
    self.resolution=resolution
    self.cx = sx/2
    self.cy = sy/2
    self.screen = pygame.Surface(sx,sy)
    self.zbuffer=[[100 for a in range(sx+1)] for b in range(sy+1)]

    self.fov=fov
    self.film = tan(radians(self.fov/2))
    self.filmdivz = self.cy/self.film
    
  def clearscreen(color=(0,0,0)):
    """Clears the screen and zbuffer"""
    self.screen.fill(color)
    self.zbuffer = [[100 for a in range(sx+1)] for b in range(sy+1)]
    
  def changeres(newx,newy):
    """Changes the resolution of screen"""
    sx=newx
    sy=newy
    
    self.cx = sx/2
    self.cy = sy/2
    
    self.screen = pygame.Surface(sx,sy)
    self.zbuffer=[[100 for a in range(sx+1)] for b in range(sy+1)]
    self.filmdivz = self.cy/self.film
  def offestps(x,y,z):
    (newx, newy, newz) = x-self.x,y-self.y,z-self.z
    dish=distance(newz,newx)
    hdir = atan2(newz,newx)-self.dh
    (newx,newy)=cos(hdir)*dish,sin(hdir)*dish
    disv=distance(newz,newy)
    vdir = atan2(newz,newy)-self.dv
    (newx,newy)=cos(vdir)*disv,sin(vdir)*vish
    return (newx/abs(newy)*self.filmdivy+self.xscreen,newz/abs(newy)*self.filmdivy+self.xscreen)
  def offsetpoint(self,x,y,z):
    """Offsets the point from the camera."""
    newx = x-self.x
    newy = y-self.y
    newz = z-self.z
    
    dish = distance(newz,newx)
    hdir = atan2(newz,newx)
    hdir -= self.dh
    newx = cos(hdir) * dish
    newy = sin(hdir) * dish
    
    disv = distance(newz,newy)
    vdir = atan2(newz,newy)
    vdir -= self.dv
    newy = cos(vdir) * disv
    newz = sin(vdir) * disv
    
    return (newx,newy,newz)
  def get3dpoint(self,(x,y,z),offseted=False):
    """Finds position of point on the camera's screen."""
    if not offseted:
      (newx,newy,newz) = self.offsetpoint(x,y,z)
    else:
      (newx,newy,newz) = x,y,z
    
    if True: #a=(b/abs(c))*d+e
      xyangle = newx/abs(newy)
      zyangle = newz/abs(newy)
      
      xposition = xyangle * self.filmdivy+self.xscreen
      yposition = zyangle * self.filmdivy+self.yscreen
      
      return (int(xposition),int(yposition))
  def drawpoly(poly,colors):
    # Find size of polygon
    xl=100000
    yl=100000
    xh=0
    yh=0
    for point in pointlist:
      if point[0] < xl:
        xl = point[0]
      if point[1] < yl:
        yl = point[1]
      if point[0] > xh:
        xh = point[0]
      if point[1] > yh:
        yh = point[1]
    width=xh-xl
    height=yh-yl

    # Offset points into polygon
    points = []
    for p in range(len(pointlist)):
      points.append(list(pointlist[p]))
      points[p][0] -= xl
      points[p][1] -= yl

    # Create 2d list for polygon
    zbufferpoly=[[None for a in range(width+1)] for b in range(height+1)] # [y][x]]
    
    # Finds the distance to the origin plane by offseting the vertices from camera # try calculating offset before
    for p in range(len(vertices)):
      y=cam.offsetpoint(vertices[p][0],vertices[p][1],vertices[p][2])[1]
      zbufferpoly[points[p][1]][points[p][0]] = abs(y)

    # Draw outline of shape onto the 2d list
    for p in range(len(vertices)-1):
      drawline2dlist(points[p][0],points[p][1],
                     points[p+1][0],points[p+1][1],
                     zbufferpoly,
                     zbufferpoly[points[p][1]][points[p][0]],
                     zbufferpoly[points[p+1][1]][points[p+1][0]])
    drawline2dlist(points[len(vertices)-1][0],points[len(vertices)-1][1],points[0][0],points[0][1],zbufferpoly,zbufferpoly[points[len(vertices)-1][1]][points[len(vertices)-1][0]],zbufferpoly[points[0][1]][points[0][0]])

    # Fills in shape
    for y in range(len(zbufferpoly)):
      # Finds start and end of each line
      lookfor = 0
      startx = None
      endx = None
      if not y + yl < 0 and not y + yl > cam.yscreen:
        for x in range(len(zbufferpoly[y])):
          if lookfor == 0:
            if zbufferpoly[y][x] != None:
              lookfor = 1
              startx = x
          elif lookfor == 1:
            if zbufferpoly[y][x] == None:
              lookfor = 2
          elif lookfor == 2:
            if zbufferpoly[y][x] != None:
              endx = x
              lookfor = 3
            break
      # Makes sure it found start and end
      if lookfor == 3:
        spreadsize = endx-startx
        spreaddist = zbufferpoly[y][endx]-zbufferpoly[y][startx]
        spread = spreaddist/spreadsize
        current = zbufferpoly[y][startx]
        # fills in line
        for x in range(startx,endx+1):
          zbufferpoly[y][x] = current
          current += spread
          try:
            if x > 0 and x < cam.screenx and y > 0 and y < cam.screenx:
              if zbufferpoly[y][x] <= zbuffer[y+yl][x+xl]:
                surface.set_at((x+xl,y+yl),color)
                zbuffer[y+yl][x+xl] = zbufferpoly[y][x]
          except:
            pass

def distance(x,y):
  return sqrt(x**2+y**2)
class Obj3d:
  def __init__(self,model,(x,y,z),scale=1,typelist):
    self.model=model
    self.x=x
    self.y=y
    self.z=z
    self.scale=scale
    typelist.append(self)
  def draw(self,cam,drawtype,surface=None):
    """Draws itself on specified camera with specified drawtype. surface is the surface
to use if not using zbuffer, defaults to camera face. possible drawtypes are "wireframe","zbuffered","filled"."""
    newverts=[]
    for vertex in self.model.vertices:
      newverts.append(vertex[0]*self.scale+self.x,vertex[1]*self.scale+self.y,vertex[2]*self.scale+self.z)
    for faceindex in range(len(self.model.faces)):
      face = self.model.faces[faceindex]
      if drawtype == "zbuffered":
        cam.drawface(face,newverts)
      else:
        screenpos = []
        for vertex in newverts:
          screenpos.append(cam.get3dpoint(vertex))
        if drawtype == "wireframe":
          if surface != None:
            pygame.draw.lines(surface,self.model.colors[faceindex],True,screenpos,1)
          else:
            pygame.draw.lines(cam.screen,self.model.colors[faceindex],True,screenpos,1)
        else:
          if surface != None:
            pygame.draw.polygon(surface,self.model.colors[faceindex],screenpos,0)
          else:
            pygame.draw.polygon(cam.screen,self.model.colors[faceindex],screenpos,0)
class Model:
  def __init__(self,filename,modellist,color=None):
    alist.append(self)
    self.color=color
    x=filename.split(".")
    if x[len(x)-1] == "POL":
      f = open(filename,"r")
      contents = f.read()
      f.close()
      clear = contents.translate(None, ' ')
      lines = clear.split("\n")
      self.polygons = []
      currentpolygon = []
      for i in range(len(lines)):
        if len(lines[i]) == 0:
          self.polygons.append(currentpolygon)
          currentpolygon = []
        else:
          point = lines[i].split(",")
          currentpolygon.append([float(point[0]),float(point[2]),float(point[1])*-1])
    elif x[len(x)-1] == "obj":
      f = open(filename,"r")
      contents = f.read()
      f.close()
      lines = contents.split("\n")
      self.polygons = []
      self.v = []
      for i in range(len(lines)):
        pars = lines[i].strip(",").split(" ")
        if pars[0] == "v":
          self.v.append([float(pars[1])*size,float(pars[2])*size,float(pars[3])*-size])
        elif pars[0] == "f":
          if "/" in lines[i]:
            x=[]
            for p in range(1,len(pars)):
              x.append(pars[p].split("//")[0])
            self.polygons.append(x)
          else:
            self.polygons.append(pars[1:len(pars):1])
        elif pars[0] == "o":
          print "Object: " + pars[1]
        elif lines[i] == "":
          pass
        elif lines[i][0] == "#":
          print " ".join(pars)
        else:
          pass
      self.faces = len(self.polygons)
      self.colord = 1530.0/self.faces
          #print "Can't do: " + str(pars)
          #raise BaseException("Only Supports faces and vetices, line: "+str(i)+" has type: "+str(pars))
    else:
      raise BaseException("Not Recognized File type: "+x[len(x)-1])
def drawline2dlist(x1,y1,x2,y2,list2d,distance1,distance2,color1,color2):
  x=x1
  y=y1
  d=distance2-distance1
  cr=color2[0]-color1[0]
  cg=color2[1]-color1[1]
  cb=color2[2]-color1[2]
  w=x2-x1
  h=y2-y1
  dx1 = 0
  dy1 = 0
  dx2 = 0
  dy2 = 0
  if w < 0:
    dx1 = -1
    dx2 = -1
  elif w > 0:
    dx1 = 1
    dx2 = 1
  if h < 0:
    dy1 = -1
  elif h > 0:
    dy1 = 1
  longest = abs(w)
  shortest = abs(h)
  if not longest>shortest:
    longest = abs(h)
    shortest = abs(w)
    if h<0:
      dy2 = -1
    elif h > 0:
      dy2 = 1
    dx2 = 0
  numerator = longest >> 1
  currentpixel = distance1
  if longest > 0:
    pixels=d/longest
  else:
    pixels = 0
  for i in range(longest+1):
    list2d[y][x] = currentpixel
    numerator += shortest
    if not numerator<longest:
      numerator -= longest
      x += dx1
      y += dy1
    else:
      x += dx2
      y += dy2
    currentpixel += pixels
