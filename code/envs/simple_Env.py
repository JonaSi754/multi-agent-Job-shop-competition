import gym
import numpy as np
from gym.spaces import Discrete, Box
from gym.utils import seeding

from utils.read import read_JSP


jobs = read_JSP()

class Workpiece:
    def __init__(self, job):
        # basic info
        self.done = False
        self.No = job.No
        self.startTime = []
        self.endTime = []
        self.process_time = job.process_time
        self.machine_arrange = job.machine_arrange
        
        # state info
        self.stakes = 20  # total stakes
        self.bets = 0     # stake given each turn
        self.cur = 0      # next op no.
        self.progress = 0.0 # percentage of job
        self.condition = 0  # condition flag for wait or processing
        self.timer = 0      # count time for each op
        self.wait_time = 0  # time has been cost to wait
        self.next_op_cost = self.process_time[self.cur]
        
        
class Machine:
    def __init__(self, joblist, No):
        self.No = No
        self.job_list = joblist
        self.num_wait = len(joblist)
        self.possessed_time = 0
        
        
class simpleEnv(gym.Env):
    metadata = {"render_modes:" ["human"]}
    
    def __init__(self) -> None:
        """init method
        
        takes following attributes:
        - poosible_agents
        - action_spaces
        - observation_spaces
        
        These attributes should not be changed after initialization
        """
        super().__init__()
            
        # define action and observation spaces
        self._observation_shape = (11,)
        self._action_spaces = {agent: Discrete(20) for agent in self.possible_agents}
        self._observation_spaces = {agent: Box(low = np.zeros(self.observation_space, dtype=np.float32),
                                               high=np.array([1, 20, 100, 5000, 1, 20, 20, 20, 100, 100, 100], dtype=np.float32))
                                    for agent in self.possible_agents}
        
        
    def render(self):
        pass
    
    def close(self):
        pass
    
    
    def reset(self):
        """
        Reset needs to initialize the following attributes
        - agents
        - rewards
        - _cumulative_rewards
        - dones
        - infos
        - agent_selection
        And must set up the environment so that render(), step(), and observe()
        can be called without issues.

        Here it sets up the state dictionary which is used by step() and the observations dictionary which is used by step() and observe()
        """
        
        # define basic agent infos
        self.agents = self.possible_agents[:]
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.dones = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.state = {agent: None for agent in self.agents}
        self.observations = {agent: None for agent in self.agents}
        
        # define jobs and machines
        self.jobs = []
        self.machines = []
        self.num_agents = len(self.jobs)
        self.possible_agents = [a for a in range(self.num_agents)]
        for job in jobs:
            self.jobs.append(Workpiece(job))
        for i in range(self.num_machines):
            self.machiens.append(Machine(job, i))
            
        # define state related infos
        self.stakes_cnt = []
        self.progress_cnt = []
        self.next_op_cost_cnt = []
        self.num_done = 0
        
        # reward related
        self._longest_op = max([max(job.process_time) for job in self.jobs])
        
        
    def seed(self, seed=None):
        if seed is None:
            _, seed = seeding.np_random()
        np.random.seed(seed)
        
    
    def step(self, action, agent):
        pass