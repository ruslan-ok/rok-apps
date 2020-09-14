CATEGORY_DESIGN = [
    'green',
    'blue',
    'red',
    'purple',
    'yellow',
    'orange'
]

def get_category_design(categ):
    l = 0
    for c in categ:
        l += ord(c)
    return CATEGORY_DESIGN[l % 6]

class Category():
    def __init__(self, name):
        self.name = name
        self.design = get_category_design(name)

def get_categories_list(caterories_string):
    ret = []
    if not caterories_string:
        return ret
    for categ in caterories_string.split():
        ret.append(Category(categ))
    return ret

