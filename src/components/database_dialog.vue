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
        <v-list>
          <!-- <v-list-item-title>
            <v-text-field
              label=""
              class="ma-4"
              @keydown.enter="createDatabase"
              autocomplete="off"
              clearable
              color="rgb(40, 85, 163)"
              solo
              dense
              light
              max-width="400px"
              hide-details
              maxlength="1023"
              v-model="db_name"
            >
             <template v-slot:append>
              <v-btn icon @click="createDatabase">
                <v-icon>mdi-plus</v-icon>
              </v-btn>
             </template>
            </v-text-field>

          </v-list-item-title> -->
          <v-row class="mb-2">
            <v-col class="font-weight-black" cols="4">Name</v-col>
            <v-col class="font-weight-black" cols="4">Last Modified</v-col>
            <v-col class="font-weight-black" cols="2">Size</v-col>
            <v-col class="font-weight-black" cols="2">Type</v-col>
          </v-row>
          <v-divider></v-divider>
          <template v-for="database in databases">
            <v-list-item style="height:52px" :key="database.uid">
              <template v-slot:default="{ active, }">
                <v-list-item-action>
                  <v-checkbox
                    :input-value="active"
                    color="primary"
                  ></v-checkbox>
                </v-list-item-action>

                <v-list-item-content>
                  <v-list-item-title>Notifications</v-list-item-title>
                  <v-list-item-subtitle>Allow notifications</v-list-item-subtitle>
                </v-list-item-content>
              </template>
              <v-list-item-action>
                <v-icon color="primary" v-if="database.edit">mdi-pencil</v-icon>
              </v-list-item-action>
              <v-list-item-content v-if="!database.edit">
                <v-list-item-title
                  @dblclick="toggleEdit({database, edit:true})"
                >{{ database.text }}</v-list-item-title>
              </v-list-item-content>
              <v-text-field
                :value="database.text"
                @blur="doneEdit"
                @keyup.enter="doneEdit"
                @keyup.esc="cancelEdit"
                clearable
                color="#fff"
                flat
                hide-details
                counter="1023"
                ref="input"
                solo
                v-else
                v-focus="database.edit"
              ></v-text-field>
          </v-list-item>
          </template>           
        </v-list>
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
      db_name:''
    };
  },
  directives: {
    focus(el, { value }, { context }) {
      if (value) {
        context.$nextTick(() => {
          context.$refs.input[0].focus();
        });
      }
    }
  },
  created() {
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