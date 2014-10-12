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

class BankPattern(Element):
    SIZE=(130,30)

    def __init__(self,bp):
        Element.__init__(self)
        self.bp=bp
        self.surf.fill((20,20,20))
        font = pygame.font.Font(None, 25)
        text = font.render(self.bp.pat.name, 1, (255, 255, 255))
        self.surf.blit(text,(5,2))

class Slider(Element):
    SIZE=(60,40)

    SLIDER_LENGTH=54
    SLIDER_THICKNESS=10

    KNOB_POS=(5,15)
    KNOB_SIZE=(50,15)

    def __init__(self,control,knobs=[None]):
        Element.__init__(self)
        self.control=control
        self.slot_drag_start=None
        self.value_start=None
        self.knobs=knobs
        self.knob_index=0

        self.font = pygame.font.Font(None, 15)
        self.text = self.font.render(self.control.name, 1, (255, 255, 255))

        self.update_knob()

    def update_knob(self):
        if self.knob_index >= len(self.knobs):
            self.knob_index = 0

        self.control.set_knob(self.knobs[self.knob_index])
        if self.control.knob is not None:
            self.knob_name=self.font.render(self.control.knob.name,1,(255,255,255))

    def handle_rect(self):
        return (3+self.control.value*(self.SLIDER_LENGTH-self.SLIDER_THICKNESS),28,self.SLIDER_THICKNESS,10)

    def mouse_to_value(self,(x,y)):
        v=self.value_start+float(x)/(self.SLIDER_LENGTH-self.SLIDER_THICKNESS)
        v=min(max(v,0.),1.)
        self.control.value=v

    def draw(self):
        self.surf.fill((0,0,0))
        self.surf.blit(self.text,(5,2))

        knob=self.knobs[self.knob_index]
        if knob is not None:
            self.surf.blit(self.knob_name,self.KNOB_POS)

        pygame.draw.rect(self.surf,(20,20,20),(3,32,self.SLIDER_LENGTH,3))
        pygame.draw.rect(self.surf,(0,0,60),self.handle_rect())

    def mouse(self,relpos,event):
        if event.type==pygame.MOUSEBUTTONUP:
            self.slot_drag_start=None
            return False
        if event.type==pygame.MOUSEBUTTONDOWN:
            if in_rect(relpos,self.KNOB_POS+self.KNOB_SIZE):
                self.knob_index+=1
                if self.knob_index>=len(self.knobs):
                    self.knob_index=0
                self.update_knob()
            if in_rect(relpos,self.handle_rect()):
                self.slot_drag_start=relpos
                self.value_start=self.control.value
                return True
        if self.slot_drag_start is not None and event.type==pygame.MOUSEMOTION:
            self.mouse_to_value(sub_pos(relpos,self.slot_drag_start))
            return True
        return False

class Pattern(Element):
    SIZE=(100,300)

    SLIDER_START=(20,30)
    SLIDER_INC=(0,50)

    ALPHA_SLIDER_POS=(10,240)

    EJECT=(85,10)
    EJECT_SIZE=(10,10)

    def __init__(self,slot):
        Element.__init__(self)
        self.slot=slot
        self.uiframe=Frame()
        self.sliders=[]

        for control in slot.controls:
            self.sliders.append(Slider(control))
        self.alpha_slider=Slider(slot.alpha_control)

        font = pygame.font.Font(None, 15)
        self.text = font.render(self.slot.pat.name, 1, (255, 255, 255))

    def draw(self):
        self.surf.fill((20,20,20))

        self.surf.blit(self.text,(5,5))

        self.uiframe.frame=self.slot.frame
        self.uiframe.render(self.surf,(10,30))

        for i in range(len(self.slot.controls)):
            self.sliders[i].render(self.surf,element_array(self.SLIDER_START,self.SLIDER_INC,i))

        self.alpha_slider.render(self.surf,self.ALPHA_SLIDER_POS)

        pygame.draw.line(self.surf,(255,255,255),(self.EJECT[0],self.EJECT[1]),(self.EJECT[0]+self.EJECT_SIZE[0],self.EJECT[1]+self.EJECT_SIZE[1]))
        pygame.draw.line(self.surf,(255,255,255),(self.EJECT[0]+self.EJECT_SIZE[0],self.EJECT[1]),(self.EJECT[0],self.EJECT[1]+self.EJECT_SIZE[1]))

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

    BANK_START=(100,420)
    BANK_INC=(150,0)

    def __init__(self,screen,bank,slots,knobs):
        self.surf=screen
        self.slots=slots
        self.bank=bank
        self.master=Frame()
        self.slot_drag_start=None
        self.bank_drag_start=None
        self.knobs=knobs

    def draw(self):
        self.master.render(self.surf,(30,100))
        for i in range(len(self.slots)):
            if self.slots[i] is not None and (self.slot_drag_start is None or i != self.drag_index):
                self.slots[i].render(self.surf,element_array(self.SLOT_START,self.SLOT_INC,i))
            else:
                pygame.draw.rect(self.surf,(20,20,20),element_array(self.SLOT_START,self.SLOT_INC,i)+Pattern.SIZE,1)

        for i in range(len(self.bank)):
            self.bank[i].render(self.surf,element_array(self.BANK_START,self.BANK_INC,i))

        if self.slot_drag_start is not None:
                self.slots[self.drag_index].render(self.surf,add_pos(element_array(self.SLOT_START,self.SLOT_INC,self.drag_index),self.drag_pos))

        elif self.bank_drag_start is not None:
                self.bank[self.drag_index].render(self.surf,add_pos(element_array(self.BANK_START,self.BANK_INC,self.drag_index),self.drag_pos))

    def update_knobs(self,slot):
        if self.slots[slot] is not None:
            knobs=self.knobs(slot)
            for slider in self.slots[slot].ui.sliders:
                slider.knobs=knobs
                slider.update_knob()

    def render(self):
        self.surf.fill((0,0,0))
        self.draw()
        pygame.display.update()

    def slot_move(self,fr,to):
        temp=self.slots[to]
        self.slots[to]=self.slots[fr]
        self.slots[fr]=temp
        self.update_knobs(fr)
        self.update_knobs(to)

    def handle_slot_drag(self,(x,y)):
        if x < -self.SLOT_INC[0]/2 and self.drag_index > 0:
            self.slot_move(self.drag_index,self.drag_index-1)
            self.drag_index -= 1
            self.slot_drag_start = sub_pos(self.slot_drag_start,self.SLOT_INC)
            self.drag_pos = add_pos((x,y),self.SLOT_INC)
            return
        if x > self.SLOT_INC[0]/2 and self.drag_index < len(self.slots)-1:
            self.slot_move(self.drag_index,self.drag_index+1)
            self.drag_index += 1
            self.slot_drag_start = add_pos(self.slot_drag_start,self.SLOT_INC)
            self.drag_pos = sub_pos((x,y),self.SLOT_INC)
            return
        self.drag_pos=(x,y)

    def handle_bank_drop(self,(x,y)):
        for i in range(len(self.slots)):
            corner=element_array(self.SLOT_START,self.SLOT_INC,i)
            if in_rect((x,y),corner+Pattern.SIZE):
                self.slots[i]=self.bank[self.drag_index].make()
                self.update_knobs(i)
                break

    def mouse(self,relpos,event):
        if event.type==pygame.MOUSEMOTION:
            # slot move
            if self.slot_drag_start is not None:
                self.handle_slot_drag(sub_pos(relpos,self.slot_drag_start))
                return True

            # bank move
            if self.bank_drag_start is not None:
                self.drag_pos=sub_pos(relpos,self.bank_drag_start)
                return True

        if event.type==pygame.MOUSEBUTTONUP:
            # slot drop
            if self.slot_drag_start is not None:
                self.slot_drag_start=None

            # bank drop
            if self.bank_drag_start is not None:
                self.handle_bank_drop(relpos)
                self.bank_drag_start=None

        # child
        for i in range(len(self.slots)):
            corner=element_array(self.SLOT_START,self.SLOT_INC,i)
            if self.slots[i] is not None:
                if self.slots[i].ui.mouse(sub_pos(relpos,corner),event):
                    return True

        if event.type==pygame.MOUSEBUTTONDOWN:
            # eject
            for i in range(len(self.slots)):
                corner=element_array(self.SLOT_START,self.SLOT_INC,i)
                corner=add_pos(corner,Pattern.EJECT)
                if self.slots[i] is not None and in_rect(relpos,corner+Pattern.EJECT_SIZE):
                    for slider in self.slots[i].ui.sliders:
                        slider.control.set_knob(None)
                    self.slots[i]=None
                    return True

            # slot drag
            for i in range(len(self.slots)):
                corner=element_array(self.SLOT_START,self.SLOT_INC,i)
                if self.slots[i] is not None and in_rect(relpos,corner+Pattern.SIZE):
                    self.slot_drag_start=relpos
                    self.drag_pos=(0,0)
                    self.drag_index=i
                    return True

            # bank drag
            for i in range(len(self.bank)):
                corner=element_array(self.BANK_START,self.BANK_INC,i)
                if in_rect(relpos,corner+BankPattern.SIZE):
                    self.bank_drag_start=relpos
                    self.drag_pos=(0,0)
                    self.drag_index=i
                    return True

        return False
