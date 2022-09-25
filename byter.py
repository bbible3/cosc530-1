from enum import Enum
class Units(int, Enum):
    B = 10
    KB = 20
    MB = 30
    GB = 40
    TB = 50
    PB = 60
    EB = 70
    ZB = 80
    YB = 90
class Byter:
    def __init__(self, data, unit=Units.B):
        self.data = data
        self.unit = unit
        #If the default unit is not bytes, convert the data to bytes
        if self.unit != Units.B:
            self.data = self.to(self.data, self.unit, Units.B)
            self.unit = Units.B


    def to(self, data, from_unit=Units.B, to_unit=Units.KB):
        return (data * (2 ** from_unit)) / (2 ** to_unit)

    def as_size(self, unit=Units.B):
        return self.to(self.data, self.unit, unit)

    def as_string(self, unit=Units.B):
        return str(self.as_size(unit)) + " " + str(unit.name)


#Example: Returns 1.0 GB as string
#print(Byter(1024, unit=Units.MB).as_string(unit=Units.GB))
##val = Byter(1, unit=Units.KB)
##print("Does", val.as_string(Units.KB), "equal", val.as_string(Units.B), "?")
##print(val.as_size(Units.B) == 1024)

