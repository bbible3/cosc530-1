from enum import Enum
from configs import Config, ConfigFile
from addresshelper import AddrHelper, Address, AddressType, Mapping

#A class of enumerated response types for various cache actions
class CacheResponseType(str, Enum):
    READ_HIT = "READ_HIT" # Read hit
    READ_MISS = "READ_MISS" #This is returned when a read misses
    READ_MISS_AND_ADD = "READ_MISS_AND_ADD"
    
    WRITE_SUCCESS = "WRITE_SUCCESS" #This is returned when a write is successful
    
    
    PASS_TO_CHILD = "PASS_TO_CHILD" #This is returned when a write/read misses and must be passed to the child
    NO_READ_FROM_CHILDREN = "NO_READ_FROM_CHILDREN" #This is returned when a read misses and no children have the data
    NO_CHILD = "NO_CHILD" #This is returned when a read misses and there are no children

    SAVE_SUCCESS = "SAVE_SUCCESS" #This is returned when the save function is called by read/write successfully
#A class to represent cache types
class CacheType(str, Enum):
    DATA = "DATA"
    L2 = "L2"

#A class to represent a datapoint logged by the cache
class CacheResponse():
    def __init__(self, response_type, address, from_cache=None):
        self.response_type = response_type
        self.address = address
        self.from_cache = from_cache
    def print(self, indents=-0):
        print("\t"*indents+"Cache Response: " + self.response_type + " " + self.address.addr_str + " " + str(self.from_cache))

#A datum (byte) in a block
class CacheDatum():
    def __init__(self, tag, address):
        self.tag = tag
        self.address = address

#A block (line) in cache
class CacheBlock():
    def __init__(self, block_size=None):
        
        self.data = []
        self.block_size = block_size
        self.block_index = None
        
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

    #Returns true if we cannot add more data to this block
    def is_full(self):
        return len(self.data) == self.block_size

#A set of blocks in cache
class CacheSet():
    def __init__(self, set_size=None):
        self.set_size = set_size
        self.set = []
        self.set_index = None
        if self.set_size is None:
            raise Exception("Set size must be specified")

    #Append an existing, complete block to the set if possible
    def add_block(self, block):
        if len(self.set) < self.set_size:
            self.set.append(block)
            return True
        else:
            return False
            raise Exception("Set is full")

    #Create a new, empty block and add it to the set. Return it.
    def add_new_block(self):
        if self.is_full():
            raise Exception("Set is full")
        else:
            self.add_block(CacheBlock(self.set_size))
            return self.set[-1]
    #How many blocks are in this set?
    def len(self):
        return len(self.set)

    #Returns true if we cannot add more blocks to this set 
    def is_full(self):
        if len(self.set) < self.set_size:
            return False
        return True


    #Returns the first block in the set that is not full
    #If all blocks in set are full, try to create a new block
    #If we cannot create a new block, return None
    def first_available_block(self):
        for block in self.set:
            if block.is_full() == False:
                return block
        #Is there room to add a new block?
        if self.add_new_block():
            return self.set[-1]
        else:
            return None

#A class to represent a cache
class Cache():
    def __init__(self, config):
        if not isinstance(config, Config):
            raise TypeError("Cache's config must be of type Config")
        
        self.config = config
        self.sets = {}
        self.cache_responses = []

        self.child_cache = None
        self.parent_cache = None

        self.cache_type = None

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
    
    #Set the child cache, and the child's parent cache to this cache
    def set_child(self, child):
        self.child_cache = child
        child.parent_cache = self

    #Add a new set to the cache if possible
    def add_set(self, set_index):
        if len(self.sets) < self.num_sets:
            self.sets[set_index] = CacheSet(self.set_size)
            return True
        else:
            raise Exception("Tried to add a set when cache is full")


    def is_set_full(self, set_index):
        #Does an entry in dict self.sets with key set_index exist?
        if set_index not in self.sets:
            return False
        return self.sets[set_index].is_full()

    def get_or_create_set(self, set_index):
        #Does the set exist?
        print("Getting or creating set {}".format(set_index))
        if set_index not in self.sets:
            #Create the set
            self.sets[set_index] = CacheSet(self.set_size)
        return self.sets[set_index]

    
    #A read operation
    def read(self, address):
        #Make sure address is of type Address
        if not isinstance(address, Address):
            raise TypeError("Address must be of type Address")
        
        #Map the address using AddressMapping to get the offset, index, and tag
        #If tag length is left blank, it will be calculated automatically
        mapping = address.mapping(self.config.cache_offset_bits, self.config.cache_index_bits)
        #At this point, mapping.tag, mapping.index, and mapping.offset are all ints that represent the tag, index, and offset of the address
        #We want to check if the index is in the cache
        #If it is, we want to check if the tag is in the set
        for set in self.sets.values():
            for block in set.set:
                #Does the index match?
                if block.block_index == mapping.index:
                    for datum in block.data:
                        #Does the tag match?
                        if datum.tag == mapping.tag:
                            #Cache hit - this address is in the cache.
                            #HIT
                            self.cache_responses.append(CacheResponse(CacheResponseType.READ_HIT, address, from_cache=self.cache_type))
                            return True
        #Cache miss - the address is no tin this level of cache.
        cache_response = CacheResponse(CacheResponseType.READ_MISS, address, from_cache=self.cache_type)
        self.cache_responses.append(cache_response)
        #At this point, we have a miss. We need to either proceed to read from a lower level of memory, or add the address to the cache

        #Do we have a child cache?
        if self.child_cache is not None:
            self.cache_responses.append(CacheResponse(CacheResponseType.PASS_TO_CHILD, address, from_cache=self.cache_type))
            
            #Tell the child cache to try to read the address
            read_recursive_response = self.child_cache.read(address)
            #If all recursive children fail, write it to the cache at this level.
            if read_recursive_response == False:
                self.cache_responses.append(CacheResponse(CacheResponseType.NO_READ_FROM_CHILDREN, address, from_cache=self.cache_type))
                #Currently, we want to just add the address to the current level of cache
                #A recursive write-through will be implemented later
                self.save(address)
        else:
            #We have no child cache, so return False
            self.cache_responses.append(CacheResponse(CacheResponseType.NO_CHILD, address, from_cache=self.cache_type))
            return False
   
    #Save an address to the cache.
    #Different from write - this is called by write AND read.
    def save(self, address):

        print("Saving address", address.addr_str)
        #Make sure address is of type Address
        if not isinstance(address, Address):
            raise TypeError("Address must be of type Address")
        
  
        #Map the address using AddressMapping to get the offset, index, and tag
        mapping = address.mapping(n_offset=self.config.cache_offset_bits, n_index=self.config.cache_index_bits)
        mapping.print()

        #print("Trying to add datum")

        #Setup which_set
        which_set = None
        #Direct mapping
        if (self.num_sets == 1):
            which_set = self.first_available_set()
        elif (self.num_sets > 1):
            if self.is_set_full(mapping.index):
                which_set = None
            else:
                which_set = self.get_or_create_set(mapping.index)
                #Need to evict...

        #No set has room, so we need to evict
        if which_set is None:
            return False

        which_block = which_set.first_available_block()
        if which_block is None:
            raise Exception("Error on save: No block available in set")
        if which_block.is_full() != True:
            #We have a block that has room for a new datum, add it
            which_block.add_datum(CacheDatum(mapping.tag, address))
            #Change this later
            which_block.block_index = mapping.index

            cache_response = CacheResponse(CacheResponseType.SAVE_SUCCESS, address, from_cache=self.cache_type)
            self.cache_responses.append(cache_response)
            return True
        return False
        



#A class to facilitate testing of the cache
def cache_tester():
    myConfig = ConfigFile("./memhier/trace.config")
    myConfig.load_file()
    myConfig.parse_lines()
    myConfig.process_config()


    print("Num configs = ", len(myConfig.configs))
    for config in myConfig.configs:
        #Print the name of the config
        print("Config name = ", config)
        print("\tAssociativity/num_sets = ", myConfig.configs[config].num_sets)

    dc_config = myConfig.configs['Data Cache ']
    dc_config.cache_offset_bits = myConfig.cache_offset_bits
    dc_config.cache_index_bits = myConfig.cache_index_bits
    dc_cache = Cache(dc_config)
    dc_cache.cache_type = CacheType.DATA
    print("Index bits = ", dc_config.cache_index_bits)
    print("Offset bits = ", dc_config.cache_offset_bits)

    l2_config = myConfig.configs['L2 Cache ']
    l2_config.cache_offset_bits = myConfig.cache_offset_bits
    l2_config.cache_index_bits = myConfig.cache_index_bits
    l2_cache = Cache(l2_config)
    l2_cache.cache_type = CacheType.L2
    

    dc_cache.set_child(l2_cache)
    
    #dc_cache.read(Address("0xFEEDBEEF"))
    #dc_cache.read(Address("0xFEEDBEEF"))
    print("Predicted virtual address length = ", dc_config.max_ref_addr_len)
    addr = Address("0xc84")
    print(addr.bin_formatted())
    dc_cache.read(addr)

    print("Responses for data cache:")
    for response in dc_cache.cache_responses:
        response.print(indents=1)
    print("Responses for L2 cache:")
    for response in l2_cache.cache_responses:
        response.print(indents=1)
    
    #We expect READ_MISS, WRITE_SUCCESS, READ_HIT
    #Because the first read should miss as this is a fresh cache
    #Then, on read miss, we should write the address to the cache
    #Then, on the second read, we should hit the cache.

cache_tester()