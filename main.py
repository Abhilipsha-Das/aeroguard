import pygame
import math
import random
from algorithms import a_star 

# --- Configuration ---
WIDTH, RADAR_WIDTH, HEIGHT = 1200, 900, 700
BLACK, GREEN, RED, DARK_GREEN, WHITE, YELLOW, GRAY = (0,0,0), (0,255,0), (255,0,0), (0,40,0), (255,255,255), (255,255,0), (100,100,100)
BG_BLUE = (10, 20, 30)

# coordinates of Airport for landing
AIRPORT_POS = (RADAR_WIDTH // 2, (HEIGHT // 2) + 80) 


#tells properties of plane
class Plane:
    def __init__(self, callsign, x, y, alt, fuel):
        self.callsign = callsign
        self.x, self.y = x, y
        self.target = AIRPORT_POS
        self.alt = alt
        self.fuel = fuel 
        self.path = []
        self.speed = 1.5
        self.state = "EN-ROUTE" 
        self.angle = random.uniform(0, 6.28)
        self.conflict = False

    def update_path(self, storms):
        if self.state != "EN-ROUTE": return
        obstacles = [(sx, sy, sr) for sx, sy, sr in storms]
        #if obstacles come calls a star algo to find new path
        new_path = a_star((self.x, self.y), self.target, obstacles, RADAR_WIDTH, HEIGHT)
        if new_path: self.path = new_path

    def move(self, airport_open):
        if self.state == "ARRIVED": return#plane lands if airport is open

        # send plane to holding pattern if Airport is  Closed 
        if not airport_open and self.state == "LANDING":
            self.state = "HOLDING"

        # Holding Pattern Trigger
        if self.state == "EN-ROUTE" and math.dist((self.x, self.y), self.target) < 70:#when plane is about 70 units near aiport it holds
            self.state = "HOLDING"

        if self.state == "HOLDING":
            self.angle += 0.04
            self.x = AIRPORT_POS[0] + math.cos(self.angle) * 80#uses sin and cos to rotate
            self.y = AIRPORT_POS[1] + math.sin(self.angle) * 60
            self.fuel -= 0.04 

        elif self.state == "LANDING":
            dist = math.dist((self.x, self.y), self.target)
            if dist > 3:
                self.x += (self.target[0] - self.x) / dist * 2
                self.y += (self.target[1] - self.y) / dist * 2
            else:
                self.state = "ARRIVED"

        elif self.state == "EN-ROUTE" and self.path:
            next_pt = self.path[0]
            dist = math.dist((self.x, self.y), next_pt)
            if dist > 1:
                self.x += (next_pt[0] - self.x) / dist * self.speed
                self.y += (next_pt[1] - self.y) / dist * self.speed
            else:
                self.path.pop(0)

    def draw(self, screen):
        if self.state == "ARRIVED": return
        color = YELLOW if self.state == "HOLDING" else (RED if self.conflict else GREEN)
        pygame.draw.polygon(screen, color, [(self.x, self.y-8), (self.x-6, self.y+6), (self.x+6, self.y+6)])
        
        font = pygame.font.SysFont("Courier", 12, bold=True)
        screen.blit(font.render(f"{self.callsign} FL{self.alt}", True, color), (self.x + 12, self.y - 12))
        screen.blit(font.render(f"FUEL:{int(self.fuel)}kg", True, color), (self.x + 12, self.y + 2))

def check_logic(planes, logs, airport_open):
    for i, p1 in enumerate(planes):
        if p1.state == "ARRIVED": continue
        p1.conflict = False
        for j, p2 in enumerate(planes):
            if i < j and p2.state != "ARRIVED":
                dist = math.dist((p1.x, p1.y), (p2.x, p2.y))# closest pair-calc distance between 2 coords
                if dist < 100 and p1.alt == p2.alt:#if dist<100 units and planes are at same altitude 
                    p1.alt += 20 #change altitude
                    logs.append(f"TCAS: {p1.callsign} CLIMB TO FL{p1.alt}")#command is given
                if dist < 60 and p1.alt == p2.alt:
                    p1.conflict = True

    if airport_open:#when gate opens and planes were in holding
        holding = [p for p in planes if p.state == "HOLDING"]
        if holding:
            holding.sort(key=lambda p: p.fuel)#greedy-sorts planes from lowest to highest fuel
            next_p = holding[0]#stores least fuel plane
            next_p.state = "LANDING"#plane with least fuel gets permission to land
            logs.append(f"GREEDY: {next_p.callsign} LANDING ({int(next_p.fuel)}kg)") #landing command in order of less to high fuel

def draw_sidebar(screen, planes, logs, airport_open):#shows log of atc in sidebar
    pygame.draw.rect(screen, (15, 15, 25), (RADAR_WIDTH, 0, 300, HEIGHT))
    pygame.draw.line(screen, GREEN, (RADAR_WIDTH, 0), (RADAR_WIDTH, HEIGHT), 2)
    
    font_header = pygame.font.SysFont("Courier", 18, bold=True)
    font_text = pygame.font.SysFont("Courier", 14)
    
    # 1. Airport Status
    status_color = GREEN if airport_open else RED
    status_txt = "OPEN" if airport_open else "CLOSED"
    screen.blit(font_header.render(f"AIRPORT: {status_txt}", True, status_color), (RADAR_WIDTH + 20, 20))
    screen.blit(font_text.render("O: OPEN | C: CLOSE", True, WHITE), (RADAR_WIDTH + 20, 45))
    
    # 2. Fuel Status
    screen.blit(font_header.render("--- FUEL STATUS ---", True, WHITE), (RADAR_WIDTH + 20, 100))
    y_off = 130
    for p in planes:
        p_color = YELLOW if p.state == "HOLDING" else GREEN
        if p.state == "ARRIVED": p_color = GRAY
        txt = font_text.render(f"{p.callsign}: {int(p.fuel)}kg ({p.state})", True, p_color)
        screen.blit(txt, (RADAR_WIDTH + 20, y_off))
        y_off += 25

    # 3. Log Box
    screen.blit(font_header.render("ATC COMMAND LOG", True, WHITE), (RADAR_WIDTH + 20, 320))
    pygame.draw.rect(screen, BLACK, (RADAR_WIDTH + 10, 350, 280, 330))
    log_y = 360
    for entry in logs[-14:]:
        log_txt = font_text.render(f"> {entry}", True, GREEN)
        screen.blit(log_txt, (RADAR_WIDTH + 15, log_y))
        log_y += 22

def run():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AeroGuard: Emergency Toggle System")
    clock = pygame.time.Clock()

    planes = [
        Plane("6E123", 100, 100, 320, 250),
        Plane("AI456", 800, 100, 320, 130),
        Plane("UK789", 450, 50, 340, 400)
    ]
    storms = []
    logs = ["System Online", "Airport CLOSED"]
    airport_open = False

    while True:
        screen.fill(BG_BLUE)
        
        # Radar circles center change
        for r in range(100, 800, 100):
            pygame.draw.circle(screen, DARK_GREEN, AIRPORT_POS, r, 1)
        pygame.draw.rect(screen, WHITE, (AIRPORT_POS[0]-10, AIRPORT_POS[1]-10, 20, 20), 2)

        for event in pygame.event.get():#checks if user pressed any key or moved mouse
            if event.type == pygame.QUIT: return#if x is pressed system quits
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_o:#if o is pressed then airport open becoms true and gate opens .planes can land
                    airport_open = True
                    logs.append("ATC: Opening Runway 09L")
                if event.key == pygame.K_c:#if c is pressed then airport open becoms false and gate opens .planes cannot land
                    airport_open = False
                    logs.append("ATC: CLOSING RUNWAY - HOLD!")
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()#takes location of click
                if mx < RADAR_WIDTH:
                    storms.append((mx, my, 65))#adds a storm
                    for p in planes: p.update_path(storms)#every plane calls a star algorithm to update its path

        check_logic(planes, logs, airport_open)
        for sx, sy, sr in storms: pygame.draw.circle(screen, (60, 0, 0), (sx, sy), sr)#draws storms like dark red circles

        for p in planes:#moves every plane to its new position and shows it on screen
            p.move(airport_open)
            p.draw(screen)

        draw_sidebar(screen, planes, logs, airport_open)
        pygame.display.flip()#updates drawings and shows on screen
        clock.tick(30) #loop runs 30 tyms in 1 second(so that the animation doesnt run too fast on screen)

if __name__ == "__main__":
    run()