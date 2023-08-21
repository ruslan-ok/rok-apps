spec_file_551 = 'c:/gedcom/5.5.1/gedcom_551.spec'
spec_file_707 = 'c:/gedcom/7.0.7/gedcom_707.spec'
sample_file_551 = 'c:/gedcom/5.5.1/sample_551.ged'
sample_file_707 = 'c:/gedcom/7.0.7/sample_707.ged'

class Gedcom:

    def __init__(self, vers, spec_file):
        self.vers = vers
        self.read_spec(spec_file)

    def read_spec(self, spec_file):
        print('-'*20)
        print(f'start read spec {self.vers}')
        self.gedcom = []
        self.types_used = []
        self.level_0_tags = []
        with open(spec_file, 'r', encoding='utf-8') as f:
            data = f.read().splitlines()
            new_type = None
            type_def = []
            for idx, s in enumerate(data):
                if not s and new_type and len(type_def):
                    self.gedcom.append({'type': new_type, 'definition': type_def})
                    new_type = None
                    type_def = []
                    continue
                if not s:
                    print(f'[x] Error "Unexpected empty string in line {idx}')
                    continue
                ss = s.split()
                if len(ss) > 1 and ss[1] == ':=' and not new_type:
                    new_type = ss[0]
                    continue
                type_def.append(s)
                ss = s.split()
                if len(ss) > 1 and ss[1].startswith('<<') and ss[1].endswith('>>'):
                    tmp = ss[1].replace('<<', '').replace('>>', '')
                    if tmp not in self.types_used:
                        self.types_used.append(tmp)
                if ss[0] not in ('[', ']', '|'):
                    level = int(ss[0].replace('n', '0').replace('+', ''))
                    if ss[1].startswith('@') and ss[1].endswith('@'):
                        tag = ss[2]
                    else:
                        tag = ss[1]
                    if level == 0 and tag not in self.level_0_tags:
                        self.level_0_tags.append(tag)
            if new_type and len(type_def):
                self.gedcom.append({'type': new_type, 'definition': type_def})


    def spec_stat(self):
        print(f'done {self.vers}: {len(self.gedcom)} types defined, {len(self.types_used)} types used')
        def_types = [t['type'] for t in self.gedcom]
        for t in self.types_used:
            if t not in def_types:
                print(f'[x] Error "Undefined type" {t}')

    def check(self, file_name):
        print('-'*20)
        print(f'start checking {file_name}')
        with open(file_name, 'r', encoding='UTF-8') as f: # Latin-1 CP1252
            data = []
            s = ''
            prev = ''
            row = 0
            while True:
                try:
                    prev = s
                    row += 1
                    s = f.readline().replace('\n', '')
                except Exception as ex:
                    print(f'[x] Error: "Exception on read string", {row=}, {prev=}')
                    continue
                if not s:
                    break
                data.append(s) 
            prev = ''
            row = 0
            for s in data:
                row += 1
                ss = s.split()
                if len(ss) < 2:
                    print(f'[x] Error: "Expected minimum 2 elements": {s}, {row=}, {prev=}')
                    break
                if ss[1] == 'HEAD' and ss[0].endswith('0'):
                    level = 0
                else:
                    level = int(ss[0])
                if ss[1].startswith('@') and ss[1].endswith('@'):
                    tag = ss[2]
                else:
                    tag = ss[1]
                if level == 0 and tag not in self.level_0_tags:
                    print(f'[x] Error: "Unknown tag": {s}')
                prev = s

if __name__ == '__main__':
    gedcom_551 = Gedcom('5.5.1', spec_file_551)
    gedcom_551.spec_stat()

    gedcom_707 = Gedcom('7.0.7', spec_file_707)
    gedcom_707.spec_stat()

    gedcom_551.check(sample_file_551)
    gedcom_707.check(sample_file_707)
