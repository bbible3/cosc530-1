from configs import Config
from configs import ConfigFile
from byter import Byter, Units
from pagetable import PageTable

#myConfig = ConfigFile("./memhier/traceslide70.config")
myConfig = ConfigFile("./memhier/trace.config")
myConfig.load_file()
myConfig.parse_lines()

#Calculate the number of index and offset bits for the different portions of the memory hierarchy
myConfig.process_config()

print("-----------------")
myConfig.output_config()



print("TESTING PAGE TABLE")
#Create a page table object
myPageTable = PageTable(parent_config_file=myConfig)
#Print the total size
print("Page table size: ", Byter(myPageTable.total_size).as_string(Units.B))
print("Or", Byter(myPageTable.total_size).as_string(Units.MB))
print("Currently, the table has", myPageTable.non_zero_entries(), "entries")
print("Let's add some entries")
#Add some entries
myPageTable.add_entry(myPageTable.create_entry(1, 1, 1, 1, 1, 1, 1))
myPageTable.add_entry(myPageTable.create_entry(1, 1, 1, 1, 1, 1, 1))
#Now print the number of non-zero entries
print("Now, the table has", myPageTable.non_zero_entries(), "entries")
#How many of them have a use bit of 1?
print("How many of them have a use bit of 1?")
print(len([x for x in myPageTable.table if x.use_bit == 1]))

# print("An example of processing a virtual address.")
# virtual_address = 0xDEADBEEF
# print("Virtual address:", hex(virtual_address))
# (vpn, offset) = myPageTable.process_virtual_address(virtual_address)
# print("VPN:", hex(vpn))
# print("Offset:", hex(offset))
print("Following the example in class, let's process a virtual address")
print("We add an entry to the page table. Specifically:")
print("An entry with an index of 71 and a pfn of 9")
myPageTable.add_entry(myPageTable.create_entry(71, 1, 1, 1, 9, 1, 1))
print("An example of trying to read a virtual address.")
virtual_address = 0x8FDF
print("Virtual address:", hex(virtual_address))
pte = myPageTable.try_read_pte_virtual_address(virtual_address)
if pte is not None:
    #We have a valid PTE
    print("Valid PTE found!")
    print("Its pfn is", hex(pte.pfn))
else:
    print("Page fault!")

get_physical_address = myPageTable.get_physical_address(virtual_address)
if get_physical_address is not None:
    print("Physical address:", hex(get_physical_address))
else:
    print("Page fault!")
