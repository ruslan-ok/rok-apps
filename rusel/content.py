class Group():
    id = None
    name = None
    items = []

    def __init__(self, grp_id, name):
        self.id = grp_id
        self.name = name
        self.items = []

    def id(self):
        if self.grp:
            return self.grp.grp_id
        return 0

    def name(self):
        if self.grp:
            return self.grp.name
        return ''

def find_group(groups, grp_id, name):
    for group in groups:
        if (group.id == grp_id):
            return group
    group = Group(grp_id, name)
    groups.append(group)
    return group

