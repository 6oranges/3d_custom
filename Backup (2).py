import pygame
from math import *
def font(size, text,color=(0,0,0),font=None):
  return pygame.font.Font(font, size).render(text, True, color)
class camera: # Creates a camera with a position direction and FOV
  def __init__(self,x,y,z,direction,angle,resolution): # direction is 2 angles; angle is FOV
    self.x=x
    self.y=y
    self.z=z
    self.direction=list(direction)
    self.angle=angle
    self.resolution=resolution
  def get3dpoint(self,x,y,z): 
    distancexy = distanceto(self.x,self.y,0,x,y,0)
    distancezy = distanceto(self.y,self.z,0,y,z,0)
    newx = x-self.x # Offsets the point from the camera
    newy = y-self.y
    newz = z-self.z
    xydir = directionto((newx,newy),(0,0)) # Calculates angle from camera to point xy
    xydir -= self.direction[0] # Offsets angle from camera to point so that the camera is facing -y
    newx = sin(radians(xydir)) * distancexy # recalculates position of xy from angle
    newy = cos(radians(xydir)) * distancexy
    zydir = directionto((newy,newz),(0,0))
    zydir -= self.direction[1]
    newy = sin(radians(zydir)) * distancezy # recalculates position of zy from angle
    newz = cos(radians(zydir)) * distancezy
    film = tan(radians(self.angle)) # Calculates the film size that captures point
##    newx *= 10**12 # Round to the nearest tenth digit
##    newy *= 10**12
##    newz *= 10**12
##    newx = round(newx)
##    newy = round(newy)
##    newz = round(newz)
##    newx *= 10**-12
##    newy *= 10**-12
##    newz *= 10**-12
    xyangle = newx/abs(newy) # finds the xy position on film
    zyangle = newz/abs(newy)
    if newy < 0: # makes sure position is in front of camera
      xposition = (xyangle / film)*self.resolution[0]/2+self.resolution[0]/2 # Finds position on screen
      yposition = (zyangle / film)*self.resolution[1]/2+self.resolution[0]/2 # Finds position on screen
      return (int(xposition),int(yposition))
    else:
      return None
class model:
  def __init__(self,filename,color,alist,every):
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
        pars = lines[i].split(" ")
        if len(pars) < 4:
          pass
        elif pars[0] == "v":
          self.v.append([float(pars[1])*100,float(pars[2])*100,float(pars[3])*-100])
        elif pars[0] == "f":
          if i%every==0:
##            currentpolygon = []
##            for point in range(len(pars)-1):
##              currentpolygon.append(self.v[int(pars[point+1])-1])
##            self.polygons.append(currentpolygon)
            self.polygons.append(pars[1:len(pars):1])
        else:
          raise BaseException("Only Supports faces and vetices, line: "+str(i)+" has type: "+str(pars))
    else:
      raise BaseException("Not Recognized File type: "+x[len(x)-1])
  def switchzy(self):
    pass
  def draw(self,surface,cam,filled):
    vpos = []
    for vertice in self.v:
      vpos.append(cam.get3dpoint(vertice[0],vertice[1],vertice[2]))
    for polygon in self.polygons:
      points = []
      candraw = True
      for pointer in polygon:
        x = vpos[int(pointer)-1]
        if x is None:
          candraw = False
        else:
          points.append(x)
      if candraw:
        if filled:
          pygame.draw.polygon(surface,self.color,points,0)
        else:
          pygame.draw.lines(surface,self.color,True,points,1)
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
def directionto((x2,y2),(x1,y1)):
  if abs(y2-y1) == 0:
    if x2 < x1:
      r = -90
    else:
      r = 90
  else:
    r = degrees(atan(float(x2-x1)/float(y2-y1)))
    if y2 < y1:
      if x2 < x1:
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
  def draw(self,s,cam,wireframe=True,doted=False,textured=False):
    color = self.color
    if doted:
      try:
        pygame.draw.circle(s,(0,0,0),cam.get3dpoint(self.x,self.y,self.z),2)
      except:
        pass
      try:
        pygame.draw.circle(s,(0,0,0),cam.get3dpoint(self.dx,self.y,self.z),2)
      except:
        pass
      try:
        pygame.draw.circle(s,(0,0,0),cam.get3dpoint(self.dx,self.y,self.dz),2)
      except:
        pass
      try:
        pygame.draw.circle(s,(0,0,0),cam.get3dpoint(self.x,self.y,self.dz),2)
      except:
        pass
      try:
        pygame.draw.circle(s,(0,0,0),cam.get3dpoint(self.x,self.dy,self.z),2)
      except:
        pass
      try:
        pygame.draw.circle(s,(0,0,0),cam.get3dpoint(self.dx,self.dy,self.z),2)
      except:
        pass
      try:
        pygame.draw.circle(s,(0,0,0),cam.get3dpoint(self.dx,self.dy,self.dz),2)
      except:
        pass
      try:
        pygame.draw.circle(s,(0,0,0),cam.get3dpoint(self.x,self.dy,self.dz),2)
      except:
        pass
    if wireframe:
      try:
        pygame.draw.line(s,color,cam.get3dpoint(self.x,self.y,self.z),cam.get3dpoint(self.dx,self.y,self.z),1)
      except:
        pass
      try:
        pygame.draw.line(s,color,cam.get3dpoint(self.dx,self.y,self.z),cam.get3dpoint(self.dx,self.y,self.dz),1)
      except:
        pass
      try:
        pygame.draw.line(s,color,cam.get3dpoint(self.dx,self.y,self.dz),cam.get3dpoint(self.x,self.y,self.dz),1)
      except:
        pass
      try:
        pygame.draw.line(s,color,cam.get3dpoint(self.x,self.y,self.dz),cam.get3dpoint(self.x,self.y,self.z),1)
      except:
        pass
      try:
        pygame.draw.line(s,color,cam.get3dpoint(self.x,self.y,self.z),cam.get3dpoint(self.x,self.dy,self.z),1)
      except:
        pass
      try:
        pygame.draw.line(s,color,cam.get3dpoint(self.x,self.dy,self.z),cam.get3dpoint(self.dx,self.dy,self.z),1)
      except:
        pass
      try:
        pygame.draw.line(s,color,cam.get3dpoint(self.dx,self.dy,self.z),cam.get3dpoint(self.dx,self.dy,self.dz),1)
      except:
        pass
      try:
        pygame.draw.line(s,color,cam.get3dpoint(self.dx,self.dy,self.dz),cam.get3dpoint(self.x,self.dy,self.dz),1)
      except:
        pass
      try:
        pygame.draw.line(s,color,cam.get3dpoint(self.x,self.dy,self.dz),cam.get3dpoint(self.x,self.dy,self.z),1)
      except:
        pass
      try:
        pygame.draw.line(s,color,cam.get3dpoint(self.dx,self.y,self.z),cam.get3dpoint(self.dx,self.dy,self.z),1)
      except:
        pass
      try:
        pygame.draw.line(s,color,cam.get3dpoint(self.x,self.y,self.dz),cam.get3dpoint(self.x,self.dy,self.dz),1)
      except:
        pass
      try:
        pygame.draw.line(s,color,cam.get3dpoint(self.dx,self.y,self.dz),cam.get3dpoint(self.dx,self.dy,self.dz),1)
      except:
        pass
    if textured:
      pass #zbuffer algorithom
def main():
  gamecamera=camera(0.0,200.0,0.0,(0.0,0.0),50,(1000,750))
  pygame.init()
  prisms = []
  #bad = []
  rect_prism(0,100,0,100,200,100,(255,200,0),prisms)
  #rect_prism(0,10,0,10,20,10,(255,0,0),bad)
  models = []
  #model("QUEEN.POL",(0,100,0),models,1)
  #model("dragon.obj",(100,100,100),models,1)
  surface = pygame.display.set_mode((gamecamera.resolution[0],gamecamera.resolution[1]))
  clock = pygame.time.Clock()
  keys = []
  done = False
  rel = [0,0]
  pygame.mouse.set_pos([250, 250])
  pygame.event.get()
  pygame.mouse.set_visible(False)
  mousestuck = True
  while not done:
    clock.tick(60)
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
    speed = 10
    if pygame.K_ESCAPE in newkeys:
      mousestuck = not mousestuck
      pygame.mouse.set_visible(not mousestuck)
    if pygame.K_p in newkeys:
      rect_prism(gamecamera.x-50,gamecamera.y-50,gamecamera.z-50,gamecamera.x+50,gamecamera.y+50,gamecamera.z+50,(255,200,0),prisms)
    if pygame.K_LCTRL in keys:
      speed = 100
    elif pygame.K_v in keys:
      speed = 1000
    elif pygame.K_c in keys:
      speed = 1
    if pygame.K_w in keys:
      gamecamera.x -= sin(radians(gamecamera.direction[0]))*speed
      gamecamera.y -= cos(radians(gamecamera.direction[0]))*speed
    if pygame.K_a in keys:
      gamecamera.x -= sin(radians(gamecamera.direction[0]+90))*speed
      gamecamera.y -= cos(radians(gamecamera.direction[0]+90))*speed
    if pygame.K_d in keys:
      gamecamera.x -= sin(radians(gamecamera.direction[0]-90))*speed
      gamecamera.y -= cos(radians(gamecamera.direction[0]-90))*speed
    if pygame.K_s in keys:
      gamecamera.x -= sin(radians(gamecamera.direction[0]+180))*speed
      gamecamera.y -= cos(radians(gamecamera.direction[0]+180))*speed
    if pygame.K_SPACE in keys:
      gamecamera.z -= speed
    if pygame.K_LSHIFT in keys:
      gamecamera.z += speed
    if pygame.K_q in newkeys:
      done = True
    if mousestuck:
      gamecamera.direction[0] -= rel[0]
      gamecamera.direction[1] += rel[1]
    for rect in prisms:
      rect.draw(surface,gamecamera)
    for thing in models:
      thing.draw(surface,gamecamera,False)
    #for rect in bad:
     # rect.draw(surface,gamecamera)
    surface.blit(font(20,"Position: %s, %s, %s" %(gamecamera.x,gamecamera.y,gamecamera.z)),(0,0))
    surface.blit(font(20,"Perspective: %s, %s" %(gamecamera.direction[0],gamecamera.direction[1])),(0,20))
    pygame.display.flip()
main()
pygame.quit()
