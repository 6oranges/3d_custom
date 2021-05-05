import pygame
from math import *
import random
def font(size, text,color=(0,0,0),font=None):
  return pygame.font.Font(font, size).render(text, True, color)
def getcolor(color):
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
    self.angle=angle
    self.resolution=resolution
    self.xscreen = resolution[0]/2
    self.yscreen = resolution[1]/2
    self.twobig = resolution[0]*2
    self.film = tan(radians(self.angle/2))
  def offsetpoint(self,x,y,z):
    # Offsets the point from the camera
    newx = x-self.x
    newy = y-self.y
    newz = z-self.z
    
    # Calculates distance between point and camera on xy plane
    distancexy = distanceto(newx,newy,0,0,0,0)
    
    # Calculates angle from the camera's xy position to the point's xy position
    xydir = degrees(atan2(newy,newx))
    
    # Finds offset angle from camera to point
    xydir -= self.direction[0]

    # Recalculates position of xy from offset
    newx = cos(radians(xydir)) * distancexy
    newy = sin(radians(xydir)) * distancexy
    
    # Calculates distance between point and camera on yz plane
    distancezy = distanceto(newy,newz,0,0,0,0)

    # Calculates angle from the camera's yz position to the point's xy position
    yzdir = degrees(atan2(newz,newy))

    # Finds offset angle from camera to point
    yzdir -= self.direction[1]
    
    # Recalculates position of zy from offset
    newy = cos(radians(yzdir)) * distancezy
    newz = sin(radians(yzdir)) * distancezy
    return (newx,newy,newz)
  def get3dpoint(self,x,y,z):
    (newx,newy,newz) = self.offsetpoint(x,y,z)
    # makes sure position is in front of camera before returning
    if newy < 0:
      # finds the xy position on film
      xyangle = newx/abs(newy)
      zyangle = newz/abs(newy)
      
      # Finds positions on screen
      xposition = (xyangle / self.film)*self.yscreen+self.xscreen
      yposition = (zyangle / self.film)*self.yscreen+self.yscreen
      if abs(xposition) > self.twobig:
        return None
      if abs(yposition) > self.twobig:
        return None
      return (int(xposition),int(yposition))
    else:
      return None
def drawface2(surface,cam,zbuffer,vertices,pointlist,color=(100,100,100)):
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
  poly=pygame.Surface((width+1,height+1))
  pygame.draw.polygon(poly,color,points)

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
  
  # Check distances
  for y in range(height):
    # Finds start and end of each line
    lookfor = 0
    startx=None
    endx=None
    for x in range(width):
      if lookfor == 0:
        if poly.get_at((x,y)) == color:
          lookfor = 1
          startx = x+1
      elif lookfor == 1:
        if poly.get_at((x,y)) != color:
          lookfor = 2
          endx=x-1
          break
    # Makes sure it found start and end
    if lookfor == 2 and endx > startx:
      spreadsize = endx-startx
      spreaddist = zbufferpoly[y][endx]-zbufferpoly[y][startx]
      spread = spreaddist/spreadsize
      current = zbufferpoly[y][startx]
      # fills in line
      for x in range(startx,endx+1):
        zbufferpoly[y][x] = current
        current += spread
        try:
          if zbufferpoly[y][x] <= zbuffer[y+yl][x+xl]:
            surface.set_at((x+xl,y+yl),color)
            zbuffer[y+yl][x+xl] = zbufferpoly[y][x]
        except:
          pass
def drawface(surface,cam,zbuffer,vertices,pointlist,color=(100,100,100)):
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
          endx=x
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
          if zbufferpoly[y][x] <= zbuffer[y+yl][x+xl]:
            surface.set_at((x+xl,y+yl),color)
            zbuffer[y+yl][x+xl] = zbufferpoly[y][x]
        except:
          pass
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
  def __init__(self,filename,color,alist,size=1,xyz=(0,0,0)):
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
          self.v.append([float(pars[1])*size+xyz[0],float(pars[2])*size+xyz[1],float(pars[3])*-size+xyz[2]])
        elif pars[0] == "f":
          #if i%every==0:
##            currentpolygon = []
##            for point in range(len(pars)-1):
##              currentpolygon.append(self.v[int(pars[point+1])-1])
##            self.polygons.append(currentpolygon)
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
  def draw(self,surface,zbuffer,cam,filled):
    vpos = []
    for vertice in self.v:
      vpos.append(cam.get3dpoint(vertice[0],vertice[1],vertice[2]))
    cc = 0
    for polygon in self.polygons:
      points = []
      vert = []
      candraw = True
      for pointer in polygon:
        try:
          x = vpos[int(pointer)-1]
          y = self.v[int(pointer)-1]
        except:
          print polygon
        if x is None:
          candraw = False
        else:
          points.append(x)
          vert.append(y)
      if candraw:
        if filled:
          drawface(surface,cam,zbuffer,vert,points,getcolor(cc))
          #pygame.draw.polygon(surface,self.color,points,0)
        else:
          pygame.draw.lines(surface,(0,0,0),True,points,1)
      cc += self.colord
##    for polygon in self.polygons:
##      #pygame.draw.lines(surface)
##      x=[]
##      d=True
##      for point in range(len(polygon)):
##        y = cam.get3dpoint(polygon[point][0],polygon[point][1],polygon[point][2])
##        if y is not None:
##          x.append(y)
##        else:
##          d=False
##      if d and len(x)>0:
##        if filled:
##          pygame.draw.polygon(surface,self.color,x,0)
##        else:
##          pygame.draw.lines(surface,self.color,True,x,1)

      
##        try:
##          if point+1 == len(polygon):
##            pygame.draw.line(surface,self.color,cam.get3dpoint(polygon[point][0],polygon[point][1],polygon[point][2]),cam.get3dpoint(polygon[0][0],polygon[0][1],polygon[0][2]),1)
##          else:
##            pygame.draw.line(surface,self.color,cam.get3dpoint(polygon[point][0],polygon[point][1],polygon[point][2]),cam.get3dpoint(polygon[point+1][0],polygon[point+1][1],polygon[point+1][2]),1)
##        except:
##          pass
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
      # todo zbuffer algorithom
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
      color=(0,0,0)
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
  #model("dragon.obj",(0,255,0),models,1)
  screen = pygame.display.set_mode((800,600))
  surface = pygame.Surface((gamecamera.resolution[0],gamecamera.resolution[1]))
  clock = pygame.time.Clock()
  keys = []
  done = False
  pygame.mouse.set_pos([gamecamera.resolution[0]/2, gamecamera.resolution[1]/2])
  pygame.event.get()
  pygame.mouse.set_visible(False)
  mousestuck = True
  while not done:
    clock.tick(60)
    zbuffer=[[255 for a in range(gamecamera.resolution[0]+1)] for b in range(gamecamera.resolution[1]+1)]
    surface.fill((0,255,255))
    newkeys=[]
    rel = [0,0]
    #bad[0].tp("~","~","~1")
    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        keys.append(event.key)
        newkeys.append(event.key)
      if event.type == pygame.KEYUP:
        keys.remove(event.key)
      if event.type == pygame.MOUSEMOTION:
        rel = event.rel
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
      rect_prism(gamecamera.x-1,gamecamera.y-1,gamecamera.z-1,gamecamera.x+1,gamecamera.y+1,gamecamera.z+1,getcolor(random.randrange(0,1531)),prisms)
    if pygame.K_LCTRL in keys:
      speed = .08
    elif pygame.K_v in keys:
      speed = .1
    elif pygame.K_c in keys:
      speed = .01
    if pygame.K_w in keys: # Move Forward
      gamecamera.x += cos(radians(gamecamera.direction[0]-90))*speed
      gamecamera.y += sin(radians(gamecamera.direction[0]-90))*speed
    if pygame.K_a in keys: # Move Left
      gamecamera.x += cos(radians(gamecamera.direction[0]-180))*speed
      gamecamera.y += sin(radians(gamecamera.direction[0]-180))*speed
    if pygame.K_d in keys: # Move Right
      gamecamera.x += cos(radians(gamecamera.direction[0]))*speed
      gamecamera.y += sin(radians(gamecamera.direction[0]))*speed
    if pygame.K_s in keys: # Move Backwards
      gamecamera.x += cos(radians(gamecamera.direction[0]+90))*speed
      gamecamera.y += sin(radians(gamecamera.direction[0]+90))*speed
    if pygame.K_SPACE in keys: # Move Up
      gamecamera.z -= speed
    if pygame.K_LSHIFT in keys: # Move Down
      gamecamera.z += speed
    if pygame.K_q in newkeys:
      done = True
    if mousestuck:
      gamecamera.direction[0] += rel[0]
      gamecamera.direction[1] -= rel[1]
      if gamecamera.direction[0] > 180:
        gamecamera.direction[0] = -180
      if gamecamera.direction[0] < -180:
        gamecamera.direction[0] = 180
      if gamecamera.direction[1] > 90:
        gamecamera.direction[1] = 90
      if gamecamera.direction[1] < -90:
        gamecamera.direction[1] = -90
    y = ((sin(radians(gamecamera.direction[1])) * 10/abs(cos(radians(gamecamera.direction[1])) * 10)) / gamecamera.film)*gamecamera.resolution[1]/2+gamecamera.resolution[1]/2
    if y < 0:
      y = 0
    if y > gamecamera.resolution[1]:
      y = gamecamera.resolution[1]
    pygame.draw.rect(surface,(0,150,150),(0,y,gamecamera.resolution[0],gamecamera.resolution[1]))
    for rect in prisms:
      rect.draw(surface,gamecamera,zbuffer,False,False,True)
    for thing in models:
      thing.draw(surface,zbuffer,gamecamera,False)
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
    pygame.display.flip()
    #raw_input()
main()
pygame.quit()
