Vue.component('tree', {
    template: `
        <div>
            <div id="treecontainer">
                <div id="tree"></div>
            </div>
        </div>
    `,
    props: ["person"],
    data: function() {
        return {
            modalAddPerson: {}
        }
    },
    mounted: function() {
        stamboom.register({
            treecontainer: document.getElementById("treecontainer"),
            tree: document.getElementById("tree")
        });
        // Register to stamboom events
        stamboom.onselect(this.onselect);
    },
    methods: {
        onselect: function(id) {
            this.$root.selectedPerson = id;
            this.$root.person = stamboom.getPerson(id);
            this.$root.person.relations = stamboom.getRelations(id);
            this.$root.person.parents = stamboom.getParents(id);
            var page = this.$root.page;
            if (!["tree"].includes(page)) {
                page = "tree";
            }
            document.location.hash = "/" + page + "/" + id
        },
    }
});