from collections import defaultdict
from collections import UserDict
from typing import Dict, List
from utils_decorators import mission_myturn_only
import numpy as np
import random

import json

from dataclasses import dataclass

CARRY_THRESHOLD_BASE = 40.0
MAX_CAP = 999999.0
DWARF_TURN = "DWARF_TURN"
ALIEN_TURN = "ALIEN_TURN"
END_TURN = "END_TURN"
DWARF_STATS_CAP = 5
DWARF_SUM_STATS_CAP = 10


class Molly:
    
    def __init__(self, name, current_mission, carried_minerals=None):
        self.name = name
        self.current_mission = current_mission
        self.carried_minerals = Minerals(MAX_CAP, **carried_minerals)
    
    def __str__(self):
        output = ""
        output += "Molly: %s" % (self.name)
        output += "Current mission: %s" % (self.current_mission)
        output += "Carried minerals: \n\t"
        output += str(self.carried_minerals).replace("\n", "\n\t")
        return output
    
    @property
    def dict_repr(self):
        return {
            "name": self.name,
            "current_mission": self.current_mission,
            "carried_minerals": self.carried_minerals.dict_repr
        }
    
    def __str__(self):
        output = ""
        output += "Name: %s\n" % (self.name)
        output += "Current Mission: %s\n" % (self.current_mission)
        output += "Carried minerals: \n\t"
        output += str(self.carried_minerals).replace("\n", "\n\t")[:-1]
        return output


class Dwarf:
        
    def __init__(self, name, _id, base_stats: Dict, minerals=None, carried_minerals=None, _in_mission=False, _my_turn=False):
        self.name = name
        self._id = _id
        self.base_stats = CharBaseStatsFactory(**base_stats)
        self.minerals = Minerals(MAX_CAP, **minerals)
        self.carried_minerals = Minerals(self.carry_weight, **carried_minerals)
        self._in_mission = False
        self._my_turn = False
        self.current_mission = None
        
    @mission_myturn_only
    def mine_random(self, verbose=True):
        mineral = random.choice(self.carried_minerals.names)
        mined_value = np.around(random.uniform(0.1, 10.), 1)
        self.carried_minerals[mineral] += mined_value
        if verbose:
            output = "%s has mined %s %s!" % (self.name, mined_value, mineral.replace("_", " "))
            return output
        
    @mission_myturn_only
    def deposit_minerals(self, molly: Molly, verbose=True):
        if self.current_mission == molly.current_mission:
            for mineral in self.carried_minerals:
                molly.carried_minerals[mineral] += self.carried_minerals[mineral]
                self.carried_minerals[mineral] = 0
            if verbose:
                output = "%s has deposited his/her minerals" % (self.name)
                return output
        else:
            return "ITS NOT YOUR MOLLY"
    
    def carry_weight(self):
        return (CARRY_THRESHOLD_BASE +
                # self.equipments.weight +
                self.base_stats.base_force * 5)
    
    @property
    def speed(self):
        return (self.base_stats.base_speed * 2
                # self.equipments.speed
                )
    
    def __str__(self):
        output = ""
        output += "Dwarf: %s\n" % (self.name)
        output += "Stats: \n\t"
        output += str(self.base_stats).replace("\n", "\n\t")[:-1]
        output += "Max carry weight: %s\n" % (self.carry_weight())
        output += "Current mission: %s\n" % (self.current_mission)
        output += "My turn: %s\n" % (self._my_turn)
        output += "Minerals: \n\t"
        output += str(self.minerals).replace("\n", "\n\t")[:-1]
        output += "Carried minerals: \n\t"
        output += str(self.carried_minerals).replace("\n", "\n\t")
        return output

    @property
    def dict_repr(self):
        return {
            "name": self.name,
            "_id": self._id,
            "base_stats": self.base_stats.dict_repr,
            "minerals": self.minerals.dict_repr,
            "carried_minerals": self.carried_minerals.dict_repr,
            "_in_mission": self._in_mission,
            "_my_turn": self._my_turn
        }
    

class MissionFactory:
    
    def __init__(self):
        self.missions = {}
        
    def begin_mission(self, mission_name, dwarfs: List[Dwarf], molly_name, clear_condition, difficulty):
        for dwarf in dwarfs:
            if dwarf._in_mission:
                return "One dwarf is already in a mission."
        molly = Molly(molly_name, mission_name, {})
        self.missions[mission_name] = Mission(mission_name, dwarfs, clear_condition, molly, difficulty)
        return "%s mission has begun." % mission_name
        
    def end_mission(self, mission_name):
        del self.missions[mission_name]
        
    def __getitem__(self, key):
        return self.missions[key]
    
    def __setitem__(self, key, value):
        self.missions[key] = value
        
    def __delitem__(self, key):
        self.missions[key].__del__()
        del self.missions[key]
        
    def __iter__(self):
        return (key for key in self.missions.keys())
    
    def values(self):
        return (value for value in self.missions.values())

class Mission:
    
    def __init__(self, mission_name, dwarfs: List[Dwarf], clear_condition, molly: Molly, difficulty: int = 1, turn=None):
        self.mission_name = mission_name
        self.dwarfs = dwarfs
        self.aliens = []
        self.clear_condition = clear_condition
        self.molly = molly
        self.difficulty = difficulty
        for dwarf in self.dwarfs:
            dwarf.current_mission = self.mission_name
            dwarf._in_mission = True
        self.turn = self.next_turn()
        _, _, self.playturn_entity = next(self.turn)
        if turn:
            while self.playturn_entity._id != turn:
                _, _, self.playturn_entity = next(self.turn)
                
            
    def take_action(self, entity, action, *args, **kwargs):
        if not entity._in_mission:
            return False, "IMPOSSIBULU, YOU AER NOT IN DUTY BIATCH"
        if entity.current_mission != self.mission_name:
            return False, "IMPOSSIBULU, WREONG MISSION BIOTACH"
        if not entity._my_turn:
            return False, "IMPOSSIBULU, NOT YOUR TURN BIATCH"
        action_response = "[%s]: " % self.mission_name
        action_response += action(*args, **kwargs)
        TURN, next_turn_response, self.playturn_entity = next(self.turn)
        if TURN == END_TURN:
            final_turn_response = next_turn_response
            TURN, next_turn_response, self.playturn_entity = next(self.turn)
            return True, "%s\n\n%s\n\n%s" % (action_response, final_turn_response, next_turn_response)
        else:
            return True, "%s\n\n%s" % (action_response, next_turn_response)

    def turn_order(self):
        return sorted([(entity, entity.speed) for entity in self.dwarfs + self.aliens], key = lambda t: t[1], reverse=True)
    
    def next_turn(self):
        while True:
            turn_order = self.turn_order()
            for entity, _ in turn_order:
                entity._my_turn = True
                if entity in self.dwarfs:
                    yield (DWARF_TURN, self.next_turn_response(entity), entity)
                else:
                    yield (ALIEN_TURN, self.next_turn_response(entity), entity)
                entity._my_turn = False
            yield self.end_of_turn()
            
    def next_turn_response(self, entity):
        return "[%s]: it is %s turn." % (self.mission_name, entity.name)
    
    def end_of_turn(self):
        # do blabla
        output = "End of turn"
        return END_TURN, output, None
            
    def __del__(self):
        print("ha")
        for dwarf in self.dwarfs:
            dwarf.current_mission = None
            dwarf._in_mission = False
            dwarf._my_turn = False
            for mineral in self.molly.carried_minerals.names:
                dwarf.minerals[mineral] += self.molly.carried_minerals[mineral]
        del self.mission_name
        del self.molly
        del self.difficulty
        del self
        
    @property
    def dict_repr(self):
        return {
            "mission_name": self.mission_name,
            "dwarfs_ids": [dwarf._id for dwarf in self.dwarfs],
            "clear_condition": self.clear_condition,
            "molly": self.molly.dict_repr,
            "difficulty": self.difficulty,
            "turn": self.playturn_entity._id
        }
    
    def __str__(self):
        output = ""
        output += "Mission name: %s\n" % (self.mission_name)
        output += "Dwarfs: %s\n" % (str([dwarf.name for dwarf in self.dwarfs]))
        output += "Clear condition: %s\n" % (self.clear_condition)
        output += "Molly :\n\t"
        output += str(self.molly).replace("\n", "\n\t")[:-1]
        output += "Difficulty: %s\n" % (self.difficulty)
        output += "Current turn: %s\n" % (self.playturn_entity.name)

        return output
        

@dataclass
class Minerals:

    cap: "Function or Float"
    _bismor: float = 0.0
    _croppa: float = 0.0
    _enor_pearl: float = 0.0
    _jadiz: float = 0.0
    _magnite: float = 0.0
    _umanite: float = 0.0
        
    def __post_init__(self):
        for mineral_name in self.names:
            setattr(type(self),
                    mineral_name,
                    property(fget=self._get_minerals(mineral_name),
                             fset=self._set_capped_minerals(mineral_name)))
    
    @staticmethod
    def _get_minerals(name):
        def fget(self):
            return getattr(self, "_" + name)
        fget.__name__ = name
        return fget

    @staticmethod
    def _set_capped_minerals(name):
        def fset(self, value):
            cap = getattr(self, "cap")() if callable(getattr(self, "cap")) else getattr(self, "cap")
            if value > cap:
                setattr(self, "_" + name, cap)
            else:
                setattr(self, "_" + name, float(value))
        fset.__name__ = name + "_setter"
        return fset
    
    @property
    def dict_repr(self):
        return {
            "_bismor": self.bismor,
            "_croppa": self.croppa,
            "_enor_pearl": self.enor_pearl,
            "_jadiz": self.jadiz,
            "_magnite": self.magnite,
            "_umanite": self.umanite
        }

    @property
    def names(self):
        return [
            "bismor",
            "croppa",
            "enor_pearl",
            "jadiz",
            "magnite",
            "umanite"
        ]
    
    def __str__(self):
        output = ""
        for name, value in [
            ("bismor", self.bismor),
            ("croppa", self.croppa),
            ("enor pearl", self.enor_pearl),
            ("jadiz", self.jadiz),
            ("magnite", self.magnite),
            ("umanite", self.umanite)
        ] :
            output += "%s: %.1f\n" % (name, value)
        return output
    
    def __getitem__(self, key):
        return getattr(self, key)
    
    def __setitem__(self, key, value):
        setattr(self, key, value)
        
    def __iter__(self):
        return (dwarf for dwarf in self.names)


from collections import abc

class TransformedDict(abc.MutableMapping):
    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys"""

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key
    
class DictKeyStr(TransformedDict):

    def __keytransform__(self, key):
        return str(key)
    
class CharBaseStatsFactory:
    
    def __init__(self, base_force, base_intelligence, base_dexterity, base_speed):
        assert base_force + base_intelligence + base_dexterity + base_speed <= DWARF_SUM_STATS_CAP, "Impossibulu sum cap"
        assert base_force <= DWARF_STATS_CAP or base_intelligence <= DWARF_STATS_CAP or base_dexterity <= DWARF_STATS_CAP or base_speed <= DWARF_STATS_CAP, "Impossibulu stat cap"
        self.base_force = base_force
        self.base_intelligence = base_intelligence
        self.base_dexterity = base_dexterity
        self.base_speed = base_speed
        
    @property
    def dict_repr(self):
        return {
            "base_force": self.base_force,
            "base_intelligence": self.base_intelligence,
            "base_dexterity": self.base_dexterity,
            "base_speed": self.base_speed
        }
    
    def __str__(self):
        output = ""
        for name, value in [
            ("base force", self.base_force),
            ("base intelligence", self.base_intelligence),
            ("base dexterity", self.base_dexterity),
            ("base speed", self.base_speed)
        ] :
            output += "%s: %s\n" % (name, value)
        return output

    
class Dwarf_guild:
    
    def __init__(self, name: str, init_data: dict=None):
        self.name = name
        self.dwarfs = DictKeyStr()
        self.mission_factory = MissionFactory()
        if init_data:
            for _id, dwarf_data in init_data["dwarfs"].items():
                self.dwarfs[_id] = Dwarf(**dwarf_data)
            for mission_name, mission_data in init_data["missions"].items():
                molly = Molly(**mission_data["molly"])
                dwarfs = [self.dwarfs[_id] for _id in mission_data["dwarfs_ids"]]
                del mission_data["dwarfs_ids"]
                del mission_data["molly"]
                self.mission_factory[mission_name] = Mission(molly=molly, dwarfs=dwarfs, **mission_data)
            
    def add_dwarf(self, _id: str, name: str, base_stats):
        self.dwarfs[_id] = Dwarf(name, _id, base_stats, {}, {}, False, False)
        
    @property
    def dict_repr(self):
        return {"dwarfs":
                    {_id: dwarf.dict_repr
                    for _id, dwarf
                    in self.dwarfs.items()},
                "missions":
                    {mission_name: mission.dict_repr
                    for mission_name, mission
                    in self.mission_factory.missions.items()}
               }
    
    def __str__(self):
        output = ""
        output += "Dwarf guild: %s\n" % (self.name)
        output += "Dwarfs:\n\t"
        for dwarf in self.dwarfs.values():
            output += "%s\n" % (str(dwarf).replace("\n", "\n\t\t"))
        output += "Missions:\n\t"
        for mission in self.mission_factory.values():
            output += "%s\n" % (str(mission).replace("\n", "\n\t\t"))

        return output
    
    def save_dwarf(self, json_file):
        with open(json_file, 'w') as outfile:
            json.dump(self.dict_repr, outfile)
