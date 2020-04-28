# Finite State Machine
from transitions import Machine
# Dronekit
from connection import connectVehicle
from set_states import setVehicleMode, armVehicle
from actions import takeoff
# Python Libraries
import time
import random
import enum


class Status(enum.Enum):
    EMPTY = 0
    AVAILABLE = 1
    STARTED = 2
    FAILED = 3


class Tasks(enum.Enum):
    NAVIGATE = 0
    SAMPLE = 1
    LAND = 2


class Mission(object):

    # The states
    states = ['idle', 'mission_analysis', 'preflight_check', 'task_control', 'path_planning',
              'navigating', 'obstacle_avoidance', 'descending', 'sampling', 'ascending', 'safe_landing']

    # Transitions between states
    transitions = [
        # # Initialization of flight
        # {'trigger': 'mission_available', 'source': 'idle', 'dest': 'mission_analysis'},
        # {'trigger': 'mission_feasible', 'source': 'mission_analysis',
        #     'dest': 'preflight_check'},
        # # Normal flight
        # {'trigger': 'conditions_met',
        #     'source': 'preflight_check', 'dest': 'task_control'},
        # {'trigger': 'waypoint_set', 'source': 'task_control', 'dest': 'path_planning'},
        # {'trigger': 'path_generated', 'source': 'path_planning', 'dest': 'navigating'},
        # {'trigger': 'waypoint_reached', 'source': 'navigating', 'dest': 'task_control'},
        # {'trigger': 'ready_to_land', 'source': 'task_control', 'dest': 'safe_landing'},
        # {'trigger': 'disarmed', 'source': 'safe_landing', 'dest': 'mission_analysis'},
        # # Obstacles avoidance task
        # {'trigger': 'obstacle_detected', 'source': 'navigating',
        #     'dest': 'obstacle_avoidance'},
        # {'trigger': 'safe', 'source': 'obstacle_avoidance', 'dest': 'path_planning'},
        # # Water sampling task
        # {'trigger': 'ready_to_sample', 'source': 'task_control', 'dest': 'descending'},
        # {'trigger': 'altitude_reached', 'source': 'descending', 'dest': 'sampling'},
        # {'trigger': 'sampling_done', 'source': 'sampling', 'dest': 'ascending'},
        # {'trigger': 'task_done', 'source': 'ascending', 'dest': 'task_control'},
        # # Completion
        # {'trigger': 'mission_complete', 'source': 'mission_analysis', 'dest': 'idle'}
    ]

    def __init__(self, name):

        # No anonymous superheroes on my watch! Every narcoleptic superhero gets
        # a name. Any name at all. SleepyMan. SlumberGirl. You get the idea.
        self.name = name

        self.mission_status = Status.EMPTY
        self.goal = []
        self.tasks = [Tasks.NAVIGATE, Tasks.LAND]
        self.current_task = None
        self.path = []

        # Initialize the state machine
        self.machine = Machine(
            model=self, states=Mission.states, transitions=Mission.transitions, initial='idle', queued=True)

        # Add some transitions. We could also define these using a static list of
        # dictionaries, as we did with states above, and then pass the list to
        # the Machine initializer as the transitions= argument.

        # Initialization of flight
        self.machine.add_transition(
            'start', 'idle', 'mission_analysis', conditions=['mission_available'])

        self.machine.add_transition(
            'proceed', 'mission_analysis', 'preflight_check', conditions=['mission_feasible'], after='check_sensors')

        # Normal flight
        self.machine.add_transition(
            'proceed', 'preflight_check', 'task_control', conditions=['safe_to_fly'], before='take_off')

        self.machine.add_transition(
            'proceed', 'task_control', 'navigating', conditions=['waypoint_set', 'is_to_navigate'], before='plan_path', after='navigate')

        self.machine.add_transition(
            'proceed', 'navigating', 'task_control', conditions=['waypoint_reached'])

        self.machine.add_transition(
            'proceed', 'task_control', 'safe_landing', conditions=['ready_to_land', 'is_to_land'], before='find_landmark', after='land')

        self.machine.add_transition(
            'proceed', 'safe_landing', 'mission_analysis')

        self.machine.on_enter_task_control('choose_action')
        self.machine.on_enter_mission_analysis('analyse_mission')
        # # Obstacles avoidance task
        # self.machine.add_transition(
        #     'avoid', 'navigating', 'obstacle_avoidance', conditions=['obstacle_detected'], before='locate_obstacle')

        # self.machine.add_transition(
        #     'navigate', 'obstacle_avoidance', 'navigating', conditions=['obstacle_detected'], before='plan_path')

        # # Water sampling task
        # self.machine.add_transition(
        #     'sample', 'task_control', 'sampling', before='check_sampling_zone')

        # self.machine.add_transition(
        #     'stand_by', 'sampling', 'task_control', conditions=['sampling_done'])

        # # Risk handling
        # self.machine.add_transition(
        #     'abort', 'navigating', 'task_control', conditions=['high_risk'])

        # self.machine.add_transition(
        #     'abort', 'sampling', 'task_control', conditions=['high_risk'])

        self.machine.add_transition(
            'rest', 'mission_analysis', 'idle', conditions=['mission_complete'])

        # # =========================Example================================
        # # At some point, every superhero must rise and shine.
        # self.machine.add_transition(trigger='wake_up', source='asleep', dest='hanging out')
        # # Superheroes are always on call. ALWAYS. But they're not always
        # # dressed in work-appropriate clothing.
        # self.machine.add_transition('distress_call', '*', 'saving the world',
        #                             before='change_into_super_secret_costume')

        # # When they get off work, they're all sweaty and disgusting. But before
        # # they do anything else, they have to meticulously log their latest
        # # escapades. Because the legal department says so.
        # self.machine.add_transition('complete_mission', 'saving the world', 'sweaty',
        #                             after='update_journal')

        # # Sweat is a disorder that can be remedied with water.
        # # Unless you've had a particularly long day, in which case... bed time!
        # self.machine.add_transition(
        #     'clean_up', 'sweaty', 'asleep', conditions=['is_exhausted'])
        # self.machine.add_transition('clean_up', 'sweaty', 'hanging out')

        # # Our NarcolepticSuperhero can fall asleep at pretty much any time.
        # self.machine.add_transition('nap', '*', 'asleep')
        # # ================================================================

    # Helper
    def add_mission(self, coordinates):
        self.goal = coordinates
        self.mission_status = Status.AVAILABLE
        print("Added goal at ", self.goal)

    # Callbacks
    def analyse_mission(self):
        if self.mission_status is Status.AVAILABLE:
            print("Feasible, mission started")
            self.mission_status = Status.STARTED
        elif self.mission_status is Status.STARTED:
            print("Mission complete")
            self.mission_status = Status.EMPTY

    def check_sensors(self):
        print("Good to take-off")

    def take_off(self):
        print("Taking off")

    def plan_path(self):
        print("Generating path")
        print("Path generated")

    def navigate(self):
        print("Navigating")

    def choose_action(self):
        print("Choosing next action")
        self.current_task = self.tasks.pop(0)

    def find_landmark(self):
        print("Looking for landmark")
        print("Landmark found")

    def land(self):
        print("Landing")

    # Conditions
    @property
    def mission_available(self):
        return self.mission_status == Status.AVAILABLE

    @property
    def mission_feasible(self):
        return self.mission_status == Status.STARTED

    @property
    def safe_to_fly(self):
        return True

    @property
    def waypoint_set(self):
        return True

    @property
    def waypoint_reached(self):
        return True

    @property
    def ready_to_land(self):
        return True

    @property
    def mission_complete(self):
        return True

    @property
    def is_to_navigate(self):
        return self.current_task == Tasks.NAVIGATE

    @property
    def is_to_land(self):
        return self.current_task == Tasks.LAND


if __name__ == "__main__":
    dip = Mission("DIP")
    # coordinates = input("Enter the sampling coordinates: ").split()
    coordinates = [1, 2, 3]
    dip.add_mission(coordinates)
    print("Current state: ", dip.state)
    dip.start()
    print("Current state: ", dip.state)
    while (dip.mission_status != Status.EMPTY):
        time.sleep(1)
        dip.proceed()
        print("Current state: ", dip.state)
    dip.rest()
