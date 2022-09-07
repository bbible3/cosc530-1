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
        self.configs = []
        self.filename = filename
        self.virtual_addresses = False
        self.tlb = False
        self.l2_cache = False
        self.lines = []


    def add_config(self, config):
        self.configs.append(config)

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
               