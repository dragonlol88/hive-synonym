from .model import *
from sqlalchemy import and_, or_, desc, asc

MODELS = {
    "Project"    : Project,
    "ProjectUser": ProjectUser,
    "User"       : User,
    "Cartegory"  : Cartegory,
    "Origin"     : Origin,
    "Synonym"    : Synonym
}

AND_OR = {
    "and": and_,
    "or" : or_
}

ORDER = {
    'desc': desc,
    'asc' : asc
}