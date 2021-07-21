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
            v-for="(title, idx) in right_titles" 
            :key="title.text" 
            @click="openExternal(idx)">
            <v-icon>{{ title.icon }}</v-icon>
          </v-btn>
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
export default {
  name: 'App',
  components: {
    databaseDialog
  },
  data: () => ({
    steps:['Home', 'Align', 'Filter'],
    right_titles:[{
      icon:"mdi-github",
    }, {
      icon:"mdi-help-circle-outline",
    }]
  }),
  methods:{
    openExternal(v) {
      if (v === 0) {
        window.electron.openExternal('https://github.com/Linnas/RNAi-designer')
      } else if (v === 1) {
        window.electron.openExternal('http://8.131.68.217/')
      }
    },
    backHome() {
         this.$router.back()
    },
  }
};
</script>
