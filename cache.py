from enum import Enum
from configs import Config, ConfigFile
from addresshelper import AddrHelper, Address, AddressType, Mapping

class CacheResponseType(str, Enum):
    READ_HIT = "READ_HIT"
    READ_MISS = "READ_MISS" #This is returned when a read misses
    READ_MISS_AND_ADD = "READ_MISS_AND_ADD"
    WRITE_SUCCESS = "WRITE_SUCCESS" #This is returned when a write is successful
class CacheResponse():
    def __init__(self, response_type, address):
        self.response_type = response_type
        self.address = address
    def print(self):
        print("Cache Response: " + self.response_type + " " + self.address.addr_str)
class CacheDatum():
    def __init__(self, tag, address):
        self.tag = tag
        self.address = address

class CacheBlock():
    def __init__(self, block_size=None):
        
        self.data = []
        self.block_size = block_size
        
        if self.block_size is None:
            #Raise an exception
            raise Exception("Block size must be specified")
    def add_datum(self, datum):
        if len(self.data) < self.block_size:
            self.data.append(datum)
        else:
            raise Exception("Tried to add datum to block that is full")
    def len(self):
        return len(self.data)

    def is_full(self):
        return len(self.data) == self.block_size

class CacheSet():
    def __init__(self, set_size=None):
        self.set_size = set_size
        self.set = []
        if self.set_size is None:
            raise Exception("Set size must be specified")
    def add_block(self, block):
        if len(self.set) < self.set_size:
            self.set.append(block)
        else:
            raise Exception("Set is full")
    def add_new_block(self):
        if self.is_full():
            raise Exception("Set is full")
        else:
            self.add_block(CacheBlock(self.set_size))
            return self.set[-1]

    def len(self):
        return len(self.set)        
    def is_full(self):
        for block in self.set:
            if not block.is_full():
                return False
    def first_available_block(self):

        for block in self.set:
            if block.is_full() == False:
                return block
        #Is there room to add a new block?
        if self.add_new_block():
            return self.set[-1]

class Cache():
    def __init__(self, config):
        if not isinstance(config, Config):
            raise TypeError("Cache's config must be of type Config")
        
        self.config = config
        self.sets = []
        self.cache_responses = []

        #How many sets?
        self.num_sets = self.config.num_sets
        if self.num_sets is None:
            raise Exception("Number of sets must be specified")

        #How many blocks per set?
        self.set_size = self.config.set_size
        if self.set_size is None:
            raise Exception("Set size must be specified")
        
        #How big is each block?
        self.block_size = self.config.line_size
        if self.block_size is None:
            raise Exception("Block size must be specified")

        print("Initialised cache with {} sets, {} blocks per set, and {} datum per block".format(self.num_sets, self.set_size, self.block_size))
    def add_set(self):
        if len(self.sets) < self.num_sets:
            self.sets.append(CacheSet(self.set_size))
            return True
        else:
            raise Exception("Tried to add a set when cache is full")

    def add_to_any_set(self, block):
        for set in self.sets:
            if set.len() < self.set_size:
                set.add_block(block)
                return True
        return False

    def is_full(self):
        if self.first_available_set() is None:
            return True
        return False

    def first_available_set(self):
        for set in self.sets:
            if set.is_full == False:
                return set
        #Can we add a new set?
        if self.add_new_set():
            return self.sets[-1]
        return None
    
    def add_new_set(self):
        if len(self.sets) < self.num_sets:
            self.sets.append(CacheSet(self.set_size))
            return True
        return False

    def read(self, address):
        #Make sure address is of type Address
        if not isinstance(address, Address):
            raise TypeError("Address must be of type Address")
        
        mapping = address.mapping(self.config.cache_offset_bits, self.config.cache_index_bits)
        #At this point, mapping.tag, mapping.index, and mapping.offset are all ints that represent the tag, index, and offset of the address
        #We want to check if the index is in the cache
        #If it is, we want to check if the tag is in the set
        for set in self.sets:
            for block in set.set:
                for datum in block.data:
                    if datum.tag == mapping.tag:
                        #Cache hit - this address is in the cache.
                        #print("HIT!")
                        self.cache_responses.append(CacheResponse(CacheResponseType.READ_HIT, address))
                        return True
        #print("MISS!")
        cache_response = CacheResponse(CacheResponseType.READ_MISS, address)
        self.cache_responses.append(cache_response)
        #At this point, we have a miss. We need to either proceed to read from a lower level of memory, or add the address to the cache

        #Branch here depending on cache behaviour. For testing, let's just have it write.
        self.write(address)
   
    def write(self, address):
        #Make sure address is of type Address
        if not isinstance(address, Address):
            raise TypeError("Address must be of type Address")
        
        mapping = address.mapping(self.config.cache_offset_bits, self.config.cache_index_bits)
        if self.is_full():
                #Cache is full, evict a block
                raise Exception("Error on read: Cache is full, evict a block.")
                pass
            
        #print("Trying to add datum")
        which_set = self.first_available_set()
        which_block = which_set.first_available_block()
        if which_block.is_full() != True:
            which_block.add_datum(CacheDatum(mapping.tag, address))
            cache_response = CacheResponse(CacheResponseType.WRITE_SUCCESS, address)
            self.cache_responses.append(cache_response)
            return True
        return False
        




def cache_tester():
    myConfig = ConfigFile("./memhier/trace.config")
    myConfig.load_file()
    myConfig.parse_lines()
    myConfig.process_config()

    print("Num configs = ", len(myConfig.configs))
    for config in myConfig.configs:
        #Print the name of the config
        print("Config name = ", config)

    curconfig = myConfig.configs['Data Cache ']
    curconfig.cache_offset_bits = myConfig.cache_offset_bits
    curconfig.cache_index_bits = myConfig.cache_index_bits
    mycache = Cache(curconfig)
    
    mycache.read(Address("0xFEEDBEEF"))
    mycache.read(Address("0xFEEDBEEF"))
    for response in mycache.cache_responses:
        response.print()
    
    #We expect READ_MISS, WRITE_SUCCESS, READ_HIT
    #Because the first read should miss as this is a fresh cache
    #Then, on read miss, we should write the address to the cache
    #Then, on the second read, we should hit the cache.

cache_tester()