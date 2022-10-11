from config import Config
from cachetype import CacheType

class Mapping():
    def __init__(self, tag=None, index=None, offset=None, vpn=None, as_type=bin, pfn=None):
        self.tag = tag
        self.index = index
        self.offset = offset
        self.vpn = vpn
        self.as_type = as_type
        self.pfn = pfn
    def print(self, indents=0):
        if self.as_type == hex:
            tag_int = int(self.tag, 2)
            index_int = int(self.index, 2)
            offset_int = int(self.offset, 2)
            vpn_int = int(self.vpn, 2)
            self.tag = hex(tag_int)
            self.index = hex(index_int)
            self.offset = hex(offset_int)
            self.vpn = hex(vpn_int)
        print(f"\t" * indents + f"Tag: {self.tag}, Index: {self.index}, Offset: {self.offset}")
        if self.vpn != None:
            print(f"\t" * indents + f"VPN: {self.vpn}")

class Address():
    def __init__(self, addr_str, is_virtual=True):
        self.addr_str = addr_str
        self.is_virtual = is_virtual
        self.pfn = None
        #Make sure this is a valid address... ie, a string of hex digits with leading 0x
        if addr_str[0:2] != "0x":
            raise ValueError("Address must start with 0x")
        if type(addr_str) != str:
            raise ValueError("Address must be a string")

        #Convert the address to an integer
        self.addr_int = int(addr_str, 16)

        #Convert the address to a binary string in format 0b101010101
        self.addr_bin = bin(self.addr_int)
        #If the address is less than specified length, pad with 0s
        if len(self.addr_bin) < 34:
            self.addr_bin = self.addr_bin[0:2] + "0" * (34 - len(self.addr_bin)) + self.addr_bin[2:]
    
    def range(self, start, end):
        bin_no_prefix = self.addr_bin[2:]
        #Return a slice of the address
        return bin_no_prefix[start:end]
    def get_bits(self, config, cache_type):
        #Make sure we have a config object
        if type(config) != Config:
            raise ValueError("Config must be a Config object")
        
        #Make sure we have a valid cache type
        if cache_type not in CacheType:
            raise ValueError("Cache type must be a valid CacheType")
        
        #Make sure we have a valid addr_bin
        if self.addr_bin == None:
            raise ValueError("Address must be initialized with a valid address")
        
        if cache_type == CacheType.DTLB:
            #Get the bits from the address
            tag = self.range(config.dtlb_tag_start, config.dtlb_tag_end)
            index = self.range(config.dtlb_index_start, config.dtlb_index_end)
            offset = self.range(config.dtlb_offset_start, config.dtlb_offset_end)
            vpn = self.range(config.dtlb_vpn_start, config.dtlb_vpn_end)
            return Mapping(tag, index, offset, vpn=vpn)
        elif cache_type == CacheType.PAGE_TABLE:
            #Get the bits from the address
            tag = self.range(config.pt_tag_start, config.pt_tag_end)
            index = self.range(config.pt_index_start, config.pt_index_end)
            offset = self.range(config.pt_offset_start, config.pt_offset_end)
            vpn = self.range(config.dtlb_vpn_start, config.dtlb_vpn_end)
            return Mapping(tag, index, offset, vpn=vpn)
        elif cache_type == CacheType.DCACHE:
            #Get the bits from the address
            tag = self.range(config.dc_tag_start, config.dc_tag_end)
            index = self.range(config.dc_index_start, config.dc_index_end)
            offset = self.range(config.dc_offset_start, config.dc_offset_end)
            return Mapping(tag, index, offset)
        elif cache_type == CacheType.L2:
            #Get the bits from the address
            tag = self.range(config.l2_tag_start, config.l2_tag_end)
            index = self.range(config.l2_index_start, config.l2_index_end)
            offset = self.range(config.l2_offset_start, config.l2_offset_end)
            return Mapping(tag, index, offset)
        else:
            raise ValueError("Cache type must be a valid CacheType")
    def print(self, indents=0):
        print(f"\t" * indents + f"Address: {self.addr_str}, Integer: {self.addr_int}, Binary: {self.addr_bin}")

            