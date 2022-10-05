
import math
from enum import Enum
class AddressType(int, Enum):
    #Define if the address is hex, binary, or decimal
    HEX = 16
    BIN = 2
    DEC = 10
    NULLTYPE = 0
class Address():
    def __init__(self, addr_str="0xFEEDBEEF", addr_type=AddressType.NULLTYPE, min_len=4):
        self.min_len = min_len
        if addr_str is not None and addr_type is not None:
            self.addr_str = addr_str
            self.addr_type = addr_type
            self.addr_int = int(addr_str, base=int(self.addr_type))

    def as_type(self, to_type):
        if to_type == AddressType.HEX:
            return hex(self.addr_int)
        elif to_type == AddressType.BIN:
            return bin(self.addr_int)
        elif to_type == AddressType.DEC:
            return str(self.addr_int)

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

class TLBEntry():
    def __init__(self, virtual_address = None, vpn = None, data = None):
        
        if not isinstance(virtual_address, Address):
            raise Exception("virtual_address must be of type Address")
    
        if isinstance(vpn, str):
            vpn = int(vpn, 2)
        if isinstance(data, str):
            data = int(data, 2)

        if virtual_address:
            self.virtual_address = virtual_address
        if vpn is not None and data is not None:
            self.vpn = vpn
            self.data = data
        
        virtual_address_bin = bin(self.virtual_address.addr_int)[2:]
    

    def process_virtual_address(self, virtual_address):
        #Get the binary value of the virtual address
        virtual_address_bin = bin(virtual_address)[2:]

        try:
            #Select the page offset bits
            page_offset = virtual_address_bin[-self.page_offset_bits_len():]
        except Exception as e:
            print("Could not select page offset bits:", e)
        try:
            #Select the index bits
            index = virtual_address_bin[-(self.page_offset_bits_len() + self.index_bits_len()):]
        except Exception as e:
            print("Could not select index bits:", e)
        try:
            #Select the tag bits
            tag = virtual_address_bin[:-self.page_offset_bits() - self.index_bits()]
        except Exception as e:
            print("Could not select tag bits:", e)

        #Assert that we have all
        assert len(page_offset) == self.page_offset_bits_len() and len(index) == self.index_bits_len() and len(tag) == len(virtual_address_bin) - self.page_offset_bits_len() - self.index_bits_len(), "Error with virtual address sanity check"

        #Set the bits
        self.page_offset_bits = page_offset
        self.index_bits = index
        self.tag_bits = tag

    def print_address_mapping(self):
        print("Page offset bits:", self.page_offset_bits)
        print("Index bits:", self.index_bits)
        print("Tag bits:", self.tag_bits)


class TLBSet():
    def __init__(self, set_size=-1):
        self.entries = []
        self.set_size = set_size

    def add_entry(self, entry):
        if len(self.entries) < self.set_size:
            self.entries.append(entry)
            return True
        else:
            return False
            raise Exception("TLB set is full")
    def index_bits(self):
        return int(math.log2(len(self.entries)))
class TLB():
    def __init__(self, page_size=-1, max_num_sets=-1):
        self.sets = []
        self.page_offset_bits = -1
        self.index_bits = -1
        self.tag_bits = -1
        self.max_num_sets = max_num_sets

    def add_set(self, set):
        self.sets.append(set)
    def num_sets(self):
        return len(self.sets)
    def get_set(self, index):
        return self.sets[index]

    def add_entry_to_tlb(self, entry):
        for set in self.sets:
            if set.add_entry(entry):
                return True
            else:
                if len(self.sets) < self.max_num_sets:
                    new_set = TLBSet()
                    new_set.add_entry(entry)
                    self.add_set(new_set)
                    return True
                else:
                    raise Exception("TLB is full")
                    return False

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






def TLBTester():
    mytlb = TLB(page_size = 512, max_num_sets = 64)
    new_address = Address(addr_str="0xABC1", addr_type=AddressType.HEX)
    print("new_address type:", new_address.addr_type)
    print("new_address value:", new_address.as_type(AddressType.HEX))
    print("new_address value:", new_address.as_type(AddressType.BIN))
    print("new_address as formatted binary:", new_address.bin_formatted())

    if len(mytlb.sets) is 0:
        print("No sets in TLB")
        #Add one
        mytlb.add_set(TLBSet(set_size=1))
        #Make a TLB entry
        mytlb_entry = TLBEntry(new_address)
        #Add the entry to the TLB
        mytlb.add_entry_to_tlb(mytlb_entry)

    #Output the TLB
    mytlb.display_tlb()


print("TLB Tester")
TLBTester()