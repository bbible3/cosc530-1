
import math
from enum import Enum
class AddressType(int, Enum):
    #Define if the address is hex, binary, or decimal
    HEX = 16
    BIN = 2
    DEC = 10
    NULLTYPE = 0

#This class represents a single address, able to be displayed in different formats
#Must define address as a string, type as an AddressType
#min_len specifies the minimum length of the address, in bits - if the address is shorter, it will be padded with zeros
class Address():
    def __init__(self, addr_str="0xFEEDBEEF", addr_type=AddressType.NULLTYPE, min_len=4):
        self.min_len = min_len
        if addr_str is not None and addr_type is not None:
            self.addr_str = addr_str
            self.addr_type = addr_type
            self.addr_int = int(addr_str, base=int(self.addr_type))

    #Return the address as a given type as specified by the AddressType enum
    def as_type(self, to_type):
        if to_type == AddressType.HEX:
            return hex(self.addr_int)
        elif to_type == AddressType.BIN:
            return bin(self.addr_int)
        elif to_type == AddressType.DEC:
            return str(self.addr_int)
    
    #Return the address as a string with proper formatting and separation
    def bin_formatted(self):
        my_bin = bin(self.addr_int)
        my_bin = my_bin[2:]

        if len(my_bin)%4 is not 0:
            #We need to pad the string with zeros
            my_bin = "0" * (4 - (len(my_bin)%4)) + my_bin
        
        #Pad if necessary
        if len(my_bin) < self.min_len:
            my_bin = "0" * (self.min_len - len(my_bin)) + my_bin
        
        #Split every 4
        my_bin = " ".join(my_bin[i:i+4] for i in range(0, len(my_bin), 4))
        return my_bin

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

    
        try:
            #Select the page offset
            start_range = len(virtual_address_bin) - self.mapping.page_offset_bits
            end_range = len(virtual_address_bin)
            self.page_offset_str = virtual_address_bin[start_range:end_range]
            #print("Page offset:", self.page_offset)
        except Exception as e:
            print("Could not select page offset bits:", e)
        try:
            index_end_range = len(virtual_address_bin) - self.mapping.page_offset_bits
            index_start_range = index_end_range - self.mapping.index_bits
            self.index_str = virtual_address_bin[index_start_range:index_end_range]
            #print("Index:", self.index)
        except Exception as e:
            print("Could not select index bits:", e)
        try:
            #Select the tag bits
            
            #How many bits are left?
            bits_left = len(virtual_address_bin) - self.mapping.page_offset_bits - self.mapping.index_bits
            #print("Bits left:", bits_left)
            if bits_left > 0:
                self.tag_str = str(int(virtual_address_bin[0:bits_left],2))
        except Exception as e:
            print("Could not select tag bits:", e)


        #Test lengths
        #print("Mapping:")
        #self.mapping.print_self()
        #print("Virtual address length:", len(virtual_address_bin))
        if len(self.page_offset_str) != self.mapping.page_offset_bits:
            raise Exception(f"Page offset bits are not the correct length. Expected {self.mapping.page_offset_bits}, got {len(self.page_offset_str)}")
        if len(self.index_str) != self.mapping.index_bits:
            raise Exception(f"Index bits are not the correct length. Expected {self.mapping.index_bits}, got {len(self.index_str)}")
        
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
       print(f"Offset bits: {self.page_offset_bits}, Index bits: {self.index_bits}, Tag bits: {self.tag_bits}")

#A TLB class, which stores TLB sets
class TLB():
    def __init__(self, page_size=-1, max_num_sets=-1):
        self.sets = []
        self.page_offset_bits = -1
        self.index_bits = -1
        self.tag_bits = -1
        self.max_num_sets = max_num_sets
        self.page_size = page_size
        self.mapping = TLBMapping()
    
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
                return True
            else:
                #THe set ight be full, can we add another set?
                if len(self.sets) < self.max_num_sets:
                    #Honestly not sure that TLB size should be page_size
                    #Create new set, append entry, add new set
                    new_set = TLBSet(self.page_size, mapping=self.mapping)
                    new_set.add_entry(entry)
                    self.add_set(new_set)
                    return True
                else:
                    #We can't add another set, so we can't add this entry
                    raise Exception("TLB is full")
                    return False
    
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

    #Init TLB
    mytlb = TLB(page_size = 512, max_num_sets = 64)
    #Setup mapping

    tlb_mapping = TLBMapping(page_offset_bits=9, index_bits=6)
    mytlb.mapping = tlb_mapping

    #Create an address t test
    new_address = Address(addr_str="0xABC1", addr_type=AddressType.HEX)
    print("new_address type:", new_address.addr_type)
    print("new_address value:", new_address.as_type(AddressType.HEX))
    print("new_address value:", new_address.as_type(AddressType.BIN))
    print("new_address as formatted binary:", new_address.bin_formatted())

    if len(mytlb.sets) is 0:
        #print("No sets in TLB")
        #Add one
        mytlb.add_set(TLBSet(set_size=1, mapping=tlb_mapping))
        #Make a TLB entry
        mytlb_entry = TLBAddrEntry(new_address, mapping=tlb_mapping)
        #Add the entry to the TLB
        mytlb.add_entry_to_tlb(mytlb_entry)

    #Output the TLB
    #mytlb.display_tlb()

    #Test the address
    # try_find = mytlb.locate_address(new_address)
    # if try_find is not None:
    #     print("Found address in TLB")
    #     print("Set:", try_find[0])
    #     print("Entry:", try_find[1])
    # else:
    #     print("Address not found in TLB")
    #Assuming we have only added one value, should ouput: Set 0 Entry 0

    #At this point, we expect to see Set 0 and Entry 0, "Found address in TLB"
    #Then, we search for it... set 0 entry 0

    #Add another address as an entry
    my_address2 = Address(addr_str="0x8FDF", addr_type=AddressType.HEX)
    mytlb_entry2 = TLBAddrEntry(my_address2, mapping=tlb_mapping)
    mytlb.add_entry_to_tlb(mytlb_entry2)

    mytlb.display_tlb()

    try_find = mytlb.locate_address(my_address2)
    if try_find is not None:
        print("Found address in TLB")
        print("Set:", try_find[0])
        print("Entry:", try_find[1])

    #What data do we have in try_find?
    if try_find[2]:
        found_entry = try_find[2]
        print("Found entry.")
        print("Virtual address:", found_entry.virtual_address.as_type(AddressType.HEX))
        print("As formatted binary:", found_entry.virtual_address.bin_formatted())
        #Try to process
        print("Trying to process entry...")
        found_entry.process_virtual_address()
        print("\tOffset:", found_entry.page_offset_str,"=", int(found_entry.page_offset_str,2))
        print("\tIndex:", found_entry.index_str, "=", int(found_entry.index_str,2))
        print("\tTag:", found_entry.tag_str, "=", int(found_entry.tag_str,2))


    #Try searching for a new entry
    my_address3 = Address(addr_str="0x8FDE", addr_type=AddressType.HEX)
    addr_entry = TLBAddrEntry(my_address3, mapping=tlb_mapping)
    #Required to populate object values
    addr_entry.process_virtual_address()
    mytlb.search_tlbaddr_entry(addr_entry)



print("TLB Tester")
TLBTester()