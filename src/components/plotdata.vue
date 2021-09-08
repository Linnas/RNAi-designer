<template>
   <v-container style="max-width:1585px !important">
      <v-tabs
         v-model="tab"
         background-color="transparent"
         color="basil"
      >
         <v-tab
           v-for="item in ['table', 'charts']"
           :key="item"
         >
           {{ item }}
         </v-tab>
      </v-tabs>
      <v-tabs-items v-model="tab">
         <v-tab-item
            eager
         >
           <v-card
             color="basil"
             flat
           >
              <v-row>
                  <v-col cols="12">
                    <div class="d-flex justify-space-between my-4">
                      <div></div>
                      <div class="title">
                        Efficient siRNA candidates table
                      </div>
                      <div style="margin-top: -6px;">
                        <v-btn icon @click="exportAsExcel"><v-icon>
                          mdi-export-variant
                        </v-icon></v-btn>
                      </div>
                      
                    </div>
                      <v-data-table
                     :headers="headers"
                     :items="reads"
                     class="elevation-1"
                   >
                   <template v-slot:item.is_efficient="{ item }">
                      <v-chip
                        :color="item.is_efficient?'green':'red'"
                        dark
                      >
                        {{ item.is_efficient }}
                      </v-chip>
                    </template>
                   </v-data-table>
                  </v-col>
               </v-row>
           </v-card>
        </v-tab-item>
         <v-tab-item
            eager
         >
           <v-card
             color="basil"
             flat
           >
               
           </v-card>
        </v-tab-item>
     </v-tabs-items>        
   </v-container>
</template>
<script>
const URL = 'http://127.0.0.1:8000/analysis/exportTable'
export default {
   name: 'Tabular',
   data: () => ({
      reads: null,
      tab:null,
      headers:null
      }),
   created() {
      var plot_data = this.$store.state.plot_data;
      this.headers = Object.keys(plot_data[0]).map(v => {
        return {
          text:v.split('_').join(' '),
          value:v
        }
      })
      console.log(this.headers)
      this.reads = plot_data
   },
   methods:{
      exportAsExcel() {
        window.electron.export().then(res => {
          if (res.canceled) return;
          console.log(res.filePath)
          return this.axios.post(URL, {path:res.filePath})
         }).then(res => {
            if(res.code === '200') {
              console.log('Saved successfully')
            }
          }).catch(e => {
            console.log(e)
          })   
      }
   }
   
}
</script>
<style scoped>
  .headlay {
    margin: auto;
  }
</style>