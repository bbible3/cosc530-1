import math
import re
from tkinter import Y

##This file manages loading config files for the application

##This class represents a single configuration type
class Config:
    def __init__(self, name="", num_sets=-1, set_size=-1, num_vpages=-1, num_ppages=-1, page_size=-1, line_size=-1, write_through=False):
        self.name = name
        self.num_sets = num_sets
        self.set_size = set_size
        self.num_vpages = num_vpages
        self.num_ppages = num_ppages
        self.page_size = page_size
        self.line_size = line_size
        self.write_through = write_through

        self.max_dtlb_sets = 256
        self.max_dc_sets = 8192
        self.max_dtlb_assoc_level = 8
        self.max_dc_assoc_level = self.max_dtlb_assoc_level
        self.max_l2_assoc_level = self.max_dtlb_assoc_level
        self.max_virtual_pages = 8192
        self.max_physical_pages = 1024
        #The number of sets and line size for DTLB and DC, num of virtual pages, and page size should all be powers of:
        self.power_of = 2
        self.max_ref_addr_len = 32
        self.min_dc_data_line_size = 8
        self.min_l2_data_line_size = self.min_dc_data_line_size
        self.use_inclusive_multilevel_cache = True
        #Physical pages should be allocated from 0 to num_physical_pages - 1
        self.physical_page_upper = self.max_physical_pages - 1
        self.use_lru = True
        self.page_fault_action = "invalidate"

        self.page_table_index_bits = -1
        self.page_table_offset_bits = -1

    def get_config(self):
        return self

## This class represents a config file and stores many configuration types.
## It also handles reading and processing of config files
class ConfigFile:
    def __init__(self, filename):
        self.configs = {}
        self.filename = filename
        self.virtual_addresses = False
        self.tlb = False
        self.l2_cache = False
        self.lines = []


        self.tlb_bits = -1

        self.page_table_index_bits = -1
        self.page_table_offset_bits = -1

        self.data_cache_index_bits = -1
        self.data_cache_offset_bits = -1

        self.l2_cache_index_bits = -1
        self.l2_cache_offset_bits = -1

        self.cache_size = -1
        self.block_offset_len = -1

        self.address_len = -1
        self.virtual_address_len = -1

    def add_config(self, config):
        self.configs[config.name] = config

    def load_file(self):
        with open(self.filename) as f:
            #Read the file into a list of lines
            self.lines = f.readlines()

    def parse_lines(self):

        cur_working_config = Config()
        special_lines = ["Virtual addresses:", "TLB:", "L2 cache:"]
        for line in self.lines:
            #Is the line a root parameter?
            for special_line in special_lines:
                if line.__contains__(special_line):
                    val = "err"
                    #Strip any non-alphanumeric characters except : and space
                    line = re.sub('[^0-9a-zA-Z: ]+', '', line)
                    if special_line == "Virtual addresses:":
                        #Split line on special_line
                        line_split = line.split(special_line)[1]
                        val = True if 'y' in line_split else False
                        self.virtual_addresses = val
                    elif special_line == "TLB:":
                        #Split line on special_line
                        line_split = line.split(special_line)[1]
                        val = True if 'y' in line_split else False
                        self.tlb = val
                    elif special_line == "L2 cache:":
                        #Split line on special_line
                        line_split = line.split(special_line)[1]
                        val = True if 'y' in line_split else False
                        self.l2_cache = val
                    cur_working_config.name = "Root"
                    #print("Updated file-wide config: " + special_line + " to " + str(val))
                    break

            #Does the line contain a ":"?
            if ":" in line:
                #Yes, so it's a config line

                #Split by ":"
                line = line.split(":")

                #Get the config name
                found_setting = line[0]

                #Get the config values
                config_val = line[1]
                #Remove any non-alphanumeric characters
                config_val = re.sub('[^0-9a-zA-Z]+', '', config_val)

                if "Number of sets" in found_setting:
                    cur_working_config.num_sets = int(config_val)
                elif "Set size" in found_setting:
                    cur_working_config.set_size = int(config_val)
                elif "Number of virtual pages" in found_setting:
                    cur_working_config.num_vpages = int(config_val)
                elif "Number of physical pages" in found_setting:
                    cur_working_config.num_ppages = int(config_val)
                elif "Page size" in found_setting:
                    cur_working_config.page_size = int(config_val)
                elif "Line size" in found_setting:
                    cur_working_config.line_size = int(config_val)
                elif "Write-through" in found_setting:
                    cur_working_config.write_through = True if 'y' in config_val else False
                #print("Updated config: " + found_setting + " to " + config_val, "for config: " + cur_working_config.name)

    
            else:
                #Is the line less than 2 characters?
                if len(line) < 2:
                    #We can add the config to the list
                    self.add_config(cur_working_config)
                    #Reset the config
                    cur_working_config = Config()
                    print()
                else:
                    #It is specifying the current working config
                    #Does it contain the word "configuration"?
                    if "configuration" in line:
                        #Split by the word "configuration"
                        line = line.split("configuration")
                        config_type = line[0]
                        if cur_working_config.name == None or cur_working_config.name == "": #If the name is not set
                            cur_working_config.name = config_type
                        else:
                            continue
                            #print("Error trying to overwrite config name")
                            #print("Current config name: " + cur_working_config.name)
                            #print("New config name: " + config_type)
                        #print("Setting working config type to: " + config_type)
    def process_config(self):
        #This function calculates the number of index and offset bits for the different portions of the memory hierarchy
        #print("Calculating bits for configs")
        
        #Cache "line" and "block" are interchangable.
        #In the in class example, 
        #How many sets in 8MB cache? "How many blocks can this cache hold?"
        #cache size / block size = number of frames

        print("I am file: " + self.filename)
        #print("len of self.configs: " + str(len(self.configs)))
        for config in self.configs:
            #Print the config name
            #print("Config name: " + config)
            #Get the config object
            config_obj = self.configs[config]

            if config == "Data TLB ":
                #How many bits to index the TLB?
                #This is log2(num_sets * set_size)
                self.tlb_bits = int(math.log2(config_obj.num_sets * config_obj.set_size))
                #print("TLB bits: " + str(self.tlb_bits))

            if config == "Page Table ":
                num_virtual_pages = config_obj.num_vpages
                num_physical_pages = config_obj.num_ppages
                page_size = config_obj.page_size
                self.page_size = page_size
                #How many bits to index the page table?
                self.page_table_index_bits = int(math.log2(num_virtual_pages))
                #print("Page table index bits: " + str(self.page_table_index_bits))
                #How many bits for page offset?
                self.page_table_offset_bits = int(math.log2(page_size))
                #print("Page table offset bits: " + str(self.page_table_offset_bits))

            if config == "Data Cache ":
                num_sets = config_obj.num_sets
                set_size = config_obj.set_size

                line_size = config_obj.line_size
                #How many bits to index the cache?
                self.cache_index_bits = int(math.log2(num_sets))
                #print("Cache index bits: " + str(self.cache_index_bits))
                #How many bits for cache offset?
                self.cache_offset_bits = int(math.log2(line_size))
                #print("Cache offset bits: " + str(self.cache_offset_bits))

            if config == "L2 Cache ":
                num_sets = config_obj.num_sets
                set_size = config_obj.set_size
                

                line_size = config_obj.line_size
                #How many bits to index the cache?
                self.l2_cache_index_bits = int(math.log2(num_sets))
                #print("L2 Cache index bits: " + str(self.l2_cache_index_bits))
                #How many bits for cache offset?
                self.l2_cache_offset_bits = int(math.log2(line_size))
                #print("L2 Cache offset bits: " + str(self.l2_cache_offset_bits))

        #Calculate my virtual address length
        self.virtual_address_len = self.page_table_index_bits + self.page_table_offset_bits
        #print("Virtual address length: " + str(self.virtual_address_len))
    def pte_size(self):
        #How many bits is a page table entry?
        val = self.page_table_offset_bits + self.page_table_index_bits
        return val
    def output_config(self):
        num_sets_tlb = self.configs["Data TLB "].num_sets
        entries_per_set_tlb = self.configs["Data TLB "].set_size
        num_bits_index = self.tlb_bits
        print(f"Data TLB contains {num_sets_tlb} sets.")
        print(f"Each set contains {entries_per_set_tlb} entries.")
        print(f"Number of bits used for the index is {num_bits_index}.")
        print()
        
        num_vpages = self.configs["Page Table "].num_vpages
        num_ppages = self.configs["Page Table "].num_ppages
        bytes_per_page = self.configs["Page Table "].page_size
        num_bits_page_table_index = self.page_table_index_bits
        num_bits_page_table_offset = self.page_table_offset_bits
        print(f"Number of virtual pages is {num_vpages}.")
        print(f"Number of physical pages is {num_ppages}.")
        print(f"Each page contains {bytes_per_page} bytes.")
        print(f"Number of bits used for the page table index is {num_bits_page_table_index}.")
        print(f"Number of bits used for the page offset is {num_bits_page_table_offset}.")

        num_sets_data_cache = self.configs["Data Cache "].num_sets
        entries_per_set_data_cache = self.configs["Data Cache "].set_size
        bytes_per_line_data_cache = self.configs["Data Cache "].line_size
        write_policy_data_cache = self.configs["Data Cache "].write_through
        num_bits_data_cache_index = self.cache_index_bits
        num_bits_data_cache_offset = self.cache_offset_bits
        print(f"D-cache contains {num_sets_data_cache} sets.")
        print(f"Each set contains {entries_per_set_data_cache} entries.")
        print(f"Each line is {bytes_per_line_data_cache} bytes.")
        if write_policy_data_cache == "y":
            print("The cache uses a no-write-allocate and write-through policy.")
        else:
            print("The cache uses a write-allocate and write back policy.")
        print(f"Number of bits used for the index is {num_bits_data_cache_index}.")
        print(f"Number of bits used for the offset is {num_bits_data_cache_offset}.")
        print()

        num_sets_l2_cache = self.configs["L2 Cache "].num_sets
        entries_per_set_l2_cache = self.configs["L2 Cache "].set_size
        bytes_per_line_l2_cache = self.configs["L2 Cache "].line_size
        write_policy_l2_cache = self.configs["L2 Cache "].write_through
        num_bits_l2_cache_index = self.l2_cache_index_bits
        num_bits_l2_cache_offset = self.l2_cache_offset_bits
        print(f"L2 cache contains {num_sets_l2_cache} sets.")
        print(f"Each set contains {entries_per_set_l2_cache} entries.")
        print(f"Each line is {bytes_per_line_l2_cache} bytes.")
        if write_policy_l2_cache == "y":
            print("The cache uses a no-write-allocate and write-through policy.")
        else:
            print("The cache uses a write-allocate and write back policy.")
        print(f"Number of bits used for the index is {num_bits_l2_cache_index}.")
        print(f"Number of bits used for the offset is {num_bits_l2_cache_offset}.")
        print()

        #Do we use virtual addresses?
        if self.virtual_addresses:
            print("The addresses read in are virtual addresses.")
        else:
            print("The addresses read in are physical addresses.")