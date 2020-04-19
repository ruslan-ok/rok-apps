import xml.etree.ElementTree as ET
from datetime import datetime
from .models import Group, Entry, History


def import_group_times(group, u, n, cnt, err):
    for p in n:
        if (p.tag == 'CreationTime'):
            group.creation = datetime.strptime(p.text, '%Y-%m-%dT%H:%M:%SZ')
            group.save()
        elif (p.tag == 'LastModificationTime'):
            group.last_mod = datetime.strptime(p.text, '%Y-%m-%dT%H:%M:%SZ')
            group.save()
        elif (p.tag == 'LastAccessTime'):
            pass
        elif (p.tag == 'ExpiryTime'):
            pass
        elif (p.tag == 'Expires'):
            pass
        elif (p.tag == 'UsageCount'):
            pass
        elif (p.tag == 'LocationChanged'):
            pass
        else:
            err.append('[x] import_group_times(): unexpected tag:' + p.tag.__str__())


def import_entry_times(entry, u, n, cnt, err):
    for p in n:
        if (p.tag == 'CreationTime'):
            entry.creation = datetime.strptime(p.text, '%Y-%m-%dT%H:%M:%SZ')
            entry.save()
        elif (p.tag == 'LastModificationTime'):
            entry.last_mod = datetime.strptime(p.text, '%Y-%m-%dT%H:%M:%SZ')
            entry.save()
        elif (p.tag == 'LastAccessTime'):
            pass
        elif (p.tag == 'ExpiryTime'):
            pass
        elif (p.tag == 'Expires'):
            pass
        elif (p.tag == 'UsageCount'):
            pass
        elif (p.tag == 'LocationChanged'):
            pass
        else:
            err.append('[x] import_entry_times(): unexpected tag:' + p.tag.__str__())


def import_auto_type(entry, u, n, cnt, err):
    for p in n:
        if (p.tag == 'Enabled'):
            if (p.text != 'True'):
                err.append('[x] import_auto_type(): unexpected value of tag Enabed:' + p.text)
        elif (p.tag == 'DataTransferObfuscation'):
            pass
        else:
            if (p.text != '0'):
                err.append('[x] import_auto_type(): unexpected value of tag DataTransferObfuscation:' + p.text)
            err.append('[x] import_auto_type(): unexpected tag:' + p.tag.__str__())


def import_string(entry, u, n, cnt, err):
    key = ''
    value = ''
    for p in n:
        if (p.tag == 'Key'):
            key = p.text
        elif (p.tag == 'Value'):
            value = p.text
        else:
            err.append('[x] import_string(): unexpected tag:' + p.tag.__str__())

    if (key == '') or (key == None):
        err.append('[x] import_string(): empty key')
    else:
        if (value != '') and (value != None):
            if (key == 'Notes'):
                entry.notes = value
                entry.save()
            elif (key == 'Password'):
                entry.value = value
                entry.save()
            elif (key == 'Title'):
                entry.title = value
                entry.save()
            elif (key == 'URL'):
                entry.url = value
                entry.save()
            elif (key == 'UserName'):
                entry.username = value
                entry.save()
            else:
                err.append('[x] import_string(): unexpected key:' + key)


def import_history(entry, u, n, cnt, err):
    for p in n:
        if (p.tag == 'Entry'):
            data = import_entry(None, 0, u, p, cnt, err)
            History.objects.create(node = entry, data = data)
        else:
            err.append('[x] import_history(): unexpected tag:' + p.tag.__str__())


def import_entry(group, actual, u, n, cnt, err):
    entry = Entry.objects.create(user = u, group = group, title = '???', value = '???', actual = actual, username = '', url = '', uuid = '')
    for p in n:
        if (p.tag == 'UUID'):
            entry.uuid = p.text
            entry.save()
        elif (p.tag == 'IconID'):
            pass
        elif (p.tag == 'ForegroundColor'):
            pass
        elif (p.tag == 'BackgroundColor'):
            pass
        elif (p.tag == 'OverrideURL'):
            pass
        elif (p.tag == 'Tags'):
            pass
        elif (p.tag == 'Times'):
            import_entry_times(entry, u, p, cnt, err)
        elif (p.tag == 'String'):
            import_string(entry, u, p, cnt, err)
        elif (p.tag == 'Binary'):
            pass
        elif (p.tag == 'AutoType'):
            import_auto_type(entry, u, p, cnt, err)
        elif (p.tag == 'History'):
            import_history(entry, u, p, cnt, err)
        else:
            err.append('[x] import_entry(): unexpected tag:' + p.tag.__str__())
    return entry

def import_group(u, n, cnt, err):
    group = Group.objects.create(user = u, name = '???', uuid = '')
    for p in n:
        if (p.tag == 'UUID'):
            group.uuid = p.text
            group.save()
        elif (p.tag == 'Name'):
            group.name = p.text
            group.save()
        elif (p.tag == 'Notes'):
            pass
        elif (p.tag == 'IconID'):
            pass
        elif (p.tag == 'Times'):
            import_group_times(group, u, p, cnt, err)
        elif (p.tag == 'IsExpanded'):
            pass
        elif (p.tag == 'DefaultAutoTypeSequence'):
            pass
        elif (p.tag == 'EnableAutoType'):
            pass
        elif (p.tag == 'EnableSearching'):
            pass
        elif (p.tag == 'LastTopVisibleEntry'):
            pass
        elif (p.tag == 'Entry'):
            import_entry(group, 1, u, p, cnt, err)
        elif (p.tag == 'Group'):
            import_group(u, p, cnt, err)
        else:
            err.append('[x] import_group(): unexpected tag:' + p.tag.__str__())

def import_root(u, n, cnt, err):
    for p in n:
        if (p.tag == 'Group'):
            import_group(u, p, cnt, err)
        elif (p.tag == 'DeletedObjects'):
            if (p.text != '') and (p.text != None):
                err.append('[!] import_root(): DeletedObjects with text:' + p.text)
            if (len(p) > 0):
                err.append('[!] import_root(): DeletedObjects with text:' + p.text)
        else:
            err.append('[x] import_root(): not empty DeletedObjects:' + str(len(p)))

def import_top(u, n, cnt, err):

    if (n.tag == 'Meta'):
        pass
    elif (n.tag == 'Root'):
        import_root(u, n, cnt, err)
    else:
        err.append('[x] import_root(): unexpected tag:' + p.tag.__str__())

    err.append('[x] import_top(): unexpected tag:' + n.tag.__str__())

def delete_all():
    Group.objects.all().delete()
    Entry.objects.all().delete()
    History.objects.all().delete()

def import_all(u, cnt, err):
    err.clear()
    delete_all()
    root = ET.parse('C:\\Web\\apps\\rusel\\store\\entries.xml').getroot()
    for n in root:
        import_top(u, n, cnt, err)
