from enum import Enum
from config import Config
from address import Address, Mapping
from cachetype import CacheType

class CacheLogType(str, Enum):
    READ_HIT = "Read Hit"
    READ_MISS = "Read Miss"
    WRITE_HIT = "Write Hit"
    WRITE_MISS = "Write Miss"
    CREATED_VPN_TO_PFN = "Created VPN to PFN mapping"
    PT_FULL = "Page Table Full"
    EVICT_SUCCESS = "Evict Success"
    EVICT_FAIL = "Evict Fail"
class CacheLogAction(str, Enum):
    ATTEMPT_READ = "Attempt Read"
    CONTINUE_LOWER = "Continue to Lower Cache"
    CREATE_VPN_TO_PFN = "Create VPN to PFN Mapping"
    TRY_PT_AGAIN = "Try Page Table Again"
    PT_EVICT = "Evict from Page Table"
class CacheLogItem():
    def __init__(self, action=None, addr=None, response=None, cache_type=None, result=None):
        self.addr = addr
        self.response = response
        self.cache_type = cache_type
        self.block = None
        self.log_type = None
        self.result = result
        self.action = action
    def print(self, indents=0):
        if self.action:
            print(f"\t" * indents + f"Action: {self.action}")
        print(f"\t" * indents + f"Address: {self.addr.addr_str}")
        print(f"\t" * indents + f"Response: {self.response}")
        print(f"\t" * indents + f"Cache Type: {self.cache_type}")
        if self.result:
            print(f"\t" * indents + f"Result: {self.result}")
class CacheLog():
    def __init__(self):
        self.log = []
    def add(self, item):
        self.log.append(item)
    def print(self):
        i=0
        for item in self.log:
            print(f"Log Item {i}")
            item.print(1)
            i+=1
            
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
    def evict_block(self):
        #Approximate LRU, make this better later
        #Just remove block at index 0
        num_blocks = len(self.blocks)
        new_blocks = self.blocks[1:]
        self.blocks = new_blocks
        num_blocks_new = len(self.blocks)
        if num_blocks_new == num_blocks - 1:
            return True
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
        elif self.cache_type == CacheType.PAGE_TABLE:
            self.pt_num_entries = (2**self.config.addr_len)*self.config.pt_page_size

            #Assume one set for page table
            self.set_size = self.pt_num_entries
            self.num_sets = 1
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
        elif self.cache_type == CacheType.PAGE_TABLE:
            #We should have one set, if not, except
            if len(self.sets) > 1:
                raise ValueError("Page table should have only one set")
            elif len(self.sets) == 0:
                #Setup the page table
                self.sets[0] = Set(self.set_size)
            print("Looking in page table for vpn: " + str(addr_bits.vpn))
            #We should have one set at this point
            for block in self.sets[0].blocks:
                if block.data.tag == addr_bits.vpn:
                    print("Found match with pfn: " + str(block.data.pfn))
                    return block.data.pfn
            #We didn't find the block, return None
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

        if self.cache_type == CacheType.PAGE_TABLE:
            which_set = self.add_get_set(0)
        else:
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

        self.cache_log = CacheLog()

    def read(self, read_addr_str):
        #Ensure the address is a valid hex string
        if not read_addr_str.startswith("0x"):
            raise ValueError("Address must be a hex string")
        #Create an Address object
        read_addr = Address(read_addr_str, is_virtual=True)

        #Are we using a TLB?
        if self.config.use_tlb == True:
            dtlb = self.mem_dtlb
            #Try to read the address from the TLB
            dtlb_read = dtlb.read(read_addr_str)
            print("DTLB read: ", dtlb_read)
            if dtlb_read is not None:
                pass
            else:
                log_result = CacheLogItem(action=CacheLogAction.ATTEMPT_READ, cache_type=CacheType.DTLB, addr=read_addr, response=CacheLogType.READ_MISS, result=CacheLogAction.CONTINUE_LOWER)
                self.cache_log.add(log_result)
                #Pass to the child
                page_table = dtlb.child
                #Try to read the address from the page table
                page_table_read = page_table.read(read_addr_str)
                print("Page table read: ", page_table_read, "given address: ", read_addr_str)
                if page_table_read is not None:
                    #Success! We found the physical address in the page table
                    log_result = CacheLogItem(action=CacheLogAction.ATTEMPT_READ, cache_type=CacheType.PAGE_TABLE, addr=read_addr, response=CacheLogType.READ_HIT, result=CacheLogAction.CONTINUE_LOWER)
                    self.cache_log.add(log_result)
                    #Translate the address
                    translated_addr = page_table.translate_addr(addr_to_translate=read_addr, pfn=page_table_read)
                    #We should update the TLB with the new entry
                    return translated_addr
                else:
                    #We didn't find the physical address in the page table. 
                    #We need to arbitrarily choose a PFN and add it to the page table
                    log_result = CacheLogItem(action=CacheLogAction.ATTEMPT_READ, cache_type=CacheType.PAGE_TABLE, addr=read_addr, response=CacheLogType.READ_MISS, result=CacheLogAction.CREATE_VPN_TO_PFN)
                    self.cache_log.add(log_result)

                    page_table_sets = page_table.sets
                    page_table_set = page_table_sets[0]
                    num_blocks_page_table = len(page_table_set.blocks)
                    if num_blocks_page_table == 0:
                        #No blocks in the set, so we must add one
                        #Since this is the first block, we can arbitrarily choose a PFN of 0
                        print("Setting up 0th PT PFN")
                        new_pfn = "0x0"
                        cur_vpn = read_addr.get_bits(self.config, CacheType.PAGE_TABLE).vpn

                        new_block = Block()
                        new_block.data.tag = cur_vpn
                        new_block.data.pfn = new_pfn
                        page_table_save = page_table.save(read_addr, new_block)
    

                        log_result = CacheLogItem(action=CacheLogAction.CREATE_VPN_TO_PFN, cache_type=CacheType.PAGE_TABLE, addr=read_addr, response=CacheLogType.CREATED_VPN_TO_PFN, result=CacheLogAction.TRY_PT_AGAIN)
                        self.cache_log.add(log_result)

                        #Update TLB
                        #dtlb.save(read_addr, new_block)
                        #Try the page table read again
                        page_table_read = page_table.read(read_addr_str)
                        print("New page table read: ", page_table_read)
                        #Currently, this is showing up as None, why?

                    elif num_blocks_page_table < self.config.pt_num_vpages:
                        #What is the most recently allocated PFN?
                        most_recent_pfn = page_table_set.blocks[-1].data.pfn
                        #Treat the hex string of format 0x0 as an integer
                        most_recent_pfn_int = int(most_recent_pfn, 16)
                        #Increment the integer
                        new_pfn_int = most_recent_pfn_int + 1
                        #Convert the integer to a hex string
                        new_pfn = str(hex(new_pfn_int))
                        cur_vpn = read_addr.get_bits(self.config, CacheType.PAGE_TABLE).vpn

                        new_block = Block()
                        new_block.data.tag = cur_vpn
                        new_block.data.pfn = new_pfn
                        page_table.save(read_addr, new_block)

                        log_result = CacheLogItem(action=CacheLogAction.CREATE_VPN_TO_PFN, cache_type=CacheType.PAGE_TABLE, addr=read_addr, response=CacheLogType.CREATED_VPN_TO_PFN, result=CacheLogAction.TRY_PT_AGAIN)
                        self.cache_log.add(log_result)

                        #Update TLB
                        dtlb.save(read_addr, new_block)

                        #Try the page table read again
                        page_table_read = page_table.read(read_addr_str)

                    else:
                        log_result = CacheLogItem(action=CacheLogAction.CREATE_VPN_TO_PFN, cache_type=CacheType.PAGE_TABLE, addr=read_addr, response=CacheLogType.PT_FULL, result=CacheLogAction.PT_EVICT)
                        self.cache_log.add(log_result)
                        #We need to evict a block from the page table
                        eviction_result = page_table_set.evict()
                        if eviction_result == True:
                            #Eviction succeeded
                            log_result = CacheLogItem(action=CacheLogAction.PT_EVICT, cache_type=CacheType.PAGE_TABLE, addr=read_addr, response=CacheLogType.EVICT_SUCCESS, result=CacheLogAction.TRY_PT_AGAIN)
                            self.cache_log.add(log_result)
                        else:
                            #Eviction failed
                            log_result = CacheLogItem(action=CacheLogAction.PT_EVICT, cache_type=CacheType.PAGE_TABLE, addr=read_addr, response=CacheLogType.EVICT_FAIL, result=CacheLogAction.TRY_PT_AGAIN)
                            self.cache_log.add(log_result)

                            raise ValueError("Eviction failed")
                if page_table_read is None:
                    #For some reason the page_table_read is still None. Fault.
                    raise ValueError("Page table read is still None")
                print("Page table read: ", page_table_read)
                        



                    
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

    
    # # Try to add an address to the TLB manually
    # #Add a virtual address to the TLB to play pretend
    # addr = Address("0xc84") 
    # block = Block()
    # #Act as if we've gotten a pfn from the page table already
    # block.data.pfn = "0x2"
    # #Set the tag to the tag from the address manually
    # block.data.tag = addr.get_bits(config, CacheType.DTLB).tag
    # #Add the block to the TLB
    # response = memhier.mem_dtlb.save(addr, block)
    # print("Save response:", response)

    
    # # Try to read the address from the TLB
    #Manually add an address to the Page Table
    # addr = Address("0xc84")
    # block = Block()
    # #Act as if we've gotten a pfn from the page table already
    # block.data.pfn = "0x2"
    # #Set the tag to the tag from the address manually
    # block.data.tag = addr.get_bits(config, CacheType.PAGE_TABLE).tag
    # #Add the block to the Page Table
    # response = memhier.mem_page_table.save(addr, block)
    # print("Manual Save response:", response)

    # test_read = memhier.read("0xc84")
    # test_read_2 = memhier.read("0xdead")

    memhier.read("0xc84")

    memhier.cache_log.print()

   


print("Cache.py loaded")
TestCache()
