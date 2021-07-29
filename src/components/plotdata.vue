<template>
   <v-container style="max-width:1385px !important">
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
      headers:[{
         text: 'Position',
         value: 'sirna_position'
       }, {
         text: 'Sequence',
         value: 'sirna_sequence'
       }, {
         text: 'duplex',
         value: 'sirna_complement'
       }, {
         text: 'Efficiency',
         value: 'is_efficient'
       }, {
         text: 'GC content',
         value: 'gc_content'
       },{
         text: 'SNP exist',
         value: 'SNP_exist'
       },{
         text:'Strand selection',
         value: 'strand_selection'
       }, {
         text:'End stability',
         value: 'end_stability'
       }, {
         text:'Accessibility',
         value: 'accessibility_value'
       }, {
         text:'Target site accessibility',
         value:'target_site_accessibility'
       }, {
         text:'Antisense MFE',
         value:'anti_sense5_MFE_enegery'
       }, {
         text:'Sense MFE',
         value:'sense5_MFE_enegery'
       }, {
         text:'Delta MFE',
         value:'delta_MFE_enegery'
       }, {
         text:'Thermo efficient',
         value:'thermo_effcicient'
       }]
   }),
   created() {
      var plot_data = this.$store.state.plot_data;
      plot_data.forEach(e => {
        e['sirna_complement'] = 'XX'+e['sirna_sequence']+'\n'+e['sirna_complement']+'XX'
      })
      console.log(plot_data[0])
      this.reads = plot_data
      console.log(this.reads[0])
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