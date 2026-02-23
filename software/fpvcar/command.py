from typing import TypeVar
from abc import ABC

TCommand = TypeVar('TCommand', bound='Command')

class Command(ABC):
    values: dict[str, int]
    
    def __init__(self):
        self.values = dict()
    
    def __add__(self, other: TCommand):
        new = Command()
        for key in self.values:
            new.values[key] = self.values[key]
        for key in other.values:
            new.values[key] = other.values[key]
        return new
            
class Speed(Command):
    def __init__(self, speed: int):
        super().__init__()
        self.values['speed'] = speed
        self.values['time'] = 200
        
class Turn(Command):
    def __init__(self, turn: int):
        super().__init__()
        self.values['turn'] = turn
        

MoveForward     = Speed(100)
MoveBackward    = Speed(-100)
Stop            = Speed(0)

TurnRight       = Turn(-100)
TurnLeft        = Turn(100)
TurnStraight       = Turn(0)

MoveForwardStraight     = MoveForward + TurnStraight
MoveForwardLeft         = MoveForward + TurnLeft
MoveForwardRight        = MoveForward + TurnRight
MoveBackwardStraight    = MoveBackward + TurnStraight
MoveBackwardLeft        = MoveBackward + TurnLeft
MoveBackwardRight       = MoveBackward + TurnRight