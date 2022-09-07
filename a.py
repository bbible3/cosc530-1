from configs import Config
from configs import ConfigFile

myConfig = ConfigFile("./memhier/trace.config")
myConfig.load_file()
myConfig.parse_lines()