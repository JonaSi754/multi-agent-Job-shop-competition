import pygame
import math

from utils.read import read_JSP

screen_width = 1500
screen_height = 1200
jobs = read_JSP()

class Workpiece:
    def __init__(self, job_img, pos, job):
        self.surface = pygame.image.load(job_img)
        self.surface = pygame.transform.scale(self.surface, (16, 16))
        self.stakes = 20  # total stakes
        self.bets = 0     # stake given each turn
        self.pos = pos
        self.center = [self.pos[0] + 8, self.pos[1] + 8]
        self.done = False
        self.No = job.No
        self.cur = 0
        self.startTime = []
        self.endTime = []
        self.process_time = job.process_time
        self.machine_arrange = job.machine_arrange
        self.condition = 0  # condition flag for wait or processing
        self.wait_time = 0
        self.speed = 100 / self.process_time[self.cur]
        
    def draw(self, screen):
        screen.blit(self.surface, self.pos)
        
    def update(self):
        if self.condition == 1:
            self.pos[1] += self.speed
            
    def place_bets(self, action):
        self.bets = min(action, self.stakes)
        self.stakes -= self.bets
        return self.bets
    
    def collect_bets(self):
        self.stakes += self.bets
        self.bets = 0
        
        

class Machine:
    def __init__(self, machine_img, pos, joblist):
        self.surface = pygame.image.load(machine_img)
        self.surface = pygame.transform.scale(self.surface, (20, 20))
        self.pos = pos
        self.job_list = joblist
        self.possessed_time = 0
        
        
class PyGame2D:
    """Construct a game for JSP
    
    Jobs and machines are initialized and painted on the map,
    This game is written under the guide of monokim
    https://github.com/monokim/framework_tutorial
    https://www.youtube.com/watch?v=ZxXKISVkH6Y
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 30)
        self.jobs = []
        self.machines = []
        self.num_machines = len(jobs[0].machine_arrange)
        self.game_speed = 10
        self.mode = 0
        
        _side_len = 20
        _init_pos_job = [_side_len * 10, _side_len]
        _init_pos_machine = [_side_len * 5, _side_len]
        _gap_job = (screen_height - _side_len * 6) // self.num_machines
        _gap_machine = (screen_height - _side_len * 11) // len(jobs)
        for job in jobs:
            self.jobs.append(Workpiece('images\job_img.png', _init_pos_job, job))
            _init_pos_job[0] += _gap_job
        for i in range(self.num_machines):
            self.machiens.append(Machine('images\machine_img.png', _init_pos_machine, job))
            _init_pos_machine[1] += _gap_machine
            
            
    def action(self, action):
        pass
    
    
    def evaluate(self):
        pass
    
    
    def is_done(self):
        pass
    
    
    def observe(self):
        pass
    
    
    def view(self):
        # draw game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                self.mode += 1
                self.mode %= 3
                
        for job in self.jobs:
            job.draw()
            
        # text