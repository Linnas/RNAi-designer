<template>
  <v-dialog
    v-model="dialog"
    max-width="800px"
    class="height:600px"
  >
    <template v-slot:activator="{ on, attrs }">
      <v-btn
        text
        v-bind="attrs"
        v-on="on"
      >
        <v-icon>mdi-database</v-icon>
        <div>Databases</div>
      </v-btn>
    </template>
    <v-card height="50vh">
      <v-toolbar
      flat
      >
        <v-toolbar-title class="font-weight-bold">Database Management</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn text class="mr-6">
          <v-icon color="primary">mdi-plus</v-icon>
          <span class="ml-2">Add</span>
        </v-btn>
        <v-btn text class="mr-6" @click="removeDatabase(database)">
          <v-icon color="primary">mdi-trash-can-outline</v-icon>
          <span class="ml-2">Delete</span>
        </v-btn>
        <v-btn text class="mr-6">
          <v-icon color="primary">mdi-share-outline</v-icon>
          <span class="ml-2">Share</span>
        </v-btn>
        <v-divider vertical inset></v-divider>
        <v-btn icon @click="dialog = false" class="ml-2">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-toolbar>
      <v-card-text class="mt-6">
          <v-data-table
            v-model="selected"
            :headers="headers"
            :items="databases"
            single-select
            item-key="text"
            show-select
             hide-default-footer
            disable-pagination
            disable-sort
            class="elevation-1"
          >
        </v-data-table>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>
<script>
import { mapState, mapActions } from "vuex";
export default {
  name: 'databaseDialog',
  data() {
    return {
      dialog:false,
      db_name:'',
      selected:[],
      headers:[{
        text:'Name',
        value:'text',
      },{
        text:'Last Modified',
        value:'time'
      },{
        text:'Size(MB)',
        value:'size'
      },{
        text:'Type',
        value:'type'
      }]
    };
  },
  // directives: {
  //   focus(el, { value }, { context }) {
  //     if (value) {
  //       context.$nextTick(() => {
  //         context.$refs.input[0].focus();
  //       });
  //     }
  //   }
  // },
  created() {
    this.axios.get(this.$localServer + 'getAllDatabasesInfo').then(res => {
      const val = Object.values(res.data)
      const keys = Object.keys(res.data)
      const values = val[0].map((_, colIdx) => val.map(row => row[colIdx]))
      const dbs = values.map(arr => Object.fromEntries(keys.map((_, i) => [keys[i], arr[i]])))
      console.log(dbs);
      dbs.forEach(db => this.$store.commit('addDatabase', db));
    })
  },
  computed: {
    ...mapState([
      "databases"
      ]),
  },

  methods: {
    ...mapActions(["addDatabase", "removeDatabase", "editDatabase", "toggleEdit"]),
    createDatabase() {
      const text = this.db_name.trim()
      const Bowtie_location = this.$Bowtie_location
      if(text) {
        window.electron.createDatabase().then(res => {
          console.log(res)
          if(res.canceled) {
            return
          } else {
            let path = res.filePaths[0]
            this.addDatabase({
            path,
            text,
            loc:Bowtie_location,
            size:'20Mb'
          })
          }
        })
      }
      
    },
    doneEdit(e) {
      const value = e.target.value.trim();
      const database = this.databases.find((e) => e.edit);
      if (!value) {
        e.target.value = database.text;
        this.toggleEdit({database, edit:false});
      } else if (database.edit) {
        this.editDatabase({
          database,
          value
        });
        this.toggleEdit({database, edit:false});
      }
    },
    cancelEdit() {
      const database = this.databases.find((e) => e.edit);
      this.toggleEdit({database, edit:false});
    }
  }
};
</script>

<style>
.todo-item .v-input__slot {
  padding: 0 !important;
}
.v-btn {
  text-transform: capitalize !important;
}
</style>