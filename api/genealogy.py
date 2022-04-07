from rest_framework import serializers

class Individual:
    def __init__(self, upd, name, sex, birth, death, nation, buri, events, fams, famc, rin, uid, objs):
        self.upd = upd
        self.name = name
        self.sex = sex
        self.birth = birth
        self.death = death
        self.nation = nation
        self.buri = buri
        self.events = events
        self.fams = fams
        self.famc = famc
        self.rin = rin
        self.uid = uid
        self.objs = objs

class GenealogySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)