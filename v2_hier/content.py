from hier.models import ContentGroup

class Group():
    grp = None
    items = []

    def __init__(self, user, app, grp_id, name):
        self.grp = get_grp(user, app, grp_id, name)
        self.items = []

    def id(self):
        if self.grp:
            return self.grp.grp_id
        return 0

    def name(self):
        if self.grp:
            return self.grp.name
        return ''

    def is_open(self):
        if self.grp:
            return self.grp.is_open
        return False


def get_grp(user, app, grp_id, name):
    if ContentGroup.objects.filter(user = user.id, app = app, grp_id = grp_id).exists():
        return ContentGroup.objects.filter(user = user.id, app = app, grp_id = grp_id).get()
    return ContentGroup.objects.create(user = user, app = app, grp_id = grp_id, name = name, is_open = True)


def find_group(groups, user, app, grp_id, name):
    for group in groups:
        if (group.grp.grp_id == grp_id):
            return group
    group = Group(user, app, grp_id, name)
    groups.append(group)
    return group

