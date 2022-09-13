from importlib.metadata import metadata
from gym.spaces import Box, Discrete
from gym.utils import seeding
import numpy as np
import functools

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import wrappers

from envs.compete_game_2d import PyGame2D


default_reward_args = dict(
    step_reward=-0.05,
    wait_penalty=-0.5,
    pass_reward=0.5,
    reach_terminal=1.0,
)


def env():
    """
    The env function often wraps the environment in wrappers by default.
    You can find full documentation for these methods
    elsewhere in the developer documentation.
    """
    # Provides a wide vareity of helpful user errors
    # Strongly recommended
    env = wrappers.OrderEnforcingWrapper(env)
    return env



class MAJspEnv(AECEnv):
    """Construct an env for multi agent JSP
    
    Each job is considered as an agent and they compete
    for machines, steps agent one at a time.
    
    This env is written under the guide of PettingZoo:
    https://github.com/Farama-Foundation/PettingZoo
    """
    
    
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "majsp_v0",
        "render_fps": 5,
    }
    
    def __init__(self, jobs):
        """
        The init method takes in environment arguments and
         should define the following attributes:
        - possible_agents
        - action_spaces
        - observation_spaces

        These attributes should not be changed after initialization.
        """
        
        self.pygame = PyGame2D()
        self.jobs = jobs
        self.num_agents = len(jobs)
        self.possible_agents = ["Job_" + str(j) for j in range(len(jobs))]
        self.agent_name_mapping = dict(
            zip(self.possible_agents, list(range(len(self.possible_agents))))
        )
        
        # define action and observation spaces
        # Gym spaces are defined here: https://gym.openai.com/docs/#spaces
        self._action_spaces = {agent: Discrete(20) for agent in self.possible_agents}
        self._observation_spaces = {agent: Discrete(11) for agent in self.possible_agents}
        # define the global space of environment or state
        self.state_space = Discrete(7)
        
    
    
    # this cache ensures that same space object is returned for the same agent
    # allows action space seeding to work as expected
    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return Box(low=np.zeros(1), high=np.ones(1), dtype=np.float32)
    
    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return Discrete(4)
    
        
    def render(self, mode="human", close=False):
        self.pygame.view()
    
    
    def observe(self, agent):
        """
        Observe should return the observation of the specified agent. This function
        should return a sane observation (though not necessarily the most up to date possible)
        at any time after reset() is called.
        """
        # observation of one agent is the previous state of the other
        return np.array(self.observations[agent])
    
    
    def close(self):
        """
        Close should release any graphical displays, subprocesses, network connections
        or any other environment data which should not be kept around after the
        user is no longer using the environment.
        """
        pass
    
    
    def reset(self, seed=None):
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
        self.agents = self.possible_agents[:]
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.dones = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.state = {agent: None for agent in self.agents}
        self.observations = {agent: None for agent in self.agents}
        del self.pygame
        self.pygame = PyGame2D()
        
        """
        Agent_selector utility allows easy cyclic stepping through the agents list.
        """
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()
    
    
    def seed(self, seed=None):
        if seed is None:
            _, seed = seeding.np_random()
        np.random.seed(seed)
    
    
    def step(self, action, agent):
        """
        step(action) takes in an action for the current agent (specified by
        agent_selection) and needs to update
        - rewards
        - _cumulative_rewards (accumulating the rewards)
        - dones
        - infos
        - agent_selection (to the next agent)
        And any internal state used by observe() or render()
        """
        # agent 传进来是一个智能体，job对象应该在self里定义好，agent和action传进来之后更新self里的job
        self.