import pygame
import lightstrip

SCREEN_SIZE=(1280,600)

def init():
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("LIGHTS OMG")
    return screen

def element_array((sx,sy),(dx,dy),i):
    return (sx+dx*i,sy+dy*i)

def sub_pos((x,y),(sx,sy)):
    return (x-sx,y-sy)

def add_pos((x,y),(sx,sy)):
    return (x+sx,y+sy)

def in_rect((x,y),(sx,sy,dx,dy)):
    return x>=sx and y>=sy and x<sx+dx and y<sy+dy

class Element(object):
    SIZE=(0,0)
    def __init__(self):
        self.surf=pygame.Surface(self.SIZE)

    def draw(self):
        return

    def render(self,surf,pos):
        self.draw()
        surf.blit(self.surf,pos)

    def mouse(self,relpos,event):
        return False

class Frame(Element):
    SIZE=(5,201)

    def draw(self):
        self.surf.fill((0,0,0))
        for i in range(lightstrip.STRIP_LENGTH):
            ca = self.frame[i]
            if len(ca) == 3:
                c = (ca[0]*255,ca[1]*255,ca[2]*255)
            elif len(ca) == 4:
                c = (ca[0]*ca[3]*255,ca[1]*ca[3]*255,ca[2]*ca[3]*255)
            pygame.draw.rect(self.surf,c,(1,1+i*4,3,3))

class Slider(Element):
    SIZE=(60,40)

    SLIDER_LENGTH=54
    SLIDER_THICKNESS=16

    def __init__(self,control):
        Element.__init__(self)
        self.control=control
        self.drag_start=None
        self.value_start=None

    def handle_rect(self):
        return (3+self.control.value*(self.SLIDER_LENGTH-self.SLIDER_THICKNESS),18,self.SLIDER_THICKNESS,16)

    def mouse_to_value(self,(x,y)):
        v=self.value_start+float(x)/(self.SLIDER_LENGTH-self.SLIDER_THICKNESS)
        v=min(max(v,0.),1.)
        self.control.value=v

    def draw(self):
        self.surf.fill((0,0,0))
        font = pygame.font.Font(None, 15)
        text = font.render(self.control.name, 1, (255, 255, 255))
        self.surf.blit(text,(5,2))

        pygame.draw.rect(self.surf,(20,20,20),(3,25,self.SLIDER_LENGTH,3))
        pygame.draw.rect(self.surf,(0,0,60),self.handle_rect())

    def mouse(self,relpos,event):
        if event.type==pygame.MOUSEBUTTONUP:
            self.drag_start=None
            return False
        if event.type==pygame.MOUSEBUTTONDOWN and in_rect(relpos,self.handle_rect()):
            self.drag_start=relpos
            self.value_start=self.control.value
            return True
        if self.drag_start is not None and event.type==pygame.MOUSEMOTION:
            self.mouse_to_value(sub_pos(relpos,self.drag_start))
            return True
        return False

class Pattern(Element):
    SIZE=(100,300)

    SLIDER_START=(20,20)
    SLIDER_INC=(0,50)

    ALPHA_SLIDER_POS=(10,240)

    def __init__(self,slot):
        Element.__init__(self)
        self.slot=slot
        self.uiframe=Frame()
        self.sliders=[]
        for control in slot.controls:
            self.sliders.append(Slider(control))
        self.alpha_slider=Slider(slot.alpha_control)

    def draw(self):
        self.surf.fill((20,20,20))

        self.uiframe.frame=self.slot.frame
        self.uiframe.render(self.surf,(10,30))

        for i in range(len(self.slot.controls)):
            self.sliders[i].render(self.surf,element_array(self.SLIDER_START,self.SLIDER_INC,i))

        self.alpha_slider.render(self.surf,self.ALPHA_SLIDER_POS)

    def mouse(self,relpos,event):
        for i in range(len(self.sliders)):
            corner=element_array(self.SLIDER_START,self.SLIDER_INC,i)
            if self.sliders[i].mouse(sub_pos(relpos,corner),event):
                return True
        if self.alpha_slider.mouse(sub_pos(relpos,self.ALPHA_SLIDER_POS),event):
            return True
        return False

class UI(Element):
    SIZE=SCREEN_SIZE

    SLOT_START=(100,100)
    SLOT_INC=(110,0)

    def __init__(self,screen,slots):
        self.surf=screen
        self.slots=slots
        self.master=Frame()
        self.drag_start=None

    def draw(self):
        self.master.render(self.surf,(30,100))
        for i in range(len(self.slots)):
            if self.slots[i] is not None and (self.drag_start is None or i != self.drag_pat):
                self.slots[i].render(self.surf,element_array(self.SLOT_START,self.SLOT_INC,i))

        if self.drag_start is not None:
                self.slots[self.drag_pat].render(self.surf,add_pos(element_array(self.SLOT_START,self.SLOT_INC,self.drag_pat),self.drag_pos))

    def render(self):
        self.surf.fill((0,0,0))
        self.draw()
        pygame.display.update()

    def pat_move(self,fr,to):
        temp=self.slots[to]
        self.slots[to]=self.slots[fr]
        self.slots[fr]=temp

    def handle_drag(self,(x,y)):
        if x < -self.SLOT_INC[0]/2 and self.drag_pat > 0:
            self.pat_move(self.drag_pat,self.drag_pat-1)
            self.drag_pat -= 1
            self.drag_start = sub_pos(self.drag_start,self.SLOT_INC)
            self.drag_pos = add_pos((x,y),self.SLOT_INC)
            return
        if x > self.SLOT_INC[0]/2 and self.drag_pat < len(self.slots)-1:
            self.pat_move(self.drag_pat,self.drag_pat+1)
            self.drag_pat += 1
            self.drag_start = add_pos(self.drag_start,self.SLOT_INC)
            self.drag_pos = sub_pos((x,y),self.SLOT_INC)
            return
        self.drag_pos=(x,y)

    def mouse(self,relpos,event):
        if self.drag_start is not None and event.type==pygame.MOUSEMOTION:
            self.handle_drag(sub_pos(relpos,self.drag_start))
            return True
        if self.drag_start is not None and event.type==pygame.MOUSEBUTTONUP:
            self.drag_start=None

        for i in range(len(self.slots)):
            corner=element_array(self.SLOT_START,self.SLOT_INC,i)
            if self.slots[i] is not None:
                if self.slots[i].ui.mouse(sub_pos(relpos,corner),event):
                    return True

        if event.type==pygame.MOUSEBUTTONDOWN:
            for i in range(len(self.slots)):
                corner=element_array(self.SLOT_START,self.SLOT_INC,i)
                if self.slots[i] is not None and in_rect(relpos,corner+Pattern.SIZE):
                    self.drag_start=relpos
                    self.drag_pos=(0,0)
                    self.drag_pat=i
                    return True
        return False

