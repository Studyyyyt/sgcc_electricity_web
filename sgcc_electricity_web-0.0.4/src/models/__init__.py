import config
from .electricity import Electricity

electricity = Electricity(config.db['name'])