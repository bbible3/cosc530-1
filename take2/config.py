import math


class Config():
    def __init__(self, filename):
        self.filename = filename
        #Does the plaintext file exist
        self.lines = []

        self.dtlb_num_sets = None
        self.dtlb_set_size = None

        self.pt_num_vpages = None
        self.pt_num_ppages = None
        self.pt_page_size = None

        self.dc_num_sets = None
        self.dc_set_size = None
        self.dc_line_size = None
        self.dc_writethrough_nowriteallocate = None

        self.l2_num_sets = None
        self.l2_set_size = None
        self.l2_line_size = None
        self.l2_writethrough_nowriteallocate = None

        self.use_virtual_addresses = None
        self.use_tlb = None
        self.use_l2 = None


        self.dtlb_num_index_bits = None

        self.pt_num_index_bits = None
        self.pt_num_offset_bits = None

        self.dc_num_index_bits = None
        self.dc_num_offset_bits = None

        self.l2_num_index_bits = None
        self.l2_num_offset_bits = None


        try:
            with open(filename, 'r') as f:
                #Read line by line
                for line in f:
                    #Strip newlines from the end of the line
                    line = line.rstrip()
                    self.lines.append(line)
        except FileNotFoundError:
            raise FileNotFoundError("File not found", filename)
        
        self.num_lines = len(self.lines)
        for i in range(self.num_lines):
            line = self.lines[i]
            
            #Is it blank?
            if line == "":
                continue
            if line == "Data TLB configuration":
                line_num_sets = self.lines[i+1]
                line_set_size = self.lines[i+2]
                property_num, value_num = self.split_and_read(line_num_sets)
                property_set, value_set = self.split_and_read(line_set_size)
                if property_num == "Number of sets":
                    self.dtlb_num_sets = int(value_num)
                if property_set == "Set size":
                    self.dtlb_set_size = int(value_set) 

            if line == "Page Table configuration":
                line_num_vpages = self.lines[i+1]
                line_num_ppages = self.lines[i+2]
                line_page_size = self.lines[i+3]
                property_num, value_num = self.split_and_read(line_num_vpages)
                property_set, value_set = self.split_and_read(line_num_ppages)
                property_size, value_size = self.split_and_read(line_page_size)
                if property_num == "Number of virtual pages":
                    self.pt_num_vpages = int(value_num)
                if property_set == "Number of physical pages":
                    self.pt_num_ppages = int(value_set)
                if property_size == "Page size":
                    self.pt_page_size = int(value_size)

            if line == "Data Cache configuration":
                line_num_sets = self.lines[i+1]
                line_set_size = self.lines[i+2]
                line_line_size = self.lines[i+3]
                line_writethrough_nowriteallocate = self.lines[i+4]
                property_num, value_num = self.split_and_read(line_num_sets)
                property_set, value_set = self.split_and_read(line_set_size)
                property_size, value_size = self.split_and_read(line_line_size)
                property_write, value_write = self.split_and_read(line_writethrough_nowriteallocate)
                if property_num == "Number of sets":
                    self.dc_num_sets = int(value_num)
                if property_set == "Set size":
                    self.dc_set_size = int(value_set)
                if property_size == "Line size":
                    self.dc_line_size = int(value_size)
                if property_write == "Write through/no write allocate":
                    self.dc_writethrough_nowriteallocate = value_write

            if line == "L2 Cache configuration":
                line_num_sets = self.lines[i+1]
                line_set_size = self.lines[i+2]
                line_line_size = self.lines[i+3]
                line_writethrough_nowriteallocate = self.lines[i+4]
                property_num, value_num = self.split_and_read(line_num_sets)
                property_set, value_set = self.split_and_read(line_set_size)
                property_size, value_size = self.split_and_read(line_line_size)
                property_write, value_write = self.split_and_read(line_writethrough_nowriteallocate)
                if property_num == "Number of sets":
                    self.l2_num_sets = int(value_num)
                if property_set == "Set size":
                    self.l2_set_size = int(value_set)
                if property_size == "Line size":
                    self.l2_line_size = int(value_size)
                if property_write == "Write through/no write allocate":
                    self.l2_writethrough_nowriteallocate = value_write

            match_virtual_addresses = "Virtual addresses"
            #Is the first part of the line "Virtual addresses"
            if line[0:len(match_virtual_addresses)] == match_virtual_addresses:
                key_va, value_va = self.split_and_read(line)
                if key_va == "Virtual addresses":
                    self.use_virtual_addresses = value_va
            
            match_tlb = "TLB"
            #Is the first part of the line "TLB"
            if line[0:len(match_tlb)] == match_tlb:
                key_tlb, value_tlb = self.split_and_read(line)
                if key_tlb == "TLB":
                    self.use_tlb = value_tlb
            
            match_l2 = "L2 cache"
            #Is the first part of the line "L2 cache"
            if line[0:len(match_l2)] == match_l2:
                key_l2, value_l2 = self.split_and_read(line)
                if key_l2 == "L2 cache":
                    self.use_l2 = value_l2

        #At this point the config file has been set up, so calculate stuff

        if self.dc_writethrough_nowriteallocate == "y":
            self.dc_writethrough_nowriteallocate = True
        else:
            self.dc_writethrough_nowriteallocate = False
        if self.l2_writethrough_nowriteallocate == "y":
            self.l2_writethrough_nowriteallocate = True
        else:
            self.l2_writethrough_nowriteallocate = False
        if self.use_virtual_addresses == "y":
            self.use_virtual_addresses = True
        else:
            self.use_virtual_addresses = False
        if self.use_tlb == "y":
            self.use_tlb = True
        else:
            self.use_tlb = False
        if self.use_l2 == "y":
            self.use_l2 = True
        else:
            self.use_l2 = False

        #Do some calculations
        self.dtlb_num_index_bits = math.log(self.dtlb_num_sets, 2)

        self.pt_num_index_bits = math.log(self.pt_num_vpages, 2)
        self.pt_num_offset_bits = math.log(self.pt_page_size, 2)

        self.dc_num_index_bits = math.log(self.dc_num_sets, 2)
        self.dc_num_offset_bits = math.log(self.dc_line_size, 2)

        self.l2_num_index_bits = math.log(self.l2_num_sets, 2)
        self.l2_num_offset_bits = math.log(self.l2_line_size, 2)


        #Make them all ints
        self.dtlb_num_index_bits = int(self.dtlb_num_index_bits)
        self.pt_num_index_bits = int(self.pt_num_index_bits)
        self.pt_num_offset_bits = int(self.pt_num_offset_bits)
        self.dc_num_index_bits = int(self.dc_num_index_bits)
        self.dc_num_offset_bits = int(self.dc_num_offset_bits)
        self.l2_num_index_bits = int(self.l2_num_index_bits)
        self.l2_num_offset_bits = int(self.l2_num_offset_bits)

        self.addr_len = 32

        #Calculate bit ranges
        self.dtlb_tag_start = 0
        self.dtlb_tag_end = self.addr_len - self.dtlb_num_index_bits - self.pt_num_offset_bits
        self.dtlb_index_start = self.dtlb_tag_end
        self.dtlb_index_end = self.dtlb_index_start + self.dtlb_num_index_bits
        self.dtlb_offset_start = self.dtlb_index_end
        self.dtlb_offset_end = self.dtlb_offset_start + self.pt_num_offset_bits
        #VPN is everything that's not the offse
        self.dtlb_vpn_start = 0
        self.dtlb_vpn_end = self.dtlb_offset_start

        self.pt_tag_start = 0
        self.pt_tag_end = self.addr_len - self.pt_num_index_bits - self.pt_num_offset_bits
        self.pt_index_start = self.pt_tag_end
        self.pt_index_end = self.pt_index_start + self.pt_num_index_bits
        self.pt_offset_start = self.pt_index_end
        self.pt_offset_end = self.pt_offset_start + self.pt_num_offset_bits

        self.dc_tag_start = 0
        self.dc_tag_end = self.addr_len - self.dc_num_index_bits - self.dc_num_offset_bits
        self.dc_index_start = self.dc_tag_end
        self.dc_index_end = self.dc_index_start + self.dc_num_index_bits
        self.dc_offset_start = self.dc_index_end
        self.dc_offset_end = self.dc_offset_start + self.dc_num_offset_bits

        self.l2_tag_start = 0
        self.l2_tag_end = self.addr_len - self.l2_num_index_bits - self.l2_num_offset_bits
        self.l2_index_start = self.l2_tag_end
        self.l2_index_end = self.l2_index_start + self.l2_num_index_bits
        self.l2_offset_start = self.l2_index_end
        self.l2_offset_end = self.l2_offset_start + self.l2_num_offset_bits

        self.pt_num_entries = (2**self.addr_len)*self.pt_page_size




            
    def split_and_read(self, line):
        #Split the sentence on ":"
        try:
            split_line = line.split(":")
        except:
            raise Exception("Invalid line", line)
        line_key = split_line[0]
        line_value = split_line[1]
        #Remove whitespace from line_value
        line_value = line_value.replace(" ", "")
        return line_key, line_value
    
    def output(self):
        print(f"Data TLB contains {self.dtlb_num_sets} sets.")
        print(f"Each set contains {self.dtlb_set_size} entries.")
        print(f"Number of bits used for the index is {self.dtlb_num_index_bits}.")
        print()
        print(f"Number of virtual pages is {self.pt_num_vpages}.")
        print(f"Number of physical pages is {self.pt_num_ppages}.")
        print(f"Each page contains {self.pt_page_size} bytes.")
        print(f"Number of bits used for the page table index is {self.pt_num_index_bits}.")
        print(f"Number of bits used for the page offset is {self.pt_num_offset_bits}.")
        print()
        print(f"D-cache contains {self.dc_num_sets} sets.")
        print(f"Each set contains {self.dc_set_size} entries.")
        print(f"Each line is {self.dc_line_size} bytes.")
        if self.dc_writethrough_nowriteallocate:
            print(f"The cache uses a write-allocate and write-back policy.")
        else:
            print(f"The cache uses a write-allocate and write back policy.")
        print(f"Number of bits used for the index is {self.dc_num_index_bits}.")
        print(f"Number of bits used for the offset is {self.dc_num_offset_bits}.")
        print()
        print(f"L2 cache contains {self.l2_num_sets} sets.")
        print(f"Each set contains {self.l2_set_size} entries.")
        print(f"Each line is {self.l2_line_size} bytes.")
        if self.l2_writethrough_nowriteallocate:
            print(f"The cache uses a write-allocate and write-back policy.")
        else:
            print(f"The cache uses a write-allocate and write back policy.")
        print(f"Number of bits used for the index is {self.l2_num_index_bits}.")
        print(f"Number of bits used for the offset is {self.l2_num_offset_bits}.")
        print()
        if self.use_virtual_addresses:
            print(f"The addresses read in are virtual addresses.")