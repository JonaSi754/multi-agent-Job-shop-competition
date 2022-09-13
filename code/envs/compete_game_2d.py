from statistics import mean
import pygame
import numpy as np

from utils.read import read_JSP

screen_width = 1500
screen_height = 1200
jobs = read_JSP()

class Workpiece:
    def __init__(self, job_img, pos, job):
        # basic info
        self.surface = pygame.image.load(job_img)
        self.surface = pygame.transform.scale(self.surface, (16, 16))
        self.pos = pos
        self.center = [self.pos[0] + 8, self.pos[1] + 8]
        self.done = False
        self.No = job.No
        self.startTime = []
        self.endTime = []
        self.process_time = job.process_time
        self.machine_arrange = job.machine_arrange
        self.speed = 0
        
        # state info
        self.stakes = 20  # total stakes
        self.bets = 0     # stake given each turn
        self.cur = 0      # next op no.
        self.progress = 0.0 # percentage of job
        self.condition = 0  # condition flag for wait or processing
        self.wait_time = 0  # time has been cost to wait
        self.next_op_cost = self.process_time[self.cur]
        
        
    def draw(self, screen):
        screen.blit(self.surface, self.pos)
        
    def update(self, gap):
        self.speed = gap / self.process_time[self.cur]
        
        
            
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
        self.num_wait = len(joblist)
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
        # basic info
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
        self.gap = _gap_machine
        for job in jobs:
            self.jobs.append(Workpiece('images\job_img.png', _init_pos_job, job))
            _init_pos_job[0] += _gap_job
        for i in range(self.num_machines):
            self.machiens.append(Machine('images\machine_img.png', _init_pos_machine, job))
            _init_pos_machine[1] += _gap_machine
            
        # env info
        self.stakes_cnt = []
        self.progress_cnt = []
        self.next_op_cost_cnt = []
        self.num_done = 0
        
        #reward related
        self.longest_op = max([max(job.process_time) for job in self.jobs])
        
        
    def get_bets(self, job_list, action_list):
        """get actual bets from each agent"""
        bets_list = []
        for i in range(len(job_list)):
            bets_list.append(job_list[i].place_bets(action_list[i]))
        return bets_list
            
            
    def action(self, job_list, action_list):
        """conduct action"""
        bets_list = self.get_bets(action_list)
        idx = bets_list.index(max(bets_list))
        winner = job_list[idx]
        return winner
    
    
    def evaluate(self, job_list, winner):
        """return reward
        
        get          <1>           for win a battle,
        get  <-p_ij / longest_op>  for fail a battle with less bets
        get        <-0.05>         for fail with same bets
        get         <-10>          for use out stakes before done
        get     <n - num_done>     for last reward
        """
        rewards = []
        for job in job_list:
            if job == winner and job.done:
                rewards.append(len(self.jobs) - self.num_done)
            elif job.bets == winner.bets:
                rewards.append(-0.05)
            elif job.stakes == 0 and not job.done:
                rewards.append(-20)
            else:
                rewards.append(winner.process_time[winner.cur] / self.longest_op)
        return rewards, winner
    
    
    def is_done(self):
        """if all jobs are done"""
        return sum([job.done for job in self.jobs]) == len(self.jobs)
    
    
    def observe(self, job, job_list):
        """return state
        
        scale: (11,)
        feature             num of channels
        my_progress,              1
        my_stakes,                1
        my_next_op_cost,          1
        my_wait_time,             1
        other_progress_mean,      1
        other_stakes_mean,        1
        other_stakes_most,        1
        other_stakes_least,       1
        other_next_op_cost_mean,  1
        other_next_op_cost_most,  1
        job_list_len,             1
        """
        obs = []
        obs.append(job.progress)
        obs.append(job.stakes)
        obs.append(job.next_op_cost)
        obs.append(job.wait_time)
        
        progress_list = [other_job.progress for other_job in job_list if not other_job == job]
        stakes_list = [other_job.stakes for other_job in job_list if not other_job == job]
        next_op_cost_list = [other_job.next_op_cost for other_job in job_list if not other_job == job]
        obs.append(mean(progress_list))
        obs.append(mean(stakes_list))
        obs.append(max(stakes_list))
        obs.append(min(stakes_list))
        obs.append(mean(next_op_cost_list))
        obs.append(max(next_op_cost_list))
        obs.append(len(job_list))
        
        return np.array(obs)
    
    
    def view(self):
        """draw game"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                self.mode += 1
                self.mode %= 3
                
        for job in self.jobs:
            job.draw()
            
        # text