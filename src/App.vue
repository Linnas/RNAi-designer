<template>
  <v-app>
    <v-app-bar app>
      <v-row class="d-flex justify-center text-center">
        <v-col  cols="4">
          <databaseDialog/>
          <v-btn 
            text 
            v-for="(title) in left_titles" 
            :key="title.text" 
            class="mx-4"
             
            >
              <v-icon>{{ title.icon }}</v-icon>
              <div>{{ title.text }}</div>
          </v-btn> 
        </v-col>
        <v-col cols="4" >
          <div class="display-1 primary--text">RNAi Designer</div>
        </v-col>
        <v-col class="d-flex justify-center" cols="4" >
          <v-btn text v-for="(title, idx) in right_titles" :key="title.text" class="mx-4"
          @click="openExternal(idx)">
            <v-icon>{{ title.icon }}</v-icon>
            <div>{{ title.text }}</div>
          </v-btn>     
        </v-col>
      </v-row>
    </v-app-bar>
    <v-main>
      <Pipeline/>
    </v-main>
  </v-app>
</template>

<script>
import Pipeline from './components/pipeline';
import databaseDialog from './components/database_dialog'
export default {
  name: 'App',
  components: {
    Pipeline,
    databaseDialog
  },

  data: () => ({
    left_titles:[{
      icon:"mdi-file-document",
      text:"Docs"
    }, {
      icon:"mdi-help",
      text:"FAQ"
    }],
    right_titles:[{
      icon:"mdi-github",
      text:"Github"
    }, {
      icon:"mdi-help-circle-outline",
      text:"help"
    }]
  }),
  methods:{
    openExternal(v) {
      if (v === 0) {
        window.electron.openExternal('https://github.com/Linnas/RNAi-designer')
      } else if (v === 1) {
        window.electron.openExternal('http://8.131.68.217/')
      }
    }
  }
};
</script>
