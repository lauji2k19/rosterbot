from aenum import Enum

class Rank(Enum):
    _init_ = 'value string'

    NINE = 0, '09'
    EIGHT = 1, '08'
    SEVEN = 2, '07'
    SIX = 3, '06'
    FIVE = 4, '05'
    FOUR = 5, '04'
    THREE = 6, '03'
    TWO = 7, '02'
    ONE = 8, '01'
    EPU = 9, 'EpU'
    SQL = 10, 'SqL'
    TOFC = 11, 'T-OfC'
    OFCI = 12, 'OfC-I'
    OFCII = 13, 'OfC-II'
    OFCIII = 14, 'OfC-III'
    CMD = 15, 'CmD'

    def __str__(self):
        return self.string
    
    @classmethod
    def _missing_value_(cls, value):
        for member in cls:
            if member.string == value:
                return member
    
    @classmethod
    def has_value(cls, value):
        for member in cls:
            if member.string == value:
                return True
        return False
    
    @staticmethod
    def promote_unit(current_rank):
        return Rank(Rank._missing_value_(current_rank).value+1)
    
    @staticmethod
    def demote_unit(current_rank):
        return Rank(Rank._missing_value_(current_rank).value-1)