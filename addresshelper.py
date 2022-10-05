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
AddrHelper().bin()