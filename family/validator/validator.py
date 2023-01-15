from __future__ import annotations

import os, glob
from dataclasses import dataclass, field
from typing import Optional
from ged4py.parser import GedcomReader
from ged4py.model import Record

work_folder = 'C:/Web/apps/rusel/family/validator'

class ParserError(Exception):
    pass

@dataclass
class LeafRecord:
    level: str
    struct_name: str
    xref_name: str
    tag: str
    xref_id: str
    value: str
    cardinality: str
    type: str
    page_num: int
    sub_records: list[LeafRecord] = field(default_factory=list)
    _actual_level: Optional[int] = None
    _key: Optional[str] = ''

    def add_sub_record(self, level, leaf):
        leaf_level = int(leaf.level.replace('+', ''))
        if level == leaf_level:
            self.sub_records.append(leaf)
        else:
            self.sub_records[-1].add_sub_record(level+1, leaf)

    def set_actual_level(self, level, key):
        self._actual_level = level
        self._key = key
        if key and self.tag:
            self._key += '.'
        self._key += self.tag
        for rec in self.sub_records:
            rec.set_actual_level(level+1, self._key)

    def get_key(self):
        return self._key

@dataclass
class StructPart:
    leafs: list[LeafRecord] = field(default_factory=list)

    def set_actual_level(self, level, key):
        for leaf in self.leafs:
            leaf.set_actual_level(level, key)

    def open_multy_tag(self):
        for leaf in self.leafs:
            if leaf.tag and leaf.tag.startswith('[') and leaf.tag.endswith(']'):
                tags = leaf.tag[1:-1].split('|')
                leaf.tag = tags[0]
                for tag in tags[1:]:
                    new_leaf = LeafRecord(
                        level=leaf.level,
                        struct_name=leaf.struct_name,
                        xref_name=leaf.xref_name,
                        tag=tag,
                        xref_id=leaf.xref_id,
                        value=leaf.value,
                        cardinality=leaf.cardinality,
                        type=leaf.type,
                        page_num=leaf.page_num,
                        sub_records=leaf.sub_records,
                    )
                    self.leafs.append(new_leaf)

@dataclass
class StructRecord:
    name: str
    alternatives: list[StructPart] = field(default_factory=list)

    def set_actual_level(self, level, key):
        for alternative in self.alternatives:
            alternative.set_actual_level(level, key)

    def open_multy_tag(self):
        for alternative in self.alternatives:
            alternative.open_multy_tag()

class GedcomSpec:
    _structures: list[StructRecord]
    _cardinalities: list[str]

    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name
        if '551' in file_name:
            self.version = '5.5.1'
        elif '707' in file_name:
            self.version = '7.0.7'
        else:
            self.version = ''
        self._structures = []
        self._cardinalities = []
        self.parse()
        for struct in self._structures:
            struct.open_multy_tag()
        print(f'done version {self.version}')

    def parse(self):
        self._data = []
        with open(self.file_name, 'r', encoding='latin-1') as f:
            self._data = f.read().splitlines()
        idx = 0
        while idx < len(self._data):
            line = self._data[idx]
            ss = line.split()
            if len(ss) > 1 and ss[1] == ':=':
                idx = self.read_structure(idx, ss[0])
            else:
                idx += 1
    
    def read_structure(self, idx, struct_name):
        struct = StructRecord(name=struct_name, alternatives=[])
        idx += 1
        if idx < len(self._data) and self._data[idx] == '[':
            idx = self.parse_alternatives(idx+1, struct)
        else:
            idx = self.parse_spec(idx, struct)
        self._structures.append(struct)
        return idx

    def get_cardinality_pos(self, parts):
        for pos in (2, 3, 4):
            if len(parts) > pos and parts[pos].startswith('{') and (parts[pos].endswith('}') or parts[pos].endswith('}*')):
                return pos
        raise ParserError(f'Invalid syntax: {" ".join(parts)}')

    def parse_alternatives(self, idx, struct):
        while idx < len(self._data) and self._data[idx] and self._data[idx] != ']':
            if self._data[idx] == '|':
                idx += 1
            else:
                idx = self.parse_spec(idx, struct)
        if self._data[idx] != ']':
            idx += 1
        return idx

    def parse_spec(self, idx, struct):
        spec = StructPart(leafs=[])
        while idx < len(self._data) and self._data[idx] and self._data[idx] not in ('|', ']'):
            parts = self._data[idx].split()
            if len(parts) < 2:
                raise ParserError(f'Invalid syntax: {self._data[idx]}')
            struct_name = ''
            xref_name = ''
            tag = ''
            xref_id = ''
            value = ''
            type = ''
            page_num = 0
            cardinality = ''

            level = parts[0]
            cardinality_pos = self.get_cardinality_pos(parts)
            if level != 'n':
                cardinality = parts[cardinality_pos]

            # struct
            if parts[1].startswith('<<') and parts[1].endswith('>>'):
                struct_name = parts[1].replace('<<', '').replace('>>', '')
            # xref name
            elif parts[1].startswith('@<XREF:') and parts[1].endswith('>@'):
                xref_name = parts[1].replace('@<XREF:', '').replace('>@', '')
                tag = parts[2]
                if cardinality_pos == 4:
                    value = parts[3]
            elif parts[1].startswith('@XREF:') and parts[1].endswith('@'):
                xref_name = parts[1].replace('@XREF:', '').replace('@', '')
                tag = parts[2]
                if cardinality_pos == 4:
                    value = parts[3]
            # xref id
            elif parts[2].startswith('@<XREF:') and parts[2].endswith('>@'):
                tag = parts[1]
                xref_id = parts[2].replace('@<XREF:', '').replace('>@', '')
            elif parts[2].startswith('@XREF:') and parts[2].endswith('@'):
                tag = parts[1]
                xref_id = parts[2].replace('@XREF:', '').replace('@', '')
            elif cardinality_pos == 2:
                tag = parts[1]
            elif cardinality_pos == 3:
                tag = parts[1]
                value = parts[2]

            if parts[-1].startswith('p.'):
                page_num = int(parts[-1].replace('p.', ''))

            if parts[-1].startswith('g7:'):
                type = parts[-1]

            leaf = LeafRecord(
                level=level,
                struct_name=struct_name,
                xref_name=xref_name,
                tag=tag,
                xref_id=xref_id,
                value=value,
                cardinality=cardinality,
                type=type,
                page_num=page_num,
                sub_records=[],
            )

            if leaf.cardinality not in self._cardinalities:
                self._cardinalities.append(leaf.cardinality)

            if level in ('0', 'n'):
                spec.leafs.append(leaf)
            else:
                spec.leafs[-1].add_sub_record(1, leaf)
            idx += 1
        struct.alternatives.append(spec)
        return idx

    def get_structure(self, struct_name, level, key):
        for struct in self._structures:
            if struct.name == struct_name:
                struct.set_actual_level(level, key)
                return struct
        return None

class Validator:
    gedcom_specs: list[GedcomSpec]

    def __init__(self, version=None):
        super().__init__()
        self.gedcom_specs = []
        os.chdir(work_folder)
        files = glob.glob('*.spec')
        for file in files:
            if version and version not in file:
                continue
            self.gedcom_specs.append(GedcomSpec(file))


    def check_tree(self, file_name, version=None):
        file_ok = False
        gedcom_ver = ''
        for specification in self.gedcom_specs:
            self._specification = specification
            dataset = specification.get_structure('Dataset', 0, '')
            ok = True
            with GedcomReader(file_name) as parser:
                for item in parser.records0():
                    if not self.validate_structure(item, dataset, ''):
                        ok = False
                        break
            # if ok:
            #     if not self.check_cardinality(item, dataset):
            #         ok = False
            if ok:
                file_ok = True
                gedcom_ver = specification.version
                break
        print(f'done: {file_ok=}, {gedcom_ver=}')

    # def check_cardinality(self, item, struct):
    #     pass

    def validate_structure(self, item, struct, key):
        for alternative in struct.alternatives:
            res = self.validate_spec(item, alternative, key)
            if res:
                return True
        return False

    def fits(self, item: Record, leaf: LeafRecord, key) -> bool:
        if item.level != leaf._actual_level:
            return False
        if not item.tag:
            raise Exception(f'Record item without tag: {item}')
        if leaf.tag and (leaf.tag == item.tag or item.tag.startswith('_')):
            return True
        if leaf.struct_name:
            struct = self._specification.get_structure(leaf.struct_name, item.level, key)
            if self.validate_structure(item, struct, key):
                return True
        return False

    def fits_with_sub_records(self, item: Record, leaf: LeafRecord, key) -> bool:
        item.valid = False
        if self.fits(item, leaf, key):
            new_key = item.tag
            if key:
                new_key = key + '.' + item.tag
            sub_records_fits = True
            for sub_item in item.sub_records:
                sub_item_fits = False
                for sub_leaf in leaf.sub_records:
                    if self.fits_with_sub_records(sub_item, sub_leaf, new_key):
                        sub_item_fits = True
                        break
                if not sub_item_fits:
                    sub_records_fits = False
                    break
            if sub_records_fits:
                item.valid = True
                item.struct_name = leaf.struct_name
                if not item.key:
                    item.key = leaf.get_key()
        return item.valid

    def validate_spec(self, item, alternative, key):
        for leaf in alternative.leafs:
            if self.fits_with_sub_records(item, leaf, key):
                return True
        return False

if __name__ == '__main__':
    validator = Validator()
    validator.check_tree('C:/Web/apps/rusel/family/validator/zhmailik.ged')
