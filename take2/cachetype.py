from enum import Enum


class CacheType(str, Enum):
    DTLB = "Data TLB"
    PAGE_TABLE = "Page Table"
    DCACHE = "Data Cache"
    L2 = "L2 Cache"