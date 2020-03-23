import functools
import inspect

MISSION_ONLY_WARNING = "Cannot do that, you are not in a mission."
MYTURN_ONLY_WARNING = "Not your turn, Bitch."

def mission_only(func):

    @functools.wraps(func)
    def decorated_function(self, *args, **kwargs):
        if self._in_mission:
            return func(self, *args, **kwargs)
        else:
            bound_args = inspect.signature(func).bind(self, *args, **kwargs)
            bound_args.apply_defaults()
            if "verbose" in bound_args.arguments:
                if bound_args.arguments["verbose"]:
                    return MISSION_ONLY_WARNING
    
    return decorated_function


def myturn_only(func):

    @functools.wraps(func)
    def decorated_function(self, *args, **kwargs):
        if self._my_turn:
            return func(self, *args, **kwargs)
        else:
            bound_args = inspect.signature(func).bind(self, *args, **kwargs)
            bound_args.apply_defaults()
            if "verbose" in bound_args.arguments:
                if bound_args.arguments["verbose"]:
                    return MYTURN_ONLY_WARNING
    
    return decorated_function


def mission_myturn_only(func):

    @functools.wraps(func)
    def decorated_function(self, *args, **kwargs):
        if self._in_mission and self._my_turn:
            return func(self, *args, **kwargs)
        else:
            bound_args = inspect.signature(func).bind(self, *args, **kwargs)
            bound_args.apply_defaults()
            if "verbose" in bound_args.arguments:
                if bound_args.arguments["verbose"] and not self._in_mission:
                    return MISSION_ONLY_WARNING
                elif bound_args.arguments["verbose"] and not self._my_turn:
                    return MYTURN_ONLY_WARNING
    
    return decorated_function