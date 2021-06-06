<template>
  <v-dialog
    v-model="dialog"
    persistent
    max-width="600px"
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
    <v-card>
      <v-card-title>
        <span class="headline">Databases management</span>
      </v-card-title>
      <v-card-text>
        <v-list>
          <v-list-item-title>
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

          </v-list-item-title>
          <v-divider></v-divider>
          <v-row>
            <v-col>Name</v-col>
            <v-col>Size</v-col>
            <v-col>Modified</v-col>
            <v-col>Description</v-col>
          </v-row>
          <v-divider></v-divider>
          <template v-for="database in databases">
            <v-divider class="ma-0" :key="`${database.uid}-divider`"></v-divider>
            <v-list-item style="height:52px" :key="database.uid">
              <v-list-item-action>
                <v-icon color="primary" v-if="database.edit">mdi-pencil</v-icon>
              </v-list-item-action>
              <template v-if="!database.edit">
                <v-list-item-title
                  class="amber--text"
                  @dblclick="toggleEdit({database, edit:true})"
                >{{ database.text }}</v-list-item-title>
                <v-list-item-action class="d-inline">
                  <v-btn @click="removeDatabase(database)" color="red lighten-3" text icon class="mr-8">
                    <v-icon>mdi-trash-can-outline</v-icon>
                  </v-btn>
                </v-list-item-action>
              </template>
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
        
      <!-- <v-card-actions>
        <v-btn
          @click="createDatabase()"
          primary
        >
          <v-icon>mdi-plus</v-icon>
          <div>New</div>
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          color="blue darken-1"
          text
          @click="dialog = false"
        >
          Close
        </v-btn>
      </v-card-actions> -->
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
</style>