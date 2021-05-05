import pygame, sys, os, math,random

def rotate2d(pos,rad):
  x,y=pos
  s,c=math.sin(rad),math.cos(rad)
  return x*c-y*s,y*c+x*s
class Cam:
  def __init__(self,pos=(0,0,0),rot=(0,0)):
    self.pos = list(pos)
    self.rot = list(rot)
  def events(self,event):
    if event.type == pygame.MOUSEMOTION:
      x,y = event.rel
      x /=200.0
      y /=200.0
      self.rot[0]+=y
      self.rot[1]+=x
  def update(self,dt,key):
    s = 1
    if key[pygame.K_SPACE]:
      self.pos[1]-=s
    if key[pygame.K_LSHIFT]:
      self.pos[1]+=s
    x,y = s*math.sin(self.rot[1]),s*math.cos(self.rot[1])
    if key[pygame.K_w]:
      self.pos[0]+=x
      self.pos[2]+=y
    if key[pygame.K_s]:
      self.pos[0]-=x
      self.pos[2]-=y
    if key[pygame.K_a]:
      self.pos[0]-=y
      self.pos[2]+=x
    if key[pygame.K_d]:
      self.pos[0]+=y
      self.pos[2]-=x

class Obj:
  def __init__(self,vertices,faces,colors=None,edges=None):
    self.name     = "Undefined"
    self.verts    = vertices
    self.edges    = edges
    self.faces    = faces
    self.colors   = colors
    if self.colors == None:
      self.colors = [(random.randrange(0,255),0,0) for c in range(len(self.faces))]
class Drawable:
  def __init__(self,obj,(x,y,z)):
    self.obj = obj
    
    self.filled    = True
    self.sorted    = True
    self.vertplot  = False
    self.linesdraw = False

    self.x=x
    self.y=y
    self.z=z
    self.size=1
def Cube():
  obj=Obj(((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)),
                ((0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(0,3,7,4),(1,2,6,5)),
                ((128,128,128),(128,128,128),(255,255,255),(100,100,100),(200,200,200),(200,200,200)),#((255,0,0),(255,128,0),(255,255,0),(255,255,255),(0,0,255),(0,255,0)),
                ((0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)))
  obj.name = "Cube"
  return obj
def openobj(filepath):
  lines = open(filepath,"r").read().split("\n")
  verts = []
  faces = []
  for line in lines:
    inputs = line.split(" ")
    linetype = inputs[0]
    if linetype == "v":
      verts.append((float(inputs[1]),-float(inputs[2]),float(inputs[3])))
    if linetype == "f":
      try:
        faces.append([int(v) for v in inputs[1::]])
      except:
        print "Error (invalid face inputs): " + " ".join(inputs)
    if linetype == "#":
      pass
    if linetype == "vn":
      pass
    
  obj=Obj(verts,faces)
  obj.name = filepath.split("/")[len(filepath.split("/"))-1].split(".")[0]
  return obj
def openx3d(filepath):
  contents = open(filepath,"r").read().replace("\n","").replace("    ","  ")
  colorIndex = contents.index("colorIndex='")
  coordIndex = contents.index("coordIndex='")
  pointIndex = contents.index("><Coordinate point='")
  colorsIndex= contents.index("/><Color color=")
  endIndex   = contents.index("/></IndexedFaceSet></Shape></Scene></X3D>")
  facecolorindexes =  [int(i) for i in contents[colorIndex+14:coordIndex-4:].split("  ")]
  faces    = [[int(a) for a in i.split(" ")[:len(i.split(" "))-1:]] for i in contents[coordIndex+14:pointIndex-3:].split("  ")]
  vertices = [(float(i.split(" ")[0])*1000,float(i.split(" ")[1])*-1000,float(i.split(" ")[2])*1000) for i in contents[pointIndex+22:colorsIndex-4].split("  ")]
  colors   = [[int(float(a)*255) for a in i.split(" ")] for i in contents[colorsIndex+18:endIndex-2].split("  ")]
  colorfaces = [colors[i] for i in facecolorindexes]
  
  obj = Obj(vertices,faces,colorfaces)
  obj.name = filepath.split("/")[len(filepath.split("/"))-1].split(".")[0]
  return obj
def openfile(filepath):
  ext=filepath.split(".")[len(filepath.split("."))-1]
  if ext == "x3d":
    return openx3d(filepath)
  elif ext == "obj":
    return openobj(filepath)
  else:
    raise "filetype: '" + ext + "' is not supported by this program."
pygame.init()
w,h = 800,600
cx,cy = w/2,h/2
fov = min(w,h)
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.display.set_caption('3d graphics')
screen = pygame.display.set_mode((w,h))
clock = pygame.time.Clock()
cube = Cube()

cam = Cam((0,0,0))

pygame.event.get()
pygame.mouse.get_rel()
pygame.mouse.set_visible(0)
pygame.event.set_grab(1)
drawables = []
cube_points = []
##for i in range(20):
##  cube_points.append((random.randrange(-50,50),random.randrange(-50,50),random.randrange(-50,50)))
#cube_points.append((0,0,0))
drawables += [Drawable(cube,(x,y,z)) for x,z,y in cube_points]
for drawable in drawables:
  drawable.life = 50
##v,f=openobj("Pirates of the Caribbean.obj")
##drawables.append(Drawable(v,f))
plane=openfile("train.x3d")
drawables.append(Drawable(plane,(0,0,0)))
while True:
  dt =clock.tick()/1000
  if random.randrange(0,10) == 1:
    a=Drawable(cube,(0,-60,30))
    a.life = 50
    drawables.append(a)
  for a in range(len(drawables)-1,1,-1):
    if drawables[a].obj.name == "Cube":
      drawables[a].x += random.randrange(-1,2)
      drawables[a].y += random.randrange(-1,1)
      drawables[a].z += random.randrange(-2,1)
      drawables[a].size += 0.1
      drawables[a].life -= 1
      if drawables[a].life <= 0:
        del drawables[a]
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        pygame.quit()
        sys.exit()
      
    cam.events(event)

  screen.fill((255,128,255))
  for obj in drawables:
    if obj.vertplot:
      for x,y,z in obj.obj.verts:
        x *= obj.size
        y *= obj.size
        z *= obj.size
        
        x += obj.x
        y += obj.y
        z += obj.z
                     
        x-=cam.pos[0]
        y-=cam.pos[1]
        z-=cam.pos[2]

        x,z = rotate2d((x,z),cam.rot[1])
        y,z = rotate2d((y,z),cam.rot[0])
        if z == 0:
          f = max(w,h)
        else:
          f = fov/z
        x,y = x*f,y*f
        pygame.draw.circle(screen,(0,0,0),(cx+int(x),cy+int(y)),6)
    if obj.linesdraw:
      for edge in obj.obj.edges:

        points = []
        for x,y,z in (obj.obj.verts[edge[0]],obj.obj.verts[edge[1]]):
          x *= obj.size
          y *= obj.size
          z *= obj.size
          
          x += obj.x
          y += obj.y
          z += obj.z
                     
          x-=cam.pos[0]
          y-=cam.pos[1]
          z-=cam.pos[2]

          x,z = rotate2d((x,z),cam.rot[1])
          y,z = rotate2d((y,z),cam.rot[0])
          if z == 0:
            f = max(w,h)
          else:
            f = fov/z
          x,y = x*f,y*f
          points += [(cx+int(x),cy+int(y))]
        try:
          pygame.draw.line(screen,(0,0,0),points[0],points[1],1)
        except:
          pass

  
  face_list = []
  face_color = []
  depth = []

  for obj in drawables:
    if obj.filled:
      vert_list = []
      screen_coords = []
      for x,y,z in obj.obj.verts:
        x *= obj.size
        y *= obj.size
        z *= obj.size
        
        x += obj.x
        y += obj.y
        z += obj.z
                     
        x-=cam.pos[0]
        y-=cam.pos[1]
        z-=cam.pos[2]
        x,z = rotate2d((x,z),cam.rot[1])
        y,z = rotate2d((y,z),cam.rot[0])
        vert_list += [(x,y,z)]
        if z == 0:
          f = max(w,h)
        else:
          f = fov/z
        x,y = x*f,y*f
        screen_coords += [(cx+int(x),cy+int(y))]

      
      
      for f in range(len(obj.obj.faces)):
        try:
          face = obj.obj.faces[f]
          
          on_screen= False
          for i in face:
            x,y = screen_coords[i]
            if vert_list[i][2]>0 and x>0 and x<w and y>0 and y<h:
              on_screen = True
              break
          if on_screen:
            coords = [screen_coords[i] for i in face]
            face_list += [coords]
            face_color += [obj.obj.colors[f]]
            if obj.sorted:
              depth+=[sum(sum(vert_list[j][i]/len(face) for j in face)**2 for i in range(3))]
            #depth+=[sum(sum(vert_list[j][i] for j in face)**2 for i in range(3))]
        except Exception as e:
          print e
    if obj.sorted:
      order = sorted(range(len(face_list)),key=lambda i: depth[i],reverse=1)
    else:
      order = range(len(face_list))
    for i in order:
      try:
        pygame.draw.polygon(screen,face_color[i],face_list[i])
      except:
        print "Can't draw poly"

    
  pygame.display.flip()
  key = pygame.key.get_pressed()
  cam.update(dt,key)
