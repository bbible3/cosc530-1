import math
from re import S
from byter import Byter, Units

class PTE:
    def __init__(self, index=0, use_bit=0, dirty_bit=0, resident_bit=0, pfn=0, protection_bit=0, disk_address=0):
        self.index = index
        self.use_bit = use_bit
        self.dirty_bit = dirty_bit
        self.resident_bit = resident_bit
        self.pfn = pfn
        self.protection_bit = protection_bit
        self.disk_address = disk_address
class PageTable:
    def __init__(self, virtual_address_size=32, page_size=4096, pte_size=4, parent_config_file=None):
        #The length of the virtual address in bits
        self.virtual_address_size = virtual_address_size
        #The size of a page in bytes
        self.page_size = page_size
        #The size of a page table entry in bytes
        self.pte_size = pte_size

        self.num_entries = 2**(self.virtual_address_size - int(math.log2(self.page_size)))
        self.num_entires_log2 = int(math.log2(self.num_entries))

        #The page table in bytes
        self.total_size = self.num_entries * self.pte_size

        #Initialise the table to be zeroed out
        self.table = [] * self.num_entries

        #The parent config file
        self.parent_config_file = parent_config_file

        self.pt_offset_bits = -1
        self.pt_index_bits = -1

        #If the parent config file is not None, use it to set up the page table
        if self.parent_config_file != None:
            #I am not sure this part is correct...
            self.virtual_address_size = self.parent_config_file.virtual_address_len
            #print("RFC Virtual address size:", self.virtual_address_size, "bits")

            self.page_size = self.parent_config_file.page_size
            #print("RFC Page size:", Byter(self.page_size).as_string(Units.B))

            self.pte_size = self.parent_config_file.pte_size()
            #print("RFC PTE size:", self.pte_size, "bits")

            self.pt_index_bits = self.parent_config_file.page_table_index_bits
            #print("RFC Page table index bits:", self.pt_index_bits)
            self.pt_offset_bits = self.parent_config_file.page_table_offset_bits
            #print("RFC Page table offset bits:", self.pt_offset_bits)

            self.num_entries = 2**(self.virtual_address_size - int(math.log2(self.page_size)))
            self.num_entires_log2 = int(math.log2(self.num_entries))
            #print("RFC Number of entries:", self.num_entries)
            #print("RFC Number of entries log2:", self.num_entires_log2)

            self.total_size = self.num_entries * self.pte_size
            #print("RFC Total size:", Byter(self.total_size).as_string(Units.B))



    def create_entry(self, index, use_bit, dirty_bit, resident_bit, pfn, protection_bit, disk_address):
        #Create a page table entry
        return PTE(index, use_bit, dirty_bit, resident_bit, pfn, protection_bit, disk_address)
    def add_entry(self, pte):
        self.table.append(pte)

    def get_entry(self, vpn):
        #Get a page table entry from the page table
        #return self.table[vpn]
        for item in self.table:
            if item.index == vpn:
                return item
        return None
    def non_zero_entries(self):
        #Return the number of non-zero entries in the page table
        return len([x for x in self.table if x != 0])

    def addr_as_binary_str(self, virtual_address, separate=True, fill_z=False):
        if fill_z:
            virtual_address_binary = bin(virtual_address)[2:].zfill(self.virtual_address_size)
        else:
            virtual_address_binary = bin(virtual_address)[2:]
        virtual_address_binary_str = str(virtual_address_binary)
        if separate:
            #Can we evenly separate this into 4-bit chunks?
            if self.virtual_address_size % 4 == 0:
                virtual_address_binary_str = " ".join(virtual_address_binary_str[i:i+4] for i in range(0, len(virtual_address_binary_str), 4))
            else:
                offset = self.virtual_address_size % 4
                #Pad the string with that many zeros
                virtual_address_binary_str = "0" * offset + virtual_address_binary_str
                virtual_address_binary_str = " ".join(virtual_address_binary_str[i:i+4] for i in range(0, len(virtual_address_binary_str), 4))


        return virtual_address_binary_str

    def process_virtual_address(self, virtual_address):
        virtual_address_binary_str = self.addr_as_binary_str(virtual_address)
        #print("Virtual address:", virtual_address_binary_str, "(", hex(virtual_address), ")")
       # print("Dirbin:", bin(0x8fdf))
        #Process a virtual address and return the VPN and offset
        offset = virtual_address & (self.page_size - 1)
        vpn = virtual_address >> int(math.log2(self.page_size))
        index = vpn & ((1 << self.pt_index_bits) - 1)
        tag = vpn >> self.pt_index_bits

        # print("Offset:", self.addr_as_binary_str(offset))
        # print("VPN:", vpn)
        # print("VPN binary:", self.addr_as_binary_str(vpn, separate=False))
        # print("Index:", index)
        # print("Index binary:", self.addr_as_binary_str(index, separate=False))
        # print("Tag:", tag)
        # print("Tag binary:", self.addr_as_binary_str(tag, separate=False))
        return (vpn, offset, index, tag)

    def get_physical_address(self, virtual_address):
        #Get the physical address for a virtual address
        (vpn, offset, index, tag) = self.process_virtual_address(virtual_address)
        pte = self.get_entry(vpn)
        if pte == 0:
            #print("Page fault!")
            return -1
        else:
            #print("Page hit!")
            return (pte.pfn << int(math.log2(self.page_size))) + offset

  
    def try_read_pte_virtual_address(self, virtual_address):
        #Try to read a virtual address and return the VPN, offset, and PTE
        vpn, offset, index, tag = self.process_virtual_address(virtual_address)
        try:
            pte = self.get_entry(vpn)
            return (pte)
        except:
            return None

        


