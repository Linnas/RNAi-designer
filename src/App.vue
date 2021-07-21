  <template>
  <v-app>
    <v-app-bar app height="58">
      <v-row class="mt-n2">
        <v-col  cols="4">
          <v-row class="mt-2">
            <v-img src="/avata.png" max-width="50"></v-img>
            <div 
              class="display-1 primary--text" 
              style="cursor: pointer;" 
              @click="$router.push('/')"
            >
              RNAi Designer
            </div>
          </v-row>
          
        </v-col>
        <v-col cols="4" >
          
        </v-col>
        <v-col class="d-flex justify-end" cols="4" >
          <databaseDialog/>
          <v-btn 
            text 
            icon  
            @click="openExternal()">
            <v-icon>mdi-github</v-icon>
          </v-btn>
          <help/>
          <v-switch
            v-model="$vuetify.theme.dark"
            class="mt-3 mx-4"
          ></v-switch>    
        </v-col>
      </v-row>
    </v-app-bar>
    <v-main>
      <keep-alive include="/">
        <router-view></router-view>        
      </keep-alive>
    </v-main>
  </v-app>
</template>

<script>
import databaseDialog from './components/database_dialog'
import help from './components/help'
export default {
  name: 'App',
  components: {
    databaseDialog,
    help
  },
  data: () => ({
    steps:['Home', 'Align', 'Filter'],
    dialog: false,
    right_titles:[{
      icon:"mdi-github",
    }, {
      icon:"mdi-help-circle-outline",
    }]
  }),
  methods:{
    openExternal() {
      window.electron.openExternal('https://github.com/Linnas/RNAi-designer')
    },
    backHome() {
         this.$router.back()
    },
  }
};
</script>
