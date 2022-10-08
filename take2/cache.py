from enum import Enum
from config import Config
from address import Address, Mapping
from cachetype import CacheType

class Data():
    def __init__(self):
        self.tag = None
        self.index = None
        self.offset = None
        self.vpn = None
        self.pfn = None
        self.data = None
class Block():
    def __init__(self):
        self.data = Data()

class Set():
    def __init__(self, size):
        self.size = size
        self.blocks = []
    def add_block(self, block):
        if len(self.blocks) < self.size:
            self.blocks.append(block)
        else:
            return False

class Cache():
    def __init__(self, config=None, cache_type=None):
        self.config = config
        self.child = None
        self.parent = None
        self.cache_type = cache_type
        self.num_sets = None
        self.set_size = None
        self.sets = None

        #If we don't receive a config, or it is not of type Config, raise an error
        if type(self.config) != Config:
            raise ValueError("Cache must be initialized with a Config object")
        #If we don't receive a cache type, or it is not of type CacheType, raise an error
        if type(self.cache_type) != CacheType:
            raise ValueError("Cache must be initialized with a valid CacheType")

        if self.cache_type == CacheType.DTLB:
            self.num_sets = self.config.dtlb_num_sets
            self.set_size = self.config.dtlb_set_size
            self.sets = {}
        elif self.cache_type == CacheType.DCACHE:
            self.num_sets = self.config.dc_num_sets
            self.set_size = self.config.dc_set_size
            self.sets = {}
        elif self.cache_type == CacheType.L2:
            self.num_sets = self.config.l2_num_sets
            self.set_size = self.config.l2_set_size
            self.sets = {}

    def add_get_set(self, index):
        
        if index in self.sets:
            return self.sets[index]

        if len(self.sets) < self.num_sets:
            self.sets[index] = Set(self.set_size)
            return self.sets[index]
        else:
            return None

    def read(self, read_addr_str):
        #Is the address a valid string?
        if type(read_addr_str) != str:
            raise ValueError("Address must be a string")
        #Is the address a valid hex string?
        if not read_addr_str.startswith("0x"):
            raise ValueError("Address must be a hex string")
        read_addr = Address(read_addr_str)
        #Get the bits we need to index the cache
        addr_bits = read_addr.get_bits(self.config, self.cache_type)
        #What is the index?
        index = addr_bits.index

        #Are we in TLB mode?
        if self.cache_type == CacheType.DTLB:
            #Does a set with this index exist?
            if index in self.sets:
                #Does a block with this tag exist?
                for block in self.sets[index].blocks:
                    if block.data.tag == addr_bits.tag:
                        #We found the block, return the pfn
                        return block.data.pfn
                return None
            return None
        else:
            #Is there a set at that index?
            if index in self.sets:
                for block in self.sets[index].blocks:
                    if block.tag == addr_bits.tag:
                        return block
                return None
            else:
                return None
    def save(self, addr, block):
        #Is the address of type Address?
        if type(addr) != Address:
            raise ValueError("Address must be of type Address")
        #Get the mapping from addr
        mapping = addr.get_bits(self.config, self.cache_type)

        which_set = self.add_get_set(mapping.index)
        #Is there a set at that index?
        if which_set != None:
            response = which_set.add_block(block)
            if response == False:
                #Need to evict
                return False
            else:
                return True

    def translate_addr(self, addr_to_translate=None, pfn=None):
        self.addr_to_translate = addr_to_translate
        self.pfn = pfn
        #If we don't receive an address to translate, raise an error
        if self.addr_to_translate == None:
            raise ValueError("Address to translate must be provided")
        if self.pfn == None:
            raise ValueError("Must provide a pfn to translate")
        #Is the pfn a valid hex string?
        if not self.pfn.startswith("0x"):
            raise ValueError("pfn must be a hex string")
        
        pfn_int = int(self.pfn, 16)
        pfn_bin = bin(pfn_int)[2:].zfill(self.config.addr_len)

        addr_to_translate_bits = self.addr_to_translate.get_bits(self.config, self.cache_type)
        
        new_addr_str_bin = pfn_bin + addr_to_translate_bits.offset
        new_addr_int = int("0b"+new_addr_str_bin, 2)
        new_addr_str_hex = str(hex(new_addr_int))
        new_addr = Address(new_addr_str_hex, is_virtual=False)
        return new_addr

        

            


class MemHier():
    def __init__(self, config):
        self.config = config
        #If we don't receive a config, or it is not of type Config, raise an error
        if type(config) != Config:
            raise ValueError("MemHier must be initialized with a Config object")

        self.mem_dtlb = Cache(config=self.config, cache_type=CacheType.DTLB)
        self.mem_page_table = Cache(config=self.config, cache_type=CacheType.PAGE_TABLE)
        self.mem_dcache = Cache(config=self.config, cache_type=CacheType.DCACHE)
        self.mem_l2 = Cache(config=self.config, cache_type=CacheType.L2)

        #Set the child and parent relationships
        self.mem_dtlb.child = self.mem_page_table
        self.mem_page_table.parent = self.mem_dtlb
        self.mem_page_table.child = self.mem_dcache
        self.mem_dcache.parent = self.mem_page_table
        self.mem_dcache.child = self.mem_l2
        self.mem_l2.parent = self.mem_dcache


def TestCache():
    config = Config("trace.config")
    memhier = MemHier(config)
    # test_address = Address("0xc84")
    # test_response = test_address.get_bits(config, CacheType.DTLB)
    # test_address.print(indents=1)
    # test_response.print(indents=1)
    # test_response.as_type = hex
    # test_response.print(indents=1)
    
    #test_read = memhier.mem_dtlb.read("0xc84")
    #print(test_read)

    
    # Try to add an address to the TLB manually
    #Add a virtual address to the TLB to play pretend
    addr = Address("0xc84") 
    block = Block()
    #Act as if we've gotten a pfn from the page table already
    block.data.pfn = "0x2"
    #Set the tag to the tag from the address manually
    block.data.tag = addr.get_bits(config, CacheType.DTLB).tag
    #Add the block to the TLB
    response = memhier.mem_dtlb.save(addr, block)
    print("Save response:", response)

    
    # Try to read the address from the TLB
    test_read = memhier.mem_dtlb.read("0xc84")
    print("Read response:", test_read)

    #Try to translate the address with the pfn we got from the TLB
    translated_addr = memhier.mem_dtlb.translate_addr(addr_to_translate=addr, pfn=test_read)
    print("Translated address:", translated_addr.addr_str)

print("Cache.py loaded")
TestCache()