from enum import Enum
from re import T
class AddressType(int, Enum):
    #Define if the address is hex, binary, or decimal
    HEX = 16
    BIN = 2
    DEC = 10
    NULLTYPE = 0

#This class represents a single address, able to be displayed in different formats
#Must define address as a string, type as an AddressType
#min_len specifies the minimum length of the address, in bits - if the address is shorter, it will be padded with zeros
class Mapping():
    def __init__(self, offset, index, tag):
        self.offset = offset
        self.index = index
        self.tag = tag
    def print(self):
        print(f"Tag: {self.tag}, Index: {self.index}, Offset: {self.offset}")
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

        if len(my_bin)%4 != 0:
            #We need to pad the string with zeros
            my_bin = "0" * (4 - (len(my_bin)%4)) + my_bin
        
        #Pad if necessary
        if len(my_bin) < self.min_len:
            my_bin = "0" * (self.min_len - len(my_bin)) + my_bin
        
        #Split every 4
        my_bin = " ".join(my_bin[i:i+4] for i in range(0, len(my_bin), 4))
        return my_bin

    def mapping(self, n_offset=None, n_index=None, n_tag=None):

        max_addr_len = 32
        if n_offset is None or n_index is None:
            raise Exception("Must specify n_offset and n_index")
        
        #Get my binary representation
        my_bin = self.as_type(AddressType.BIN)
        my_bin = my_bin[2:]

        #Pad if necessary
        addr_bits = len(my_bin)
        if (addr_bits < max_addr_len):
            my_bin = "0" * (max_addr_len - addr_bits) + my_bin
        addr_bits = len(my_bin)
        
        n_offset_int = int(n_offset)
        n_index_int = int(n_index)
        if n_tag is None:
            n_tag_int = addr_bits - n_offset_int - n_index_int
        else:
            n_tag_int = int(n_tag)
 


        print("Tag of length", n_tag_int)

        n_tag_res = my_bin[0:n_tag_int]
        print("Got tag", n_tag_res)
        
        n_index_end = n_tag_int + n_index_int
        n_index_res = my_bin[n_tag_int:n_index_end]

        n_offset_start = n_index_end
        n_offset_res = my_bin[n_offset_start:addr_bits]

        #print(f"\tTag 0:{n_tag_int} = {n_tag_res}")
        #print(f"\tIndex {n_tag_int}:{n_index_end} = {n_index_res}")
        #print(f"\tOffset {n_index_end}:{addr_bits} = {n_offset_res}")
        bin_int_tag = int(n_tag_res, base=2)
        bin_int_index = int(n_index_res, base=2)
        bin_int_offset = int(n_offset_res, base=2)
        
        
        output_mapping = Mapping(bin_int_offset, bin_int_index, bin_int_tag)
        return output_mapping


class AddrHelper():

    def __init__(self, tag=4, index=4, offset=4):
        self.tag = tag
        self.index = index
        self.offset = offset
    def bin(self):
        while True:
            input_b = input("Enter a binary number: ")
            input_dec = int(input_b, 2)
            print(input_dec)
    def hexaddr(self):
        while True:
            #Read input frm command line
            input_v = input("Enter an address in hex:\n 0x")
            input_str = str(input_v)
            input_len = len(input_str)

            input_hex = int(input_str, 16)
            input_bin = bin(input_hex)
            #Strip 0b
            input_bin = input_bin[2:]
            input_bin_digits = len(input_bin)
            if input_bin_digits < 16:
                #Pad with zeros
                input_bin = input_bin.zfill(16)
            #Convert binary to string
            input_bin_str = str(input_bin)

            #Print 4 digits separated by spaces
            ct = 0
            for char in range(0, len(input_bin_str)):
                if char%4 == 0:
                    print(" ", end="")
                print(input_bin_str[char], end="")
                
            print("\n")


            #Offset bits are the last n=offset bits
            offset_bits = input_bin_str[-self.offset:]
            #Index bits are the next n=index bits
            index_bits = input_bin_str[-(self.offset+self.index):-self.offset]
            #Tag bits are the remaining bits
            tag_bits = input_bin_str[:-(self.offset+self.index)]

            offset_dec = int(offset_bits, 2)
            index_dec = int(index_bits, 2)
            tag_dec = int(tag_bits, 2)
            print("Tag: ", tag_bits, "(", tag_dec, ")")
            print("Index: ", index_bits, "(", index_dec, ")")
            print("Offset: ", offset_bits, "(", offset_dec, ")")



#AddrHelper(offset=4,index=6,tag=6)
#AddrHelper(offset=9,index=6,tag=6).hexaddr()
#AddrHelper().bin()