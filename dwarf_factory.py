from collections import defaultdict
from collections import UserDict
from typing import Dict
import numpy as np
import random

import json

from dataclasses import dataclass

CARRY_THRESHOLD_BASE = 40.0
MAX_CAP = 999999.0

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
        for mineral_name in [
            "bismor",
            "croppa",
            "enor_pearl",
            "jadiz",
            "magnite",
            "umanite"
        ]:
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
    def values(self):
        return {
            "_bismor": self.bismor,
            "_croppa": self.croppa,
            "_enor_pearl": self.enor_pearl,
            "_jadiz": self.jadiz,
            "_magnite": self.magnite,
            "_umanite": self.umanite
        }
    
    def __str__(self):
        output = ""
        for name, value in [
            ("bismor", self.bismor),
            ("croppa", self.croppa),
            ("enor_pearl", self.enor_pearl),
            ("jadiz", self.jadiz),
            ("magnite", self.magnite),
            ("umanite", self.umanite)
        ] :
            output += "%s: %s\n" % (name, value)
        return output
    
    def __getitem__(self, key):
        return getattr(self, key)
    
    def __setitem__(self, key, value):
        setattr(self, key, value)
        
    def __iter__(self):
        return (dwarf for dwarf in self.values)


class Dwarf:
        
    def __init__(self, name, minerals=None, carried_minerals=None):
        self.name = name
        self.minerals = Minerals(MAX_CAP, **minerals)
        self.carried_minerals = Minerals(self.carry_weight, **carried_minerals)
        
    def mine_random(self, verbose=False):
        mineral = random.choice(list(self.carried_minerals.values))
        mined_value = np.around(random.uniform(0.1, 10.), 1)
        self.carried_minerals[mineral] += mined_value
        if verbose:
            output = "%s has mined %s %s!" % (self.name, mined_value, mineral[1:])
            return output
    
    def carry_weight(self):
        return CARRY_THRESHOLD_BASE + self.equipment_add_weight
    
    def __str__(self):
        output = ""
        output += "Dwarf: %s\n" % (self.name)
        output += "Minerals: \n\t"
        output += str(self.minerals).replace("\n", "\n\t")[:-1]
        output += "Carried minerals: \n\t"
        output += str(self.carried_minerals).replace("\n", "\n\t")
        return output
    
    @property
    def equipment_add_weight(self):
        return 0

    @property
    def values(self):
        return {
            "name": self.name,
            "minerals": self.minerals.values,
            "carried_minerals": self.carried_minerals.values
        }

class Dwarf_guild:
    
    def __init__(self, name: str, init_data: dict=None):
        self.name = name
        self.dwarfs = {}
        if init_data:
            for _id, dwarf_data in init_data.items():
                self.dwarfs[_id] = Dwarf(**dwarf_data)
            
    def add_dwarf(self, _id: str, name: str):
        if isinstance(_id, int):
            _id = str(_id)
        self[_id] = Dwarf(name, {}, {})
        
    def __getitem__(self, key):
        if isinstance(key, int):
            key = str(key)
        return self.dwarfs[key]
    
    def __setitem__(self, key, value):
        if isinstance(key, int):
            key = str(key)
        self.dwarfs[key] = value
        
    def __iter__(self):
        return (dwarf for dwarf in self.dwarfs)
    
    def __contains__(self, key):
        return str(key) in self.dwarfs
        
    @property
    def values(self):
        return {_id: dwarf.values
                for _id, dwarf
                in self.dwarfs.items()}
    
    def save_dwarf(self, json_file):
        with open(json_file, 'w') as outfile:
            json.dump(self.values, outfile)
