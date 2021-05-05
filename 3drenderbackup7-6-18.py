import pygame
import math
mode=[0]
errors=[0]
MAXDISTANCE=100000.0
INVERSEMAXDISTANCE=1/MAXDISTANCE
def rectcollide(rect1,rect2):
    if rect1[0]<rect2[0]+rect2[2] and rect2[0]<rect1[0]+rect1[2]:
        if rect1[1]<rect2[1]+rect2[3] and rect2[1]<rect1[1]+rect1[3]:
            return True
    return False
def distanceto(x1,y1,z1,x2,y2,z2):
    return math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)
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
class Point:
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
    def update(self,camera):
        offsetedpoint=camera.offsetpoint(self.x,self.y,self.z)
        if offsetedpoint[1]>0:
            self.distancetocamera=1/abs(offsetedpoint[1])
            self.screenx,self.screeny=camera.screenpos(offsetedpoint[0],offsetedpoint[1],offsetedpoint[2],True)
        else:
            self.distancetocamera=None
            self.screenx=None
            self.screeny=None
class Triangle:
    def __init__(self,point1,point2,point3,texture,tex1,tex2,tex3):
        # Point objects
        self.point1=point1
        self.point2=point2
        self.point3=point3
        # pygame Surface
        self.texture=texture
        # tuples for location of each point on texture
        self.tex1=tex1
        self.tex2=tex2
        self.tex3=tex3
    def get_rect(self):
        sx=min(self.point1.screenx,self.point2.screenx,self.point3.screenx)
        sy=min(self.point1.screeny,self.point2.screeny,self.point3.screeny)
        dx=max(self.point1.screenx,self.point2.screenx,self.point3.screenx)-sx+1
        dy=max(self.point1.screeny,self.point2.screeny,self.point3.screeny)-sy+1
        return [int(sx),int(sy),int(dx),int(dy)]
    def __getitem__(self, key):
        if key==0:
            return self.point1,self.tex1
        if key==1:
            return self.point2,self.tex2
        if key==2:
            return self.point3,self.tex3
class Camera:
    def __init__(self,width,height,surface=None,x=0,y=0,z=0,hrot=0,vrot=3.141592653,fov=90,fill=(0,0,0)):
        self.width=width
        self.height=height
        self.x=x
        self.y=y
        self.z=z
        self.hrot=hrot
        self.vrot=vrot
        self.fov=fov
        self.film=self.height*math.tan(math.radians(fov/2))
        self.fill=fill
        if surface:
            self.surface=surface
        else:
            self.surface=pygame.Surface((width,height))
        self.zbuffer=[[INVERSEMAXDISTANCE for c in range(self.width)] for r in range(self.height)]
        self.pbuffer=[[INVERSEMAXDISTANCE for c in range(self.width)] for r in range(self.height)]
        self.texbuffer=[[[0.0,0.0] for c in range(self.width)] for r in range(self.height)]
    def drawline(self,point1,point2,tex1,tex2,texture):
        x=point1.screenx
        y=point1.screeny
        w=point2.screenx-x
        h=point2.screeny-y
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
        w=abs(w)
        longest = w
        shortest = abs(h)
        if not longest>shortest:
            longest = abs(h)
            shortest = w
            if h<0:
                dy2 = -1
            elif h > 0:
                dy2 = 1
            dx2 = 0
        numerator = longest >> 1
        currentdistance = point1.distancetocamera
        currenttex=tex1[::]
        if longest > 0:
            distancecounter=(point2.distancetocamera-point1.distancetocamera)/longest
            texcounter1=(tex2[0]-tex1[0])/longest
            texcounter2=(tex2[1]-tex1[1])/longest
        else:
            distancecounter = 0
            texcounter1=0
            texcounter2=0
        for i in range(longest+1):
            if x>=0 and x<self.width and y>=0 and y<self.height:
                self.setpoint(x,y,texture,currentdistance,currenttex)
                self.texbuffer[y][x][0]=currenttex[0]
                self.texbuffer[y][x][1]=currenttex[1]
                self.pbuffer[y][x]=currentdistance
            numerator += shortest
            if not numerator<longest:
                numerator -= longest
                x += dx1
                y += dy1
            else:
                x += dx2
                y += dy2
            currentdistance += distancecounter
            currenttex[0]+=texcounter1
            currenttex[1]+=texcounter2
    def eraseline(self,point1,point2):
        x=point1.screenx
        y=point1.screeny
        w=point2.screenx-x
        h=point2.screeny-y
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
        w=abs(w)
        longest = w
        shortest = abs(h)
        if not longest>shortest:
            longest = abs(h)
            shortest = w
            if h<0:
                dy2 = -1
            elif h > 0:
                dy2 = 1
            dx2 = 0
        numerator = longest >> 1
        for i in range(longest+1):
            if x>=0 and x<self.width and y>=0 and y<self.height:
                self.pbuffer[y][x]=INVERSEMAXDISTANCE
            numerator += shortest
            if not numerator<longest:
                numerator -= longest
                x += dx1
                y += dy1
            else:
                x += dx2
                y += dy2
    def clearbuffers(self):
        self.surface.fill(self.fill)
        for row in range(self.height):
            self.zbuffer[row][:]=[INVERSEMAXDISTANCE] * self.width
    def offsetpoint(self,x,y,z):
        x-=self.x
        y-=self.y
        z-=self.z
        directionh=math.atan2(y,x)-self.hrot
        distanceh=distanceto(y,x,0,0,0,0)
        x=math.cos(directionh)*distanceh
        y=math.sin(directionh)*distanceh
        directionv=math.atan2(y,z)-self.vrot
        distancev=distanceto(y,z,0,0,0,0)
        z=math.cos(directionv)*distancev
        y=math.sin(directionv)*distancev
        return x,y,z
    def screenpos(self,x,y,z,offseted=False):
        if not offseted:
            x,y,z=self.offsetpoint(x,y,z)
        if y>0:
            return int(x/y*self.film+self.width/2),int(z/y*self.film+self.height/2)
        else:
            return None
    def setpoint(self,x,y,texture,distance,tex):
        if self.zbuffer[y][x]<distance:
            self.zbuffer[y][x]=distance
            if mode[0]==0:
                try:
                    self.surface.set_at((x,y),texture.get_at((int(tex[0]),int(tex[1]))))
                except Exception as e:
                    self.surface.set_at((x,y),(0,255,0))
            elif mode[0]==1:
                self.surface.set_at((x,y),(tex[0]/2048*255,tex[1]/2048*255,255))
            elif mode[0]==2:
                self.surface.set_at((x,y),getcolor(1/distance*100))
    def croprect(self,rect):
        if rect[0]<0:
            rect[2]+=rect[0]
            rect[0]=0
        if rect[1]<0:
            rect[3]+=rect[1]
            rect[1]=0
        if rect[0]+rect[2]>=self.width:
            rect[2]=self.width-rect[0]
        if rect[1]+rect[3]>=self.height:
            rect[3]=self.height-rect[1]
        if rect[2]<0:
            rect[2]=0
        if rect[3]<0:
            rect[3]=0
    def drawtriangle(self,triangle):
        if triangle.point1.screenx and triangle.point2.screenx and triangle.point3.screenx:
            r=triangle.get_rect()
            if rectcollide(r,(0,0,self.width,self.height)):
                # Draw outline of triangle
                self.drawline(triangle.point1,triangle.point2,triangle.tex1,triangle.tex2,triangle.texture)
                self.drawline(triangle.point2,triangle.point3,triangle.tex2,triangle.tex3,triangle.texture)
                self.drawline(triangle.point3,triangle.point1,triangle.tex3,triangle.tex1,triangle.texture)
                self.croprect(r)
                # Fill in triangle
                for y in range(r[1],r[3]+r[1]):
                    if y>=self.height:
                        errors[0]+=1
                        continue
                    lookfor = 0
                    startx = 0
                    endx = 0
                    for x in range(r[0],r[2]+r[0]+1):
                        if x>=self.width:
                            errors[0]+=1
                            continue
                        if lookfor == 0:
                            if self.pbuffer[y][x]!=INVERSEMAXDISTANCE:
                                lookfor = 1
                                startx = x
                        elif lookfor == 1:
                            if self.pbuffer[y][x]==INVERSEMAXDISTANCE:
                                lookfor = 2
                        elif lookfor == 2:
                            if self.pbuffer[y][x]!=INVERSEMAXDISTANCE:
                                endx=x
                                lookfor = 3
                    # If there is a start and end on this row fill in
                    if lookfor == 3:
                        spreadsize = endx-startx
                        spreaddist = (self.pbuffer[y][endx]-self.pbuffer[y][startx])/spreadsize
                        spreadtex1 = (self.texbuffer[y][endx][0]-self.texbuffer[y][startx][0])/spreadsize
                        spreadtex2 = (self.texbuffer[y][endx][1]-self.texbuffer[y][startx][1])/spreadsize
                        currentdistance = self.pbuffer[y][startx]
                        currenttex=self.texbuffer[y][startx]
                        for x in range(startx,endx):
                            self.setpoint(x,y,triangle.texture,currentdistance,currenttex)
                            currentdistance += spreaddist
                            currenttex[0]+=spreadtex1
                            currenttex[1]+=spreadtex2
                # Erase outline of distances on pbuffer
                self.eraseline(triangle.point1,triangle.point2)
                self.eraseline(triangle.point2,triangle.point3)
                self.eraseline(triangle.point3,triangle.point1)
def lineattr(line,attr):
    start=line.index(" "+attr)+len(attr)+3
    r=line[start:line.index('"',start):]
    return r
def read_3mf(location):
    textures={}
    texturegroups={}
    points=[]
    triangles=[]
    currentvert=0
    a=0
    for line in open(location+"/3D/3dmodel.model","r"):
        line=line.strip()
        if line.startswith("<m:texture2d "):
            textures[lineattr(line,"id")]=pygame.image.load(location+lineattr(line,"path"))
        elif line.startswith("<m:texture2dgroup "):
            gid=lineattr(line,"id")
            texturegroups[gid]={"texid":lineattr(line,"texid")}
            texturegroups[gid]["coords"]=[]
        elif line.startswith("<m:tex2coord "):
            size=textures[texturegroups[gid]["texid"]].get_size()
            texturegroups[gid]["coords"].append([float(lineattr(line,"u"))*size[0],(1-float(lineattr(line,"v")))*size[1]])
        elif line.startswith("<vertex "):
            x=float(lineattr(line,"x"))
            z=float(lineattr(line,"y"))
            y=float(lineattr(line,"z"))
            points.append(Point(x,y,z))
        elif line.startswith("<triangle "):
            v1=int(lineattr(line,"v1"))+currentvert
            v2=int(lineattr(line,"v2"))+currentvert
            v3=int(lineattr(line,"v3"))+currentvert
            pid=lineattr(line,"pid")
            p1=int(lineattr(line,"p1"))
            p2=int(lineattr(line,"p2"))
            p3=int(lineattr(line,"p3"))
            tg=texturegroups[pid]
            texture=textures[tg["texid"]]
            tex1=tg["coords"][p1]
            tex2=tg["coords"][p2]
            tex3=tg["coords"][p3]
            triangles.append(Triangle(points[v1],points[v2],points[v3],texture,tex1,tex2,tex3))
        elif line.startswith("<object "):
            currentvert=len(points)
        a+=1
    return textures,points,triangles
def main():
    pygame.init()
    size=[800,600]
    surface=pygame.display.set_mode(size)
    c=Camera(size[0],size[1],None,-2.31,-4.96,0,2.77)
    clock=pygame.time.Clock()
    running=True
    keys=set()
    buttons=set()
    speed=64
    textures,points,triangles=read_3mf("Dog")
##    points=[Point(0,0,0),Point(0,0,1),Point(0,1,1)]
##    texture=pygame.image.load("box.png")
##    triangles=[]
##    triangles.append(Triangle(points[0],points[1],points[2],texture,[0,0],[0,0],[0,0]))
    font=pygame.font.SysFont(None,32)
    import time
    while running:
        prevtime=clock.tick(60)/1000.0
        c.clearbuffers()
        mousebefore=pygame.mouse.get_pos()
        newkeys=set()
        newbuttons=set()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            if event.type==pygame.KEYDOWN:
                keys.add(event.key)
                newkeys.add(event.key)
            if event.type==pygame.KEYUP:
                keys.discard(event.key)
            if event.type==pygame.MOUSEBUTTONDOWN:
                buttons.add(event.button)
                newbuttons.add(event.button)
            if event.type==pygame.MOUSEBUTTONUP:
                buttons.remove(event.button)
        mouseafter=pygame.mouse.get_pos()
        if pygame.K_ESCAPE in keys:
            running = False
        if 1 in buttons:
            c.hrot+=(mouseafter[0]-mousebefore[0])/500.0
            c.vrot-=(mouseafter[1]-mousebefore[1])/500.0
            c.hrot%=3.141592653*2
            c.vrot%=3.141592653*2
        if 4 in newbuttons:
            speed*=2
        if 5 in newbuttons:
            speed/=2
        if pygame.K_w in keys:
            c.x-=math.cos(c.hrot+math.radians(90))*speed*prevtime
            c.y-=math.sin(c.hrot+math.radians(90))*speed*prevtime
        if pygame.K_s in keys:
            c.x+=math.cos(c.hrot+math.radians(90))*speed*prevtime
            c.y+=math.sin(c.hrot+math.radians(90))*speed*prevtime
        if pygame.K_a in keys:
            c.x-=math.cos(c.hrot)*speed*prevtime
            c.y-=math.sin(c.hrot)*speed*prevtime
        if pygame.K_d in keys:
            c.x+=math.cos(c.hrot)*speed*prevtime
            c.y+=math.sin(c.hrot)*speed*prevtime
        if pygame.K_SPACE in keys:
            c.z+=speed*prevtime
        if pygame.K_LSHIFT in keys:
            c.z-=speed*prevtime
        if pygame.K_i in newkeys:
            mode[0]+=1
            mode[0]%=5
        for point in points:
            point.update(c)
        for triangle in triangles:
            c.drawtriangle(triangle)
        surface.blit(pygame.transform.scale(c.surface,size),(0,0))
        surface.blit(font.render(str(errors[0]),True,(255,255,255)),(0,30*0))
        a=pygame.mouse.get_pos()
        errors[0]=0
        surface.blit(font.render(" ".join([str(round(i,2)) for i in (c.x,c.y,c.z,c.hrot,c.vrot,1/prevtime,speed)]),True,(255,255,255)),(0,30*1))
        pygame.display.flip()
    pygame.quit()
main()
##import time
##t1=time.time()
##for i in range(10000000):
##    a=abs(-5)
##    a=abs(5)
##t2=time.time()
##print (t2-t1)
##t1=time.time()
##for i in range(10000000):
##    n=-5
##    if n<0:
##        n*=-1
##    n=5
##    if n<0:
##        n*=-1
##t2=time.time()
##print (t2-t1)
