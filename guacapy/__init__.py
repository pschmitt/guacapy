import sys
if sys.version_info[0] < 3:
    from client import Guacamole
    from templates import *
else:
    from .client import Guacamole
    from .templates import *
