import math
import re

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
                    print("Updated file-wide config: " + special_line + " to " + str(val))
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
                print("Updated config: " + found_setting + " to " + config_val, "for config: " + cur_working_config.name)

    
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
                            print("Error trying to overwrite config name")
                            print("Current config name: " + cur_working_config.name)
                            print("New config name: " + config_type)
                        print("Setting working config type to: " + config_type)
    def process_config(self):
        #This function calculates the number of index and offset bits for the different portions of the memory hierarchy
        print("Calculating bits for configs")
        
        #Cache "line" and "block" are interchangable.
        #In the in class example, 
        #How many sets in 8MB cache? "How many blocks can this cache hold?"
        #cache size / block size = number of frames

        print("I am file: " + self.filename)
        print("len of self.configs: " + str(len(self.configs)))
        for config in self.configs:
            #Print the config name
            print("Config name: " + config)
            #Get the config object
            config_obj = self.configs[config]

            if config == "Data TLB ":
                #How many bits to index the TLB?
                #This is log2(num_sets * set_size)
                self.tlb_bits = int(math.log2(config_obj.num_sets * config_obj.set_size))
                print("TLB bits: " + str(self.tlb_bits))

            if config == "Page Table ":
                num_virtual_pages = config_obj.num_vpages
                num_physical_pages = config_obj.num_ppages
                page_size = config_obj.page_size
                #How many bits to index the page table?
                self.page_table_index_bits = int(math.log2(num_virtual_pages))
                print("Page table index bits: " + str(self.page_table_index_bits))
                #How many bits for page offset?
                self.page_table_offset_bits = int(math.log2(page_size))
                print("Page table offset bits: " + str(self.page_table_offset_bits))

            if config == "Data Cache ":
                num_sets = config_obj.num_sets
                set_size = config_obj.set_size
                line_size = config_obj.line_size
                #How many bits to index the cache?
                self.cache_index_bits = int(math.log2(num_sets))
                print("Cache index bits: " + str(self.cache_index_bits))
                #How many bits for cache offset?
                self.cache_offset_bits = int(math.log2(line_size))
                print("Cache offset bits: " + str(self.cache_offset_bits))

            if config == "L2 Cache ":
                num_sets = config_obj.num_sets
                set_size = config_obj.set_size
                line_size = config_obj.line_size
                #How many bits to index the cache?
                self.l2_cache_index_bits = int(math.log2(num_sets))
                print("L2 Cache index bits: " + str(self.l2_cache_index_bits))
                #How many bits for cache offset?
                self.l2_cache_offset_bits = int(math.log2(line_size))
                print("L2 Cache offset bits: " + str(self.l2_cache_offset_bits))

        #Calculate my virtual address length
        self.virtual_address_length = self.page_table_index_bits + self.page_table_offset_bits
        print("Virtual address length: " + str(self.virtual_address_length))

    def output_config(self):
        #This function produces output in the same way that the in class example did
        print(f"Data TLB Contains {self.configs['Data TLB '].num_sets} sets.")
        print(f"Each set contains {self.configs['Data TLB '].set_size} entries.")
            

