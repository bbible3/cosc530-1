
import math
from enum import Enum
from addresshelper import AddressType, Address
from configs import ConfigFile

class TLBResponseType(str, Enum):
    ADD_SUCCESS = "add_success"
    CANNOT_ADD_TO_SET = "cannot_add_to_set"
    ADD_FAILED = "add_failed"

    EVICT_SUCCESS = "evict_success"
    EVICT_FAILED = "evict_failed"
class TLBResponse():
    def __init__(self, response_type, tlb_entry):
        self.response_type = response_type
        self.tlb_entry = tlb_entry
    def print(self, indents=-0):
        print("\t"*indents+"Cache Response: " + self.response_type + " " + self.tlb_entry.virtual_address.addr_str)

#An entry address in a TLB set
class TLBAddrEntry():
    def __init__(self, virtual_address = None, vpn = None, data = None, mapping=None):

        self.mapping = mapping        
        self.page_offset_str = -1
        self.index_str = -1
        self.tag_str = -1
        #If our virtual_address is invalid, except
        if not isinstance(virtual_address, Address):
            raise Exception("virtual_address must be of type Address")
        if not isinstance(mapping, TLBMapping):
            raise Exception("mapping must be of type TLBMapping")
        #Convert VPN and data if we're given it

        if isinstance(vpn, str):
            vpn = int(vpn, 2)
        if isinstance(data, str):
            data = int(data, 2)
        
        #Set the virtual address
        if virtual_address:
            self.virtual_address = virtual_address
        
        #Set the VPN and data if we have it
        if vpn is not None and data is not None:
            self.vpn = vpn
            self.data = data
        
        self.virtual_address_bin = bin(self.virtual_address.addr_int)[2:]
    #Returns a string assuming that the self.value is binary
    #This used to snip off the leading 0b but right now it doesnt

    def index_offset_str(self):
        return str(self.index)
    def tag_bits(self):
        return len(self.tag)
    #Call this function to calculate the VPN and data from the virtual address
    def process_virtual_address(self):
        #Get the binary value of the virtual address
        virtual_address_bin = self.virtual_address.as_type(AddressType.BIN)[2:]
        
        #We may need to change this
        addr_len = 32

        #Pad if necessary
        if len(virtual_address_bin) < addr_len:
            virtual_address_bin = "0" * (addr_len - len(virtual_address_bin)) + virtual_address_bin

        #0xc84 = 1100 1000 0100
        n_offset_bits = self.mapping.page_offset_bits
        n_index_bits = self.mapping.index_bits
        n_tag_bits = addr_len - n_offset_bits - n_index_bits
        
        offset_end = addr_len
        offset_start = offset_end - n_offset_bits
        index_end = offset_start
        index_start = index_end - n_index_bits
        tag_end = index_start
        tag_start = tag_end - n_tag_bits

        tag_bits = virtual_address_bin[tag_start:tag_end]
        index_bits = virtual_address_bin[index_start:index_end]
        offset_bits = virtual_address_bin[offset_start:offset_end]

        self.tag_str = tag_bits
        self.page_offset_str = offset_bits
        self.index_str = index_bits

        
#These are stored in the TLB Sets
class TLBEntry():
    def __init__(self, index=None, page_num=None, tag=None, valid=False, addr_entry=None):
        self.index = index
        self.page_num = page_num
        self.tag = tag
        self.valid = valid
        self.dirty = False
        self.used = False
        self.data = None
        self.mapping = None
        self.addr_entry = addr_entry



#A set in a TLB, must have a specified set_size
class TLBSet():
    def __init__(self, set_size=-1, mapping=None):
        self.entries = []
        self.set_size = set_size
        self.mapping = mapping

        if set_size == -1:
            raise Exception("Set size must be specified")
        if mapping is None:
            raise Exception("Mapping must be specified")

    #Add an entry to this TLB set
    def add_entry(self, entry):
        #If there's room, add it
        if len(self.entries) < self.set_size:
            self.entries.append(entry)
            return True
        else:
            #TLB Set Is Full
            return False
    #Return the number of bits required to index this set
    def index_bits(self):
        return int(math.log2(len(self.entries)))

#Store the TLB address mapping
class TLBMapping():
    def __init__(self, virtual_address=None, physical_address=None,  page_offset_bits=None, index_bits=None, tag_bits=None):
        self.virtual_address = virtual_address
        self.physical_address = physical_address
        self.page_offset_bits = page_offset_bits
        self.index_bits = index_bits
        self.tag_bits = tag_bits
    def print_self(self):
       print(f"Tag bits: {self.tag_bits} Offset bits: {self.page_offset_bits} Index bits: {self.index_bits}")

#A TLB class, which stores TLB sets
class TLB():
    def __init__(self, page_size=-1, max_num_sets=-1, max_set_size=-1):
        self.sets = []
        self.page_offset_bits = -1
        self.index_bits = -1
        self.tag_bits = -1
        self.max_num_sets = max_num_sets
        self.max_set_size = max_set_size
        self.page_size = page_size
        self.mapping = TLBMapping()
        self.responses = []

        #Set up sets
        if max_num_sets == -1:
            raise Exception("Max number of sets must be specified")
        for i in range(max_num_sets):
            self.sets.append(TLBSet(set_size=self.max_set_size, mapping=self.mapping))
    
    #Manually add a set to the TLB
    def add_set(self, set):
        self.sets.append(set)
    #Get the number of sets in the TLB
    def num_sets(self):
        return len(self.sets)
    #Get a set by index
    def get_set(self, index):
        return self.sets[index]
    
    #Try to add an Entry to the TLB.
    def add_entry_to_tlb(self, entry):
        for set in self.sets:
            #This will return true if it was added
            if set.add_entry(entry):
                self.responses.append(TLBResponse(TLBResponseType.ADD_SUCCESS, entry))
                return True
        #We can't add another set, so we can't add this entry.
        #Need to evict something
        if self.evict(entry):
            self.responses.append(TLBResponse(TLBResponseType.EVICT_SUCCESS, entry))
            #This is recursive and scary
            return self.add_entry_to_tlb(entry)
        #raise Exception("TLB is full")
        return False
    
    #Evict an entry from the TLB
    def evict(self, via_entry):
        for set in self.sets:
            for entry in set.entries:
                #If the entry hasn't been set up, ignore it
                if entry.index_str == -1:
                    continue
                
                #Do these entries have the same index bit?
                if entry.index_str == via_entry.index_str:
                    #If so, evict it
                    #print(f"Match found, evicting {entry.index_str} to add {via_entry.index_str}")
                    #print(f"Address {entry.virtual_address.addr_str} evicted for {via_entry.virtual_address.addr_str}")
                    set.entries.remove(entry)
                    return True
                
    
    #Search the TLB for a given Address
    def locate_address(self, address):
        #Is the address a valid address?
        if not isinstance(address, Address):
            raise Exception("Address must be of type Address")
        
        #Try the address in the TLB, if it exists return it in (set, entry_index, TLBEntry) format
        for i,set in enumerate(self.sets):
            for j,entry in enumerate(set.entries):
                if entry.virtual_address == address:
                    return (i, j, entry)
        return None

    def display_tlb(self):
        for set in self.sets:
            print("Set:", self.sets.index(set))
            for entry in set.entries:
                print("\tEntry:", set.entries.index(entry))
                print("\t\tVirtual address:", entry.virtual_address)


    
    
    def page_offset_bits_len(self):
        return int(math.log2(self.page_size))
    def index_bits_len(self):
        return int(math.log2(len(self.table)))

    #This function checks to see if a match is found in the TLB.
    def search_tlbaddr_entry(self, entry):
        for set in self.sets:
            for tlb_entry in set.entries:
                if tlb_entry.index_str == entry.index_str:
                    print("Found entry that matches", entry.virtual_address.as_type(AddressType.HEX))
                    print("\tTLB Entry:", tlb_entry.index_str)
                    print("\tOffset:", tlb_entry.page_offset_str)
                    print("Address:", tlb_entry.virtual_address.as_type(AddressType.HEX))
                    return tlb_entry
        return None





#Tester Class#
##############
def TLBTester():
    myConfig = ConfigFile("./memhier/trace.config")
    myConfig.load_file()
    myConfig.parse_lines()
    myConfig.process_config()


    print("Num configs = ", len(myConfig.configs))

    #Get values from config
    config_page_size = myConfig.configs['Page Table '].page_size
   


    config_set_size = myConfig.configs['Data TLB '].set_size
    config_num_sets = myConfig.configs['Data TLB '].num_sets

    config_page_table_index_bits = myConfig.page_table_index_bits
    config_page_table_offset_bits = myConfig.page_table_offset_bits
    config_tlb_index_bits = myConfig.tlb_bits

    print("Page table offset bits:", config_page_table_offset_bits)
    print("TLB index bits:", config_tlb_index_bits)
 
    #Init TLB
    mytlb = TLB(page_size = config_page_size, max_num_sets = config_num_sets, max_set_size = config_set_size)
    #Setup mapping

    tlb_mapping = TLBMapping(page_offset_bits=config_page_table_offset_bits, index_bits=config_tlb_index_bits)
    mytlb.mapping = tlb_mapping


    my_address = Address(addr_str="0x0c84", addr_type=AddressType.HEX)
    mytlb_entry = TLBAddrEntry(my_address, mapping=tlb_mapping)
    mytlb_entry.process_virtual_address()
    mytlb.add_entry_to_tlb(mytlb_entry)

    my_address = Address(addr_str="0x0c85", addr_type=AddressType.HEX)
    mytlb_entry = TLBAddrEntry(my_address, mapping=tlb_mapping)
    mytlb_entry.process_virtual_address()
    mytlb.add_entry_to_tlb(mytlb_entry)

    my_address = Address(addr_str="0x0c86", addr_type=AddressType.HEX)
    mytlb_entry = TLBAddrEntry(my_address, mapping=tlb_mapping)
    mytlb_entry.process_virtual_address()
    mytlb.add_entry_to_tlb(mytlb_entry)

    for response in mytlb.responses:
        response.print(indents=1)

  

print("TLB Tester")
TLBTester()