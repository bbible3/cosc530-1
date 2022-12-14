
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
    EVICTING = "evicting"
class TLBResponse():
    def __init__(self, response_type, tlb_entry, extra_data=None):
        self.response_type = response_type
        self.tlb_entry = tlb_entry
        self.extra_data = extra_data
    def print(self, indents=-0):
        print("\t"*indents+"Cache Response: " + self.response_type + " " + self.tlb_entry.virtual_address.addr_str)
        if self.extra_data is not None:
            print("\tExtra Data: " + self.extra_data)

#An entry address in a TLB set
class TLBAddrEntry():
    def __init__(self, virtual_address = None, vpn = None, data = None, mapping=None):

        self.mapping = mapping        
        self.page_offset_str = -1
        self.index_str = -1
        self.tag_str = -1
        self.pfn = None
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
                    
                    self.responses.append(TLBResponse(TLBResponseType.EVICTING, via_entry, extra_data=entry.virtual_address.addr_str))

                    set.entries.remove(entry)
                    return True
                
    
    #Search the TLB for a given Address
    def locate_address(self, address=None, mapping=None):

        #Make a TLBEntry from the address
        entry = TLBAddrEntry(virtual_address=address, mapping=mapping)
        #Process it
        entry.process_virtual_address()
        
        if entry.index_str == -1:
            raise Exception("Address must be processed before it can be located")

        if mapping is None:
            raise Exception("Mapping must be specified")

        locate_addr_index = entry.index_str
        locate_addr_tag = entry.tag_str

        for set in self.sets:
            for entry in set.entries:
                if entry.index_str == locate_addr_index:
                    print("Found index match")
                    #Index matches, check tag
                    if entry.tag_str == locate_addr_tag:
                        print("Found tag match")
                        #Tag matches, we found it
                        return entry

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



def EntryGenerator(like, change_bits=None, change_by=None):
    #Get the information about the entry
    like_addr = like.virtual_address
    if like.index_str == -1:
        like.process_virtual_address()
    if change_bits == "tag":
        like_tag = like.tag_str
        like_tag_bin = "0b" + like_tag
        like_tag_int = int(like_tag_bin, 2)
        like_tag_int += change_by
        like_tag_bin = bin(like_tag_int)
        like_tag = like_tag_bin[2:]
    else:
        like_tag = like.tag_str
    if change_bits == "index":
        like_index = like.index_str
        like_index_bin = "0b" + like_index
        like_index_int = int(like_index_bin, 2)
        like_index_int += change_by
        like_index_bin = bin(like_index_int)
        like_index = like_index_bin[2:]
    else:
        like_index = like.index_str
    if change_bits == "offset":
        like_offset = like.page_offset_str
        like_offset_bin = "0b" + like_offset
        like_offset_int = int(like_offset_bin, 2)
        like_offset_int += change_by
        like_offset_bin = bin(like_offset_int)
        like_offset = like_offset_bin[2:]
    else:
        like_offset = like.page_offset_str
    n_like_tag = len(like_tag)
    n_like_index = len(like_index)
    n_like_offset = len(like_offset)

    new_tag = like_tag
    new_index = like_index
    new_offset = like_offset
    new_bin = "0b" + new_tag + new_index + new_offset
    new_hex = hex(int(new_bin, 2))
    print("New hex:", new_hex)
    return str(new_hex)


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
    mytlb_entry.pfn = "1000"
    mytlb_entry.process_virtual_address()
    mytlb.add_entry_to_tlb(mytlb_entry)

    for response in mytlb.responses:
        response.print(indents=1)

    # my_address = Address(addr_str="0x0c86", addr_type=AddressType.HEX)
    # mytlb_entry = TLBAddrEntry(my_address, mapping=tlb_mapping)
    # mytlb_entry.process_virtual_address()
    # print("Tag:", mytlb_entry.tag_str)
    # print("Index:", mytlb_entry.index_str)
    # mytlb.locate_address(address=my_address, mapping=tlb_mapping)


    #print("Trying to make an entry like 0x0c86 with incremented index")
    #EntryGenerator(mytlb_entry, change_bits="index", change_by=1)
    #0xd86
    new_hex = EntryGenerator(mytlb_entry, change_bits="offset", change_by=1)
    my_address = Address(addr_str=new_hex, addr_type=AddressType.HEX)
    print("Running a locate on the new address", new_hex)
    found_entry = mytlb.locate_address(address=my_address, mapping=tlb_mapping)
    if found_entry != None:
        print(found_entry.virtual_address.addr_str, "found in TLB")
        print(f"The tag is {found_entry.tag_str}, the index is {found_entry.index_str}, and the offset is {found_entry.page_offset_str}")
        #In a virtual address, everything that is not the offset is the VPN. The VPN is the tag and index combined.
        
        #Ensure that found_entry has a valid PFN
        if found_entry.pfn == None:
            raise Exception("PFN is None for found_entry=", found_entry.virtual_address.addr_str)
        physical_address = "0b" + found_entry.pfn + found_entry.page_offset_str
        print("Physical address:", hex(int(physical_address, 2)))

        test_address = Address(addr_str="0xc84", addr_type=AddressType.HEX)
        test_entry = TLBAddrEntry(test_address, mapping=tlb_mapping)
        test_entry.process_virtual_address()
        test_tag = test_entry.tag_str
        test_index = test_entry.index_str
        test_offset = test_entry.page_offset_str
        test_tag_int = int(test_tag, 2)
        test_index_int = int(test_index, 2)
        test_offset_int = int(test_offset, 2)
        print("Test tag:", hex(test_tag_int))
        print("Test index:", hex(test_index_int))
        print("Test offset:", hex(test_offset_int))
print("TLB Tester")
TLBTester()