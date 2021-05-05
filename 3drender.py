import pygame
import math
import time
def rectcollide(rect1,rect2):
    if rect1[0]<rect2[0]+rect2[2] and rect2[0]<rect1[0]+rect1[2]:
        if rect1[1]<rect2[1]+rect2[3] and rect2[1]<rect1[1]+rect1[3]:
            return True
    return False
def distanceto(x1,y1,z1,x2,y2,z2):
    return math.sqrt((x1-x2)*2+(y1-y2)**2+(z1-z2)**2)
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
def tupletocolor(t):
    return t[0]*65536+t[1]*256+t[2]
class Texture:
    def __init__(self,surface):
        self.width,self.height=surface.get_size()
        self.tex=[[tupletocolor(surface.get_at((c,r))) for c in range(self.width)] for r in range(self.height)]
    def get_size(self):
        return self.width,self.height
class Point:
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
        self.distancetocamera=0.0
        self.screenx=0
        self.screeny=0
    def update(self,camera):
        offsetedpoint=camera.offsetpoint(self.x,self.y,self.z)
        if offsetedpoint[1]>0:
            self.distancetocamera=1/abs(offsetedpoint[1])
            self.screenx,self.screeny=camera.screenpos(offsetedpoint[0],offsetedpoint[1],offsetedpoint[2],True)
        else:
            self.distancetocamera=0.0
            self.screenx=0
            self.screeny=0
class Triangle:
    def __init__(self,point1,point2,point3,texture,tex1,tex2,tex3):
        # Point objects
        self.point1=point1
        self.point2=point2
        self.point3=point3
        # pygame Surface
        self.texture=texture
        # tuples for location of each point on texture
        self.U1=tex1[0]
        self.V1=tex1[1]
        self.U2=tex2[0]
        self.V2=tex2[1]
        self.U3=tex3[0]
        self.V3=tex3[1]
    def get_rect(self):
        sx=self.point1.screenx
        if self.point2.screenx<sx:
            sx=self.point2.screenx
        if self.point3.screenx<sx:
            sx=self.point3.screenx

        sy=self.point1.screeny
        if self.point2.screeny<sy:
            sy=self.point2.screeny
        if self.point3.screeny<sy:
            sy=self.point3.screeny

        dx=self.point1.screenx
        if self.point2.screenx>dx:
            dx=self.point2.screenx
        if self.point3.screenx>dx:
            dx=self.point3.screenx
        dx-=sx-1

        dy=self.point1.screeny
        if self.point2.screeny>dy:
            dy=self.point2.screeny
        if self.point3.screeny>dy:
            dy=self.point3.screeny
        dy-=sy-1
        return (sx,sy,dx,dy)
class Camera:
    def __init__(self,width,height,x=0,y=0,z=0,hrot=0,vrot=3.141592653,fov=90):
        self.width=width
        self.height=height
        self.x=x
        self.y=y
        self.z=z
        self.hrot=hrot
        self.vrot=vrot
        self.fov=fov
        self.rect=(0,0,self.width,self.height)
        self.film=self.height*math.tan(math.radians(fov/2))
##        if surface:
##            self.surface=surface
##        else:
##            self.surface=pygame.Surface((width,height))
        self.buffer=tuple([tuple([[0.0,0.0,0.0,0.0,0] for c in range(self.width)]) for r in range(self.height)])
        # 0-zbufferdistance,1-pbufferdistance,2-texbuffer.u,3-texbuffer.v,4-colorbuffer.r,5-colorbuffer.g,6-colorbuffer.b
##        self.zbuffer=[[INVERSEMAXDISTANCE for c in range(self.width)] for r in range(self.height)]
##        self.pbuffer=[[INVERSEMAXDISTANCE for c in range(self.width)] for r in range(self.height)]
##        self.texbuffer=[[[0.0,0.0] for c in range(self.width)] for r in range(self.height)]
    def cropline(self,width,height,x1,y1,d1,x2,y2,d2,U1,V1,U2,V2):
        if x2>width:
            ratio = (width-x1)/(x2-x1)
            x2=width
            y2=int(y1+(y2-y1)*ratio)
            d2=d1+(d2-d1)*ratio
            U2=U1+(U2-U1)*ratio
            V2=V1+(V2-V1)*ratio
        elif x2<0:
            ratio = (0-x1)/(x2-x1)
            x2=0
            y2=int(y1+(y2-y1)*ratio)
            d2=d1+(d2-d1)*ratio
            U2=U1+(U2-U1)*ratio
            V2=V1+(V2-V1)*ratio
        if y2>height:
            ratio = (height-y1)/(y2-y1)
            y2=height
            x2=int(x1+(x2-x1)*ratio)
            d2=d1+(d2-d1)*ratio
            U2=U1+(U2-U1)*ratio
            V2=V1+(V2-V1)*ratio
        elif y2<0:
            ratio = (0-y1)/(y2-y1)
            y2=0
            x2=int(x1+(x2-x1)*ratio)
            d2=d1+(d2-d1)*ratio
            U2=U1+(U2-U1)*ratio
            V2=V1+(V2-V1)*ratio
        if x1>width:
            ratio = (width-x2)/(x1-x2)
            x1=width
            y1=int(y2+(y1-y2)*ratio)
            d1=d2+(d1-d2)*ratio
            U1=U2+(U1-U2)*ratio
            V1=V2+(V1-V2)*ratio
        elif x1<0:
            ratio = (0-x2)/(x1-x2)
            x1=0
            y1=int(y2+(y1-y2)*ratio)
            d1=d2+(d1-d2)*ratio
            U1=U2+(U1-U2)*ratio
            V1=V2+(V1-V2)*ratio
        if y1>height:
            ratio = (height-y2)/(y1-y2)
            y1=height
            x1=int(x2+(x1-x2)*ratio)
            d1=d2+(d1-d2)*ratio
            U1=U2+(U1-U2)*ratio
            V1=V2+(V1-V2)*ratio
        elif y1<0:
            ratio = (0-y2)/(y1-y2)
            y1=0
            x1=int(x2+(x1-x2)*ratio)
            d1=d2+(d1-d2)*ratio
            U1=U2+(U1-U2)*ratio
            V1=V2+(V1-V2)*ratio
        return x1,y1,d1,x2,y2,d2,U1,V1,U2,V2
    def drawoutline(self,x1,y1,d1,x2,y2,d2,x3,y3,d3,U1,V1,U2,V2,U3,V3,texture):
        width=self.width-1
        height=self.height-1
        nx1,ny1,nd1,nx2,ny2,nd2,nU1,nV1,nU2,nV2=self.cropline(width,height,x1,y1,d1,x2,y2,d2,U1,V1,U2,V2)
        
        
    def drawline(self,width,height,x1,y1,d1,x2,y2,d2,U1,V1,U2,V2,texture):
        if x1>width and x2>width:
            return
        if y1>height and y2>height:
            return
        if x1<0 and x2<0:
            return
        if y1<0 and y2<0:
            return
        x=x1
        y=y1
        w=x2-x
        h=y2-y
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
            longest = shortest
            shortest = abs(w)
            if h<0:
                dy2 = -1
            elif h > 0:
                dy2 = 1
            dx2 = 0
        numerator = longest // 2
        currentdistance = d1
        currentu=U1
        currentv=V1
        spreaddistance = 0.0
        spreadu=0.0
        spreadv=0.0
        if longest != 0:
            spreaddistance=(d2-d1)/longest
            spreadu=(U2-U1)/longest
            spreadv=(V2-V1)/longest
        for i in range(longest+1):
            try:
                location=self.buffer[y][x]
                if location[0]<currentdistance:
                    location[0]=currentdistance
                    try:
                        location[4]=texture.tex[int(round(currentv))][int(round(currentu))]
                    except Exception as e:
                        location[4]=65280
                location[1]=currentdistance
                location[2]=currentu
                location[3]=currentv
            except:
                pass#print(x,y)
            numerator += shortest
            if not numerator<longest:
                numerator -= longest
                x += dx1
                y += dy1
            else:
                x += dx2
                y += dy2
            currentdistance += spreaddistance
            currentu+=spreadu
            currentv+=spreadv
    def eraseline(self,x1,y1,x2,y2):
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
            longest = shortest
            shortest = abs(w)
            if h<0:
                dy2 = -1
            elif h > 0:
                dy2 = 1
            dx2 = 0
        numerator = longest >> 1
        for i in range(longest+1):
            if x1>=0 and x1<self.width and y1>=0 and y1<self.height:
                self.buffer[y1][x1][1]=0.0
            numerator += shortest
            if not numerator<longest:
                numerator -= longest
                x1 += dx1
                y1 += dy1
            else:
                x1 += dx2
                y1 += dy2
    def swapbuffers(self,surface):
        r=0
        for row in self.buffer:
            c=0
            for col in row:
                if col[0]!=0.0:
                    col[0]=0.0
                    surface.set_at((c,r),col[4])
                c+=1
            r+=1
    def offsetpoint(self,x,y,z):
        x-=self.x
        y-=self.y
        z-=self.z
        directionh=math.atan2(y,x)-self.hrot
        distanceh=math.sqrt(y**2+x**2)
        x=math.cos(directionh)*distanceh
        y=math.sin(directionh)*distanceh
        directionv=math.atan2(y,z)-self.vrot
        distancev=math.sqrt(y**2+z**2)
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
##    def setpoint(self,x,y,texture,distance,tex):
##        if self.zbuffer[y][x]<distance:
##            self.zbuffer[y][x]=distance
##            if mode[0]==0:
##                try:
##                    self.surface.set_at((x,y),texture.get_at((int(tex[0]),int(tex[1]))))
##                except Exception as e:
##                    self.surface.set_at((x,y),(0,255,0))
##            elif mode[0]==1:
##                self.surface.set_at((x,y),(tex[0]/2048*255,tex[1]/2048*255,255))
##            elif mode[0]==2:
##                self.surface.set_at((x,y),getcolor(1/distance*100))
    def croprect(self,rect):
        sx,sy,dx,dy=rect
        if sx<0:
            dx+=sx
            sx=0
        if sy<0:
            dy+=sy
            sy=0
        if sx+dx>=self.width:
            dx=self.width-sx
        if sy+dy>=self.height:
            dy=self.height-sy
        if dx<0:
            dx=0
        if dy<0:
            dy=0
        return (sx,sy,dx,dy)
    def drawtriangle(self,triangle):
        point1=triangle.point1
        point2=triangle.point2
        point3=triangle.point3
        d1=point1.distancetocamera
        d2=point2.distancetocamera
        d3=point3.distancetocamera
        if d1 and d2 and d3:
            r=triangle.get_rect()
            texture=triangle.texture
            x1=point1.screenx
            y1=point1.screeny
            U1=triangle.U1
            V1=triangle.V1
            x2=point2.screenx
            y2=point2.screeny
            U2=triangle.U2
            V2=triangle.V2
            x3=point3.screenx
            y3=point3.screeny
            U3=triangle.U3
            V3=triangle.V3
            width=self.width
            height=self.height
            if rectcollide(r,self.rect):
                # Draw outline of triangle # these lines are slow 0.6
                self.drawline(width,height,x1,y1,d1,x2,y2,d2,U1,V1,U2,V2,texture)
                self.drawline(width,height,x2,y2,d2,x3,y3,d3,U2,V2,U3,V3,texture)
                self.drawline(width,height,x3,y3,d3,x1,y1,d1,U3,V3,U1,V1,texture)
                r=self.croprect(r)
                # Fill in triangle
                startx = 0
                endx = 0
                # fill slow 1.1
                xgen=range(r[0],r[2]+r[0])
                for y in range(r[1],r[3]+r[1]):
                    lookfor = 0
                    row = self.buffer[y]
                    for x in xgen:
                        if lookfor == 0:
                            if row[x][1]!=0.0:
                                lookfor = 1
                                startx = x
                        elif lookfor == 1:
                            if row[x][1]==0.0:
                                lookfor = 2
                        elif lookfor == 2:
                            if row[x][1]!=0.0:
                                endx=x
                                lookfor = 3
                    # If there is a start and end on this row fill in
                    if lookfor == 3:
                        start=row[startx]
                        end=row[endx]
                        spreadsize = float(endx-startx)
                        currentdistance = start[1]
                        currentu=start[2]
                        currentv=start[3]
                        spreaddist = (end[1]-currentdistance)/spreadsize
                        spreadu = (end[2]-currentu)/spreadsize
                        spreadv = (end[3]-currentv)/spreadsize
                        for x in range(startx,endx):
                            current=row[x]
                            # this if is slow
                            if current[0]<currentdistance:
                                current[0]=currentdistance # .001
                                try:
                                    current[4]=texture.tex[int(round(currentv))][int(round(currentu))]
                                except Exception as e:
                                    current[4]=65280
##                            self.setpoint(x,y,triangle.texture,currentdistance,currenttex)
                            currentdistance += spreaddist
                            currentu+=spreadu
                            currentv+=spreadv
                # Erase outline of distances on pbuffer # .18
                self.eraseline(x1,y1,x2,y2)
                self.eraseline(x2,y2,x3,y3)
                self.eraseline(x3,y3,x1,y1)
def lineattr(line,attr):
    start=line.index(" "+attr+"=")+len(attr)+3
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
            textures[lineattr(line,"id")]=Texture(pygame.image.load(location+lineattr(line,"path")))
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
    c=Camera(size[0],size[1],-2.31,-4.96,0,2.77)
    clock=pygame.time.Clock()
    running=True
    keys=set()
    buttons=set()
    speed=64
    textures,points,triangles=read_3mf("Dog")
    #points=[Point(0,0,0),Point(0,0,1),Point(0,1,1)]
    #texture=Texture(pygame.image.load("box.png"))
    #triangles=[]
    #triangles.append(Triangle(points[0],points[1],points[2],texture,[0,0],[0,1],[1,0]))
    font=pygame.font.SysFont(None,32)
    last=0
    while running:
        current=time.perf_counter()
        prevtime=current-last
        last=current
        surface.fill((0,0,0))
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
        for point in points:
            point.update(c)
        for triangle in triangles:
            c.drawtriangle(triangle)
        c.swapbuffers(surface)
        surface.blit(font.render(" ".join([str(round(i,5)) for i in (c.x,c.y,c.z,c.hrot,c.vrot,prevtime,speed)]),True,(255,255,255)),(0,30*1))
        pygame.display.flip()
    pygame.quit()
main()
##class Test:
##    def __init__(self,a,b,c,d,e,f):
##        self.a=a
##        self.b=b
##        self.c=c
##        self.d=d
##        self.e=e
##        self.f=f
##t=Test(0,0,0,0,0,0)
##q=[0,0,0,0,0,0]
##g=0
##import timeit
##t=(0,0,0,0,255,0,0)
##t2=(0,0,0,0,16711680)
##print(timeit.timeit('t[4:7]',setup="from __main__ import t",number=10000000))
##print(timeit.timeit('t2[4]',setup="from __main__ import t2",number=10000000))
##print(timeit.timeit("t.c",setup="from __main__ import t",number=20000000))
##print(timeit.timeit("q[2]",setup="from __main__ import q",number=20000000))
##print(timeit.timeit("g",setup="from __main__ import g",number=20000000))
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
