from enum import Enum
from config import Config
from address import Address, Mapping
from cachetype import CacheType

class CacheResult():
    def __init__(self, virtual_address_str=None, virtual_page_num_str=None, page_offset_str=None, tlb_tag_str=None, tlb_index_str=None, tlb_result_str=None, pt_result_str=None, pfn_str=None, dc_tag_str=None, dc_index_str=None, dc_result_str=None, l2_tag_str=None, l2_index_str=None, l2_result_str=None):
        self.virtual_address_str = virtual_address_str
        self.virtual_page_num_str = virtual_page_num_str
        self.page_offset_str = page_offset_str
        self.tlb_tag_str = tlb_tag_str
        self.tlb_index_str = tlb_index_str
        self.tlb_result_str = tlb_result_str
        self.pt_result_str = pt_result_str
        self.pfn_str = pfn_str
        self.dc_tag_str = dc_tag_str
        self.dc_index_str = dc_index_str
        self.dc_result_str = dc_result_str
        self.l2_tag_str = l2_tag_str
        self.l2_index_str = l2_index_str
        self.l2_result_str = l2_result_str

    def output(self):
        #"%08x %6x %4x %6x %3x %4s %4s %4x %6x %3x %4s %6x %3x %4s"

        #output_str = "{va_str:08x} {vpn_str:6x} {po_str:4x} {tlb_tag_str:6x} {tlb_index_str:3x} {tlb_result_str:4s} {pt_result_str:4s} {pfn_str:4x} {dc_tag_str:6x} {dc_index_str:3x} {dc_result_str:4s} {l2_tag_str:6x} {l2_index_str:3x} {l2_result_str:4s}"
        #formatted_str = output_str.format(va_str=self.virtual_address_str, vpn_str=self.virtual_page_num_str, po_str=self.page_offset_str, tlb_tag_str=self.tlb_tag_str, tlb_index_str=self.tlb_index_str, tlb_result_str=self.tlb_result_str, pt_result_str=self.pt_result_str, pfn_str=self.pfn_str, dc_tag_str=self.dc_tag_str, dc_index_str=self.dc_index_str, dc_result_str=self.dc_result_str, l2_tag_str=self.l2_tag_str, l2_index_str=self.l2_index_str, l2_result_str=self.l2_result_str)
        formatted_str = ""

        if self.virtual_address_str[:2] != "0x":
            raise ValueError("virtual_address_str must be in hex format")
    
        if self.pt_result_str == "IGNORE":
            self.pt_result_str = " "
        #formatted_str += self.virtual_address_str[2:].zfill(8)
        formatted_str = "{va_str:08x}".format(va_str=int(self.virtual_address_str, 16))
        formatted_str += " "
        formatted_str += "{vpn_str:6x}".format(vpn_str=int(self.virtual_page_num_str, 2))
        formatted_str += " "
        formatted_str += "{po_str:4x}".format(po_str=int(self.page_offset_str, 2))
        formatted_str += " "
        formatted_str += "{tlb_tag_str:6x}".format(tlb_tag_str=int(self.tlb_tag_str, 2))
        formatted_str += " "
        formatted_str += "{tlb_index_str:3x}".format(tlb_index_str=int(self.tlb_index_str, 2))
        formatted_str += " "
        formatted_str += "{tlb_result_str:4s}".format(tlb_result_str=self.tlb_result_str)
        formatted_str += " "
        formatted_str += "{pt_result_str:4s}".format(pt_result_str=self.pt_result_str)
        formatted_str += " "
        formatted_str += "{pfn_str:4x}".format(pfn_str=int(self.pfn_str, 16))
        formatted_str += " "
        formatted_str += "{dc_tag_str:6x}".format(dc_tag_str=int(self.dc_tag_str, 2))
        formatted_str += " "
        formatted_str += "{dc_index_str:3x}".format(dc_index_str=int(self.dc_index_str, 2))
        formatted_str += " "
        formatted_str += "{dc_result_str:4s}".format(dc_result_str=self.dc_result_str)
        formatted_str += " "
        formatted_str += "{l2_tag_str:6x}".format(l2_tag_str=int(self.l2_tag_str, 2))
        formatted_str += " "
        formatted_str += "{l2_index_str:3x}".format(l2_index_str=int(self.l2_index_str, 2))
        formatted_str += " "
        formatted_str += "{l2_result_str:4s}".format(l2_result_str=self.l2_result_str)

        return formatted_str
    def headers(self):

        header_line_1 = ["Virtual", "Virt.", "Page", "TLB", "TLB", "TLB", "PT", "Phys", "", "DC", "DC", "", "L2", "L2"]
        header_line_2 = ["Address", "Page #", "Off", "Tag", "Ind", "Res.", "Res.", "Pg #", "DC Tag", "Ind", "Res.", "L2 Tag", "Ind", "Res."]
        widths = [8, 6, 4, 6, 3, 4, 4, 4, 6, 3, 4, 6, 3, 4]
        
        line_1_str = ""
        line_2_str = ""
        for i in range(len(header_line_1)):
            line_1_str += header_line_1[i].ljust(widths[i])
            line_1_str += " "
            line_2_str += header_line_2[i].ljust(widths[i])
            line_2_str += " "
        print(line_1_str)
        print(line_2_str)
        bar_str = ""
        for num in widths:
            bar_str += "-" * num
            bar_str += " "
        print(bar_str)
        return True
class CacheLogType(str, Enum):
    READ_HIT = "Read Hit"
    READ_MISS = "Read Miss"
    WRITE_HIT = "Write Hit"
    WRITE_MISS = "Write Miss"
    CREATED_VPN_TO_PFN = "Created VPN to PFN mapping"
    PT_FULL = "Page Table Full"
    EVICT_SUCCESS = "Evict Success"
    EVICT_FAIL = "Evict Fail"
    UPDATED_PT = "Updated Page Table"
    UPDATED_TLB = "Updated TLB"
class CacheLogAction(str, Enum):
    ATTEMPT_READ = "Attempt Read"
    CONTINUE_LOWER = "Continue to Lower Cache"
    CREATE_VPN_TO_PFN = "Create VPN to PFN Mapping"
    TRY_PT_AGAIN = "Try Page Table Again"
    PT_EVICT = "Evict from Page Table"
    RESTART_READ = "Restart Read"
    SUCCESS = "Success"
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
            #print("Looking in page table for vpn: " + str(addr_bits.vpn))
            #We should have one set at this point
            for block in self.sets[0].blocks:
                if block.data.tag == addr_bits.vpn:
                    #print("Found match with pfn: " + str(block.data.pfn))
                    return block.data.pfn
            #We didn't find the block, return None
            return None
            
        else:
            #Is there a set at that index?
            if index in self.sets:
                for block in self.sets[index].blocks:
                    if block.data.tag == addr_bits.tag:
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
        self.cache_result = None
    def read_sub_tlb(self, read_addr_str=None, read_addr=None, cache_result=None):
        #To segment the code properly to make it easier to read, this contains the code previously under the branch
        #if self.config.use_tlb == True.
        #If any of the parameters are None, raise an error
        if read_addr_str == None:
            raise ValueError("read_addr_str must be provided")
        if read_addr == None:
            raise ValueError("read_addr must be provided")
        if cache_result == None:
            raise ValueError("cache_result must be provided")
        if self.config.use_tlb == True:
            dtlb = self.mem_dtlb
            #Try to read the address from the TLB
            dtlb_read = dtlb.read(read_addr_str)
            #print("DTLB read: ", dtlb_read)
            if dtlb_read is not None:
                translated_addr = self.read_sub_dtlb_hit(read_addr_str=read_addr_str, read_addr=read_addr, cache_result=cache_result, dtlb=dtlb, dtlb_read=dtlb_read)
                if self.cache_result.tlb_result_str != "miss":
                    self.cache_result.tlb_result_str = "hit"
                    #If we have a TLB hit, we don't have to look at the PT.
                    self.cache_result.pt_result_str = "IGNORE"
                return translated_addr
                
            else:
                log_result = CacheLogItem(action=CacheLogAction.ATTEMPT_READ, cache_type=CacheType.DTLB, addr=read_addr, response=CacheLogType.READ_MISS, result=CacheLogAction.CONTINUE_LOWER)
                self.cache_log.add(log_result)
                #Pass to the child
                page_table = dtlb.child
                #Try to read the address from the page table
                page_table_read = page_table.read(read_addr_str)
                #print("Page table read: ", page_table_read, "given address: ", read_addr_str)
                if page_table_read is not None:
                    translated_addr = self.read_sub_page_table_hit(read_addr_str=read_addr_str, read_addr=read_addr, cache_result=cache_result, page_table=page_table, page_table_read=page_table_read, dtlb=dtlb)
                    self.cache_result.pt_result_str = "hit"
                    self.cache_result.pfn_str = page_table_read
                    return translated_addr
                else:
                    self.read_sub_dtlb_miss(read_addr_str=read_addr_str, read_addr=read_addr, cache_result=cache_result, dtlb=dtlb, page_table=page_table)
                    self.cache_result.pt_result_str = "miss"
                    self.cache_result.tlb_result_str = "miss"

                    

    def read_sub_dtlb_hit(self, read_addr_str=None, read_addr=None, cache_result=None, dtlb=None, dtlb_read = None):
        #If any of the parameters are None, except
        if read_addr_str == None:
            raise ValueError("read_addr_str cannot be None")
        if read_addr == None:
            raise ValueError("read_addr cannot be None")
        if cache_result == None:
            raise ValueError("cache_result cannot be None")
        if dtlb == None:
            raise ValueError("dtlb cannot be None")
        if dtlb_read == None:
            raise ValueError("read_sub_tlb tried to call dtlb_read, but dtlb_read was None")
        #print ("DTLB hit")
        #We found the address in the TLB, translate the address
        translated_addr = dtlb.translate_addr(addr_to_translate=read_addr, pfn=dtlb_read)
        #print("Translated address: " + str(translated_addr))

        log_result = CacheLogItem(action=CacheLogAction.ATTEMPT_READ, cache_type=CacheType.DTLB, addr=read_addr, response=CacheLogType.READ_HIT, result=CacheLogAction.SUCCESS)
        self.cache_log.add(log_result)

        #Given this translated address, get the DC tag
        dc_addr = translated_addr.get_bits(self.config, CacheType.DCACHE)
        l2_addr = translated_addr.get_bits(self.config, CacheType.L2)


        #This is necessary to ensure that the cache_result is updated properly.
        #A DTLB hit must occur for output to be proper.
        #Maybe we can change this, but if DTLB is disabled maybe just hide output? lol
        cache_result.pfn_str = dtlb_read
        cache_result.dc_tag_str = dc_addr.tag
        cache_result.dc_index_str = dc_addr.index
        cache_result.l2_tag_str = l2_addr.tag
        cache_result.l2_index_str = l2_addr.index
        self.cache_result = cache_result
        #Pass this to recursive function for other levels!
        #Essentially, say on a read we have a TLB miss followed by a PT miss,
        #We want to keep the same cache result even if we have to recursively restart the memhier read
        #So pass this object to the recursive function.
        #We can do this to properly fill out the result_strs.
        #Once that is done, it's mostly troubleshooting!
        #Also note that in the writeup PDF, TLB Res for that first read is a miss.
        #Blank if it should be skipped. See Abram's message
        return translated_addr      
    def read_sub_dtlb_miss(self, read_addr_str=None, read_addr=None, cache_result=None, dtlb=None, dtlb_read = None, page_table=None):
        if page_table == None:
            raise ValueError("read_sub_tlb_miss tried to call page_table, but page_table was None")
        
        #We didn't find the physical address in the page table. 
        #We need to arbitrarily choose a PFN and add it to the page table
        log_result = CacheLogItem(action=CacheLogAction.ATTEMPT_READ, cache_type=CacheType.PAGE_TABLE, addr=read_addr, response=CacheLogType.READ_MISS, result=CacheLogAction.CREATE_VPN_TO_PFN)
        self.cache_log.add(log_result)

        self.read_sub_page_table_miss(read_addr_str=read_addr_str, read_addr=read_addr, cache_result=cache_result, page_table=page_table, dtlb=dtlb)

    def read_sub_page_table_miss(self, read_addr_str=None, read_addr=None, cache_result=None, page_table=None, dtlb=None):
        if read_addr_str == None:
            raise ValueError("read_addr_str cannot be None")
        if read_addr == None:
            raise ValueError("read_addr cannot be None")
        if cache_result == None:
            raise ValueError("cache_result cannot be None")
        if page_table == None:
            raise ValueError("page_table cannot be None")
            
        page_table_sets = page_table.sets
        page_table_set = page_table_sets[0]
        num_blocks_page_table = len(page_table_set.blocks)
        if num_blocks_page_table == 0:
            #No blocks in the set, so we must add one
            #Since this is the first block, we can arbitrarily choose a PFN of 0

            new_pfn = "0x0"
            cur_vpn = read_addr.get_bits(self.config, CacheType.PAGE_TABLE).vpn

            new_block = Block()
            new_block.data.tag = cur_vpn
            new_block.data.pfn = new_pfn
            
            page_table_save = page_table.save(read_addr, new_block)


            log_result = CacheLogItem(action=CacheLogAction.CREATE_VPN_TO_PFN, cache_type=CacheType.PAGE_TABLE, addr=read_addr, response=CacheLogType.UPDATED_PT, result=CacheLogAction.RESTART_READ)
            self.cache_log.add(log_result)

            #Update TLB
            cur_index = read_addr.get_bits(self.config, CacheType.DTLB).index
            cur_tag = read_addr.get_bits(self.config, CacheType.DTLB).tag

            dtlb_block = Block()
            dtlb_block.data.tag = cur_tag
            dtlb_block.data.pfn = new_pfn
            dtlb_block.data.index = cur_index
            dtlb.save(read_addr, dtlb_block)

            log_result = CacheLogItem(action=CacheLogAction.CREATE_VPN_TO_PFN, cache_type=CacheType.PAGE_TABLE, addr=read_addr, response=CacheLogType.UPDATED_TLB, result=CacheLogAction.RESTART_READ)
            self.cache_log.add(log_result)

            #Set the cache result to miss for PT
            cache_result.pt_result_str = "miss"
            #Restart the read
            self.read(read_addr_str)
            

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

            #This means the Page Table was a miss. Update the cache_result to "miss" to reflect this
            cache_result.pt_result_str = "miss"
            page_table.save(read_addr, new_block)

            log_result = CacheLogItem(action=CacheLogAction.CREATE_VPN_TO_PFN, cache_type=CacheType.PAGE_TABLE, addr=read_addr, response=CacheLogType.CREATED_VPN_TO_PFN, result=CacheLogAction.TRY_PT_AGAIN)
            self.cache_log.add(log_result)

            
            #Update TLB
            cur_index = read_addr.get_bits(self.config, CacheType.DTLB).index
            cur_tag = read_addr.get_bits(self.config, CacheType.DTLB).tag

            dtlb_block = Block()
            dtlb_block.data.tag = cur_tag
            dtlb_block.data.pfn = new_pfn
            dtlb_block.data.index = cur_index
            dtlb.save(read_addr, dtlb_block)
            log_result = CacheLogItem(action=CacheLogAction.CREATE_VPN_TO_PFN, cache_type=CacheType.PAGE_TABLE, addr=read_addr, response=CacheLogType.UPDATED_TLB, result=CacheLogAction.RESTART_READ)
            self.cache_log.add(log_result)

            #Restart the read
            self.read(read_addr_str)


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

    def read_sub_page_table_hit(self, read_addr_str=None, read_addr=None, cache_result=None, page_table=None, dtlb=None, page_table_read=None):
        if read_addr_str == None:
            raise ValueError("read_addr_str cannot be None")
        if read_addr == None:
            raise ValueError("read_addr cannot be None")
        if cache_result == None:
            raise ValueError("cache_result cannot be None")
        if page_table == None:
            raise ValueError("page_table cannot be None")
        if dtlb == None:
            raise ValueError("dtlb cannot be None")
        if page_table_read == None:
            raise ValueError("page_table_read cannot be None")
        
        #Success! We found the physical address in the page table
        log_result = CacheLogItem(action=CacheLogAction.ATTEMPT_READ, cache_type=CacheType.PAGE_TABLE, addr=read_addr, response=CacheLogType.READ_HIT, result=CacheLogAction.CONTINUE_LOWER)
        self.cache_log.add(log_result)
        #Translate the address
        translated_addr = page_table.translate_addr(addr_to_translate=read_addr, pfn=page_table_read)
        #If PT_res is not already miss, update it to hit
        if self.cache_result.pt_result_str != "miss":
            self.cache_result.pt_result_str = "hit"
        #If dc_tag is not already set, update it
        if self.cache_result.dc_tag_str == "-1":
            self.cache_result.dc_tag_str = translated_addr.get_bits(self.config, CacheType.DCACHE).tag
        if self.cache_result.dc_index_str == "-1":
            self.cache_result.dc_index_str = translated_addr.get_bits(self.config, CacheType.DCACHE).index
        if self.cache_result.l2_tag_str == "-1":
            self.cache_result.l2_tag_str = translated_addr.get_bits(self.config, CacheType.L2).tag
        if self.cache_result.l2_index_str == "-1":
            self.cache_result.l2_index_str = translated_addr.get_bits(self.config, CacheType.L2).index
        
        #We should update the TLB with the new entry
        return translated_addr


    def read_sub_dc(self, read_addr_str=None, read_addr=None, cache_result=None):
        if read_addr_str == None:
            raise ValueError("read_addr_str cannot be None")
        if read_addr == None:
            raise ValueError("read_addr cannot be None")
        if cache_result == None:
            raise ValueError("cache_result cannot be None")
        
        #Attempt to read from the data cache
        dc_read = self.mem_dcache.read(read_addr_str)
        if dc_read == None:
            #Read miss
            #Do we continue to L2 or just do nothing?
            #Do we just store it into cache? Or write-policy?
            self.cache_result.dc_result_str = "miss"
            #Log the miss
            log_result = CacheLogItem(action=CacheLogAction.ATTEMPT_READ, cache_type=CacheType.DCACHE, addr=read_addr, response=CacheLogType.READ_MISS, result=CacheLogAction.CONTINUE_LOWER)
            self.cache_log.add(log_result)
            return False
        else:
            #Read hit
            self.cache_result.dc_result_str = "hit"
            #Log the hit
            log_result = CacheLogItem(action=CacheLogAction.ATTEMPT_READ, cache_type=CacheType.DCACHE, addr=read_addr, response=CacheLogType.READ_HIT, result=CacheLogAction.SUCCESS)
            self.cache_log.add(log_result)
            return dc_read
    def read_sub_l2(self, read_addr_str=None, read_addr=None, cache_result=None):
        if read_addr_str == None:
            raise ValueError("read_addr_str cannot be None")
        if read_addr == None:
            raise ValueError("read_addr cannot be None")
        if cache_result == None:
            raise ValueError("cache_result cannot be None")
        
        #Attempt to read from L2
        l2_read = self.mem_l2.read(read_addr_str)
        if l2_read == None:
            #Read miss
            self.cache_result.l2_result_str = "miss"
            #Log the miss
            log_result = CacheLogItem(action=CacheLogAction.ATTEMPT_READ, cache_type=CacheType.L2, addr=read_addr, response=CacheLogType.READ_MISS, result=CacheLogAction.CONTINUE_LOWER)
            self.cache_log.add(log_result)

            #Save to L2
            #Get bits from read_addr
            get_bits = read_addr.get_bits(self.config, CacheType.L2)
            l2_block = Block()
            l2_block.data.tag = get_bits.tag
            l2_block.data.index = get_bits.index
            l2_block.data.offset = get_bits.offset
            l2_save = self.mem_l2.save(read_addr, l2_block)


            return False
        else:
            #Read hit
            #To avoid wrong long on restart
            if self.cache_result.l2_result_str != "miss":
                self.cache_result.l2_result_str = "hit"
            #Log the hit
            log_result = CacheLogItem(action=CacheLogAction.ATTEMPT_READ, cache_type=CacheType.L2, addr=read_addr, response=CacheLogType.READ_HIT, result=CacheLogAction.SUCCESS)
            self.cache_log.add(log_result)
            return l2_read
    def read(self, read_addr_str):
        #print("Starting read of address: " + read_addr_str)
        #Ensure the address is a valid hex string
        if not read_addr_str.startswith("0x"):
            raise ValueError("Address must be a hex string")
        #Create an Address object
        read_addr = Address(read_addr_str, is_virtual=True)
        #Create a CacheResult to log
        cache_result = CacheResult()
        cache_result.virtual_address_str = read_addr_str
        cache_result.virtual_page_num_str = read_addr.get_bits(self.config, CacheType.DTLB).vpn
        cache_result.page_offset_str = read_addr.get_bits(self.config, CacheType.DTLB).offset
        cache_result.tlb_tag_str = read_addr.get_bits(self.config, CacheType.DTLB).tag
        cache_result.tlb_index_str = read_addr.get_bits(self.config, CacheType.DTLB).index
        cache_result.tlb_result_str = "notset"
        cache_result.pt_result_str = "notset"
        cache_result.pfn_str = "-1"
        cache_result.dc_tag_str = "-1"
        cache_result.dc_index_str = "-1"
        cache_result.dc_result_str = "-1"
        cache_result.l2_tag_str = "-1"
        cache_result.l2_index_str = "-1"
        cache_result.l2_result_str = "-1"
        self.cache_result = cache_result

        #Are we using a TLB?
        if self.config.use_tlb:
            self.read_sub_tlb(read_addr_str=read_addr_str, read_addr=read_addr, cache_result=cache_result)
        
        #Are we using DC? Always, yes
        sub_dc_result = self.read_sub_dc(read_addr_str=read_addr_str, read_addr=read_addr, cache_result=cache_result)
        if sub_dc_result == False:
            #Read miss
            #Attempt to read from L2
            self.read_sub_l2(read_addr_str=read_addr_str, read_addr=read_addr, cache_result=cache_result)
                    
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

    #memhier.cache_log.print()

    cache_result = memhier.cache_result
    cache_result.headers()
    print(cache_result.output())
    
    memhier.read("0x81c")
    cache_result = memhier.cache_result
    print(cache_result.output())
   


print("Cache.py loaded")
TestCache()
