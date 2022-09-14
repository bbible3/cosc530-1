from configs import Config
from configs import ConfigFile

myConfig = ConfigFile("./memhier/trace.config")
myConfig.load_file()
myConfig.parse_lines()

#Calculate the number of index and offset bits for the different portions of the memory hierarchy
myConfig.process_config()

print("-----------------")
myConfig.output_config()