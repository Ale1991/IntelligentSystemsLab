import json
from src.direction import Direction
from utility import EnumEncoder
def main():
    x = 10
    y = 5
    dir = Direction.EST
    jsn_dir = json.dumps(dir, cls=EnumEncoder)
    jsn = json.dumps({ 'x': x, 'y': y, 'direction': jsn_dir})
    
    print(jsn)

    obj = json.loads(jsn)
    dir2 = json.loads(obj["direction"], object_hook=EnumEncoder.as_enum)
    print(dir2)
if __name__ == "__main__":
    main()