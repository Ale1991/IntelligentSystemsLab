import json, sys

if __name__ == "__main__":
    from src.action import Action
    from src.direction import Direction
    from src.mapelement import MapElement
else:
    from src.action import Action
    from src.direction import Direction
    from src.mapelement import MapElement

AVAIABLE_CLASS = [Action, Direction, MapElement]

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) in AVAIABLE_CLASS:
            className, value = str(obj).split(".")
            return {f"{str(className)}": str(value)}
        return json.JSONEncoder.default(self, obj)


    def as_enum(str):
        if "Action" in str:
            return Action[str["Action"]] # WORKS: specific enum conversion
            # className, value = "Action", str["Action"]
            # return getattr(sys.modules[__name__], className)[value] # WORKS: general enum conversion
        elif "Direction" in str:
            return Direction[str["Direction"]] # WORKS: specific enum conversion
            # className, value = "Direction", str["Direction"]
            # return getattr(sys.modules[__name__], className)[value] # WORKS: general enum conversion
        elif "MapElement" in str:
            return MapElement[str["MapElement"]] # WORKS: specific enum conversion
            # className, value = "MapElement", str["MapElement"]
            # return getattr(sys.modules[__name__], className)[value] # WORKS: general enum conversion
        else:
            return str

# Test custom Json Converter
if __name__ == "__main__":
    act = MapElement.ENERGY # Action, Direction, MapElement conversion works
    j = json.dumps(act, cls=EnumEncoder) # from obj(Enum) to str
    print(j)
    obj = json.loads(j, object_hook=EnumEncoder.as_enum) # from str to obj(Enum)
    print(obj)