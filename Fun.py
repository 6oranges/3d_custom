import pygame
from math import *
import random
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
class camera: # Creates a camera with a position direction and FOV
  def __init__(self,x,y,z,direction,angle,resolution): # angle is FOV
    self.x=x
    self.y=y
    self.z=z
    self.direction=list(direction)
    self.direction[0] = radians(self.direction[0])
    self.direction[1] = radians(self.direction[1])
    self.angle=angle
    self.resolution=resolution
    self.xscreen = resolution[0]/2
    self.yscreen = resolution[1]/2
    self.film = tan(radians(self.angle/2))
    self.filmdivy = self.yscreen/self.film
  def offsetpoint(self,x,y,z):
    # Offsets the point from the camera
    newx = x-self.x
    newy = y-self.y
    newz = z-self.z
    
    # Calculates distance between point and camera on xy plane
    distancexy = distance2(newx,newy)
    
    # Calculates angle from the camera's xy position to the point's xy position
    xydir = atan2(newy,newx)
    
    # Finds offset angle from camera to point
    xydir -= self.direction[0]

    # Recalculates position of xy from offset
    newx = cos(xydir) * distancexy
    newy = sin(xydir) * distancexy
    
    # Calculates distance between point and camera on yz plane
    distancezy = distance2(newy,newz)

    # Calculates angle from the camera's yz position to the point's xy position
    yzdir = atan2(newz,newy)

    # Finds offset angle from camera to point
    yzdir -= self.direction[1]
    
    # Recalculates position of zy from offset
    newy = cos(yzdir) * distancezy
    newz = sin(yzdir) * distancezy
    return (newx,newy,newz)
  def get3dpoint(self,x,y,z):
    (newx,newy,newz) = self.offsetpoint(x,y,z)
    # makes sure position is in front of camera before returning
    if newy < 0:
      # finds the xy position on film
      xyangle = newx/abs(newy)
      zyangle = newz/abs(newy)
      
      # Finds positions on screen
      xposition = xyangle * self.filmdivy+self.xscreen
      yposition = zyangle * self.filmdivy+self.yscreen
      return (int(xposition),int(yposition))
def drawfacenp(surface,cam,zbuffer,vertices,color=(100,100,100)):
  pointlist = []
  d = []
  candraw = True
  # Find points on screen
  for p in range(len(vertices)):
    a = cam.offsetpoint(vertices[p][0],vertices[p][1],vertices[p][2])
    pointlist.append([int(a[0]),int(a[2])])
    if a[0] > cam.xscreen*4 and a[2] > cam.yscreen*4:
      candraw = False
    d.append(a[1])
  if candraw:
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
    # Draws outline of shape on zbuffer
    for p in range(len(vertices)):
      if p > 0:
        drawline2dlist(points[p-1][0],points[p-1][1],points[p][0],points[p][1],zbufferpoly,d[p-1],d[p])
    drawline2dlist(points[p][0],points[p][1],points[0][0],points[0][1],zbufferpoly,d[p],d[0])
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
              if zbufferpoly[y][x] <= zbuffer[y+yl+cam.yscreen][x+xl+cam.xscreen]:
                surface.set_at((x+xl,y+yl),color)
                zbuffer[y+yl+cam.yscreen][x+xl+cam.xscreen] = zbufferpoly[y][x]
          except:
            pass
def drawface(surface,cam,zbuffer,vertices,pointlist,color=(100,100,100),texture=None):
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
def drawline2dlistzbuff(x1,y1,x2,y2,list2d,distance1,distance2,surface,color):
  x=x1
  y=y1
  d=distance2-distance1
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
    if list2d[y][x] > currentpixel:
      list2d[y][x] = currentpixel
      surface.set_at((x,y),color)
    numerator += shortest
    if not numerator<longest:
      numerator -= longest
      x += dx1
      y += dy1
    else:
      x += dx2
      y += dy2
    currentpixel += pixels
def drawline2dlist(x1,y1,x2,y2,list2d,distance1,distance2):
  x=x1
  y=y1
  d=distance2-distance1
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
class model:
  def __init__(self,filename,color,alist,size=1):
    self.x = 0
    self.y = 0
    self.z = 0
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
  def switchzy(self):
    pass
  def draw(self,surface,zbuffer,cam,perspective,filled=False,zbuff=True):
    vpos = []
    verpos = []
    for vx,vy,vz in self.v:
      vpos.append(cam.get3dpoint(vx+self.x,vy+self.y,vz+self.z))
      verpos.append([vx+self.x,vy+self.y,vz+self.z])
    cc = 0
    for polygon in self.polygons:
      points = []
      vert = []
      candraw = True
      for pointer in polygon:
        try:
          x = vpos[int(pointer)-1]
          y = verpos[int(pointer)-1]
        except:
          print polygon
        if x is None:
          candraw = False
        else:
          points.append(x)
          vert.append(y)
      if candraw:
        if filled:
          if zbuff:
            if perspective:
              drawface(surface,cam,zbuffer,vert,points,getcolor(cc))
            else:
              drawfacenp(surface,cam,zbuffer,vert,getcolor(cc))
          else:
            pygame.draw.polygon(surface,self.color,points,0)
        else:
          try:
            if distanceto(vert[0][0],vert[0][1],vert[0][2],cam.x,cam.y,cam.z) < 10:
              pygame.draw.lines(surface,self.color,True,points,1)
          except:
            pass
      cc += self.colord
def directionto((x1,y1),(x2,y2)): # Returns the angle from x1,y1 to x2,y2 in degrees -180 to 180
  if abs(x2-x1) < 10**-10:
    if y1 < y2:
      r = -90
    else:
      r = 90
  else:
    r = degrees(atan(float(y2-y1)/float(x2-x1)))
    if x2 < x1:
      if y2 < y1:
        r -= 180.0
      else:
        r += 180.0
  return r
def distanceto(x2,y2,z2,x1,y1,z1):
  return sqrt((x2-x1)**2+(y2-y1)**2+(z2-z1)**2)
def distance2(x,y):
  return sqrt(x**2+y**2)
class rect_prism:
  def __init__(self,x,y,z,dx,dy,dz,color,alist):
    self.x=x
    self.y=y
    self.z=z
    self.dx=dx
    self.dy=dy
    self.dz=dz
    self.color=color
    alist.append(self)
  def tp(self,x,y,z):
    newx = self.dx-self.x
    newy = self.dy-self.y
    newz = self.dz-self.z
    if x[0] == "~":
      if len(x) > 1:
        self.x += int(x[1:len(x):1])
        self.dx += int(x[1:len(x):1])
    else:
      self.x = int(x)-newx/2
    if y[0] == "~":
      if len(y) > 1:
        self.y += int(y[1:len(y):1])
        self.dy += int(y[1:len(y):1])
    else:
      self.y = int(y)-newy/2
    if z[0] == "~":
      if len(z) > 1:
        self.z += int(z[1:len(z):1])
        self.dz += int(z[1:len(z):1])
    else:
      self.z = int(z)-newz/2
  def draw(self,s,cam,zbuffer,wireframe=True,doted=False,textured=False):
    color = self.color
    vert1 = self.x,self.y,self.z
    vert2 = self.dx,self.y,self.z
    vert3 = self.dx,self.y,self.dz
    vert4 = self.x,self.y,self.dz
    vert5 = self.x,self.dy,self.z
    vert6 = self.dx,self.dy,self.z
    vert7 = self.dx,self.dy,self.dz
    vert8 = self.x,self.dy,self.dz
    v1 = cam.get3dpoint(vert1[0],vert1[1],vert1[2])
    v2 = cam.get3dpoint(vert2[0],vert2[1],vert2[2])
    v3 = cam.get3dpoint(vert3[0],vert3[1],vert3[2])
    v4 = cam.get3dpoint(vert4[0],vert4[1],vert4[2])
    v5 = cam.get3dpoint(vert5[0],vert5[1],vert5[2])
    v6 = cam.get3dpoint(vert6[0],vert6[1],vert6[2])
    v7 = cam.get3dpoint(vert7[0],vert7[1],vert7[2])
    v8 = cam.get3dpoint(vert8[0],vert8[1],vert8[2])
    if doted:
      if v1:
        pygame.draw.circle(s,(0,0,0),v1,2)
      if v2:
        pygame.draw.circle(s,(0,0,0),v2,2)
      if v3:
        pygame.draw.circle(s,(0,0,0),v3,2)
      if v4:
        pygame.draw.circle(s,(0,0,0),v4,2)
      if v5:
        pygame.draw.circle(s,(0,0,0),v5,2)
      if v6:
        pygame.draw.circle(s,(0,0,0),v6,2)
      if v7:
        pygame.draw.circle(s,(0,0,0),v7,2)
      if v8:
        pygame.draw.circle(s,(0,0,0),v8,2)
    if textured:
      color=self.color
      if v1 and v2 and v3 and v4:
        drawface(s,cam,zbuffer,[vert1,vert2,vert3,vert4],[v1,v2,v3,v4],(255,0,0))
      if v5 and v6 and v7 and v8:
        drawface(s,cam,zbuffer,[vert5,vert6,vert7,vert8],[v5,v6,v7,v8],(255,100,0))
      if v1 and v2 and v5 and v6:
        drawface(s,cam,zbuffer,[vert1,vert2,vert6,vert5],[v1,v2,v6,v5],(255,255,0))
      if v3 and v4 and v7 and v8:
        drawface(s,cam,zbuffer,[vert3,vert4,vert8,vert7],[v3,v4,v8,v7],(0,255,0))
      if v1 and v4 and v8 and v5:
        drawface(s,cam,zbuffer,[vert1,vert4,vert8,vert5],[v1,v4,v8,v5],(0,0,255))
      if v2 and v3 and v6 and v7:
        drawface(s,cam,zbuffer,[vert2,vert3,vert7,vert6],[v2,v3,v7,v6],(255,0,255))
    if wireframe:
      color=self.color
      try:
        if v1 and v2:
          pygame.draw.line(s,color,v1,v2,1)
        if v2 and v3:
          pygame.draw.line(s,color,v2,v3,1)
        if v3 and v4:
          pygame.draw.line(s,color,v3,v4,1)
        if v4 and v1:
          pygame.draw.line(s,color,v4,v1,1)
        if v1 and v5:
          pygame.draw.line(s,color,v1,v5,1)
        if v5 and v6:
          pygame.draw.line(s,color,v5,v6,1)
        if v6 and v7:
          pygame.draw.line(s,color,v6,v7,1)
        if v7 and v8:
          pygame.draw.line(s,color,v7,v8,1)
        if v8 and v5:
          pygame.draw.line(s,color,v8,v5,1)
        if v2 and v6:
          pygame.draw.line(s,color,v2,v6,1)
        if v4 and v8:
          pygame.draw.line(s,color,v4,v8,1)
        if v3 and v7:
          pygame.draw.line(s,color,v3,v7,1)
      except:
        print "error"
def main():
  gamecamera=camera(0.0,0.0,-2.0,(0.0,0.0),100,(800,600))
  pygame.init()
  prisms = []
  #bad = []
  #rect_prism(-0.5,-0.5,-0.5,0.5,0.5,0.5,(0,255,0),prisms)
  #rect_prism(0,10,0,10,20,10,(255,0,0),bad)
  models = []
  #model("QUEEN.POL",(0,100,0),models,1)
  #model("Keychain.obj",(0,255,0),models,0.1)
  model("Plane.obj",(100,70,0),models,0.1)
  model("Plane.obj",(100,70,0),models,0.1)
  model("space_ship.obj",(150,150,150),models,0.005)
  #model("Pirates of the Caribbean.obj",(150,150,150),models,0.005)
  models[1].x = 10
  screen = pygame.display.set_mode((800,600))
  surface = pygame.Surface((gamecamera.resolution[0],gamecamera.resolution[1]))
  clock = pygame.time.Clock()
  keys = []
  done = False
  pygame.mouse.set_pos([gamecamera.resolution[0]/2, gamecamera.resolution[1]/2])
  pygame.event.get()
  pygame.mouse.set_visible(False)
  mousestuck = True
  zoom=100
  while not done:
    clock.tick(60)
    zbuffer=[[10000 for a in range(gamecamera.resolution[0]+1)] for b in range(gamecamera.resolution[1]+1)]
    newkeys=[]
    rel = [0,0]
    #bad[0].tp("~","~","~1")
    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        keys.append(event.key)
        newkeys.append(event.key)
      elif event.type == pygame.KEYUP:
        keys.remove(event.key)
      elif event.type == pygame.MOUSEMOTION:
        rel = event.rel
      elif event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 4:
          zoom += 1
        if event.button == 5:
          zoom -= 1
        if zoom < 5:
          zoom = 5
        if zoom > 100:
          zoom = 100
        gamecamera.resolution = [int(800*zoom/100.0),int(600*zoom/100.0)]
        gamecamera.xscreen = gamecamera.resolution[0]/2
        gamecamera.yscreen = gamecamera.resolution[1]/2
        gamecamera.filmdivy = gamecamera.yscreen/gamecamera.film
        surface = pygame.Surface((gamecamera.resolution[0],gamecamera.resolution[1]))
    if mousestuck:
      pygame.mouse.set_pos([gamecamera.resolution[0]/2, gamecamera.resolution[1]/2])
    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        keys.append(event.key)
        newkeys.append(event.key)
      if event.type == pygame.KEYUP:
        keys.remove(event.key)
    speed = .05
    if pygame.K_ESCAPE in newkeys:
      mousestuck = not mousestuck
      pygame.mouse.set_visible(not mousestuck)
    if pygame.K_p in newkeys:
      rect_prism(gamecamera.x-.1,gamecamera.y-.1,gamecamera.z-.1,gamecamera.x+.1,gamecamera.y+.1,gamecamera.z+.1,getcolor(random.randrange(0,1531)),prisms)
      print prisms
    if pygame.K_LCTRL in keys:
      speed = .08
    elif pygame.K_v in keys:
      speed = .1
    elif pygame.K_c in keys:
      speed = .01
    if pygame.K_w in keys: # Move Forward
      gamecamera.x += cos(gamecamera.direction[0]-1.570795)*speed
      gamecamera.y += sin(gamecamera.direction[0]-1.570795)*speed
    if pygame.K_a in keys: # Move Left
      gamecamera.x += cos(gamecamera.direction[0]+3.14159)*speed
      gamecamera.y += sin(gamecamera.direction[0]+3.14159)*speed
    if pygame.K_d in keys: # Move Right
      gamecamera.x += cos(gamecamera.direction[0])*speed
      gamecamera.y += sin(gamecamera.direction[0])*speed
    if pygame.K_s in keys: # Move Backwards
      gamecamera.x += cos(gamecamera.direction[0]+1.570795)*speed
      gamecamera.y += sin(gamecamera.direction[0]+1.570795)*speed
    if pygame.K_SPACE in keys: # Move Up
      gamecamera.z -= speed
    if pygame.K_LSHIFT in keys: # Move Down
      gamecamera.z += speed
    if pygame.K_q in newkeys:
      done = True
    if mousestuck:
      gamecamera.direction[0] += rel[0]/100.0
      gamecamera.direction[1] -= rel[1]/100.0
      if gamecamera.direction[0] > 3.14159:
        gamecamera.direction[0] = -3.14159
      if gamecamera.direction[0] < -3.14159:
        gamecamera.direction[0] = 3.14159
      if gamecamera.direction[1] > 1.570795:
        gamecamera.direction[1] = 1.570795
      if gamecamera.direction[1] < -1.570795:
        gamecamera.direction[1] = -1.570795
    y = ((sin(gamecamera.direction[1]) * 10/abs(cos(gamecamera.direction[1]) * 10)) / gamecamera.film)*gamecamera.resolution[1]/2+gamecamera.resolution[1]/2
    if y < 0:
      y = 0
    if y > gamecamera.resolution[1]:
      y = gamecamera.resolution[1]
    surface.fill((0,255,255))
    pygame.draw.rect(surface,(0,150,150),(0,y,gamecamera.resolution[0],gamecamera.resolution[1]))
    for rect in prisms:
      rect.draw(surface,gamecamera,zbuffer,True,True,False)
    for thing in models:
      thing.draw(surface,zbuffer,gamecamera,True,False,False)
    models[0].x += .01
    models[1].x -= .01
    models[2].y += .05
    for i in range(len(models)-4):
      models[i+4].life -= 1
      models[i+4].y -= 0.1
      models[i+4].x += models[i+4].vx
      models[i+4].z += models[i+4].vz
      if models[i+4].life == 0:
        del models[i+4]
        break
    if random.randrange(0,2) == 0:
      m = model("star.obj",(255,0,0),models,0.001)
      m.x = models[2].x
      m.y = models[2].y
      m.vx = random.randrange(-5,5)/50.0
      m.vz = random.randrange(-5,5)/50.0
      m.life = 10
    pygame.transform.scale(surface, (800, 600), screen)
    try:
      label = gamecamera.get3dpoint(0,0,0)
      if label:
        surface.blit(font(20,"(0,0,0)"),label)
    except:
      print label
    #for rect in bad:
     # rect.draw(surface,gamecamera)
    screen.blit(font(20,"Position: %s, %s, %s" %(gamecamera.x,gamecamera.y,gamecamera.z)),(0,0))
    screen.blit(font(20,"Perspective: %s, %s" %(gamecamera.direction[0],gamecamera.direction[1])),(0,20))
    screen.blit(font(20,"Zoom: %s" %(zoom)),(0,40))
    pygame.display.flip()
    #raw_input()
main()
pygame.quit()
