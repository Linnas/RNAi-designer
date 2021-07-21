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
              <v-row class="d-flex justify-center">
                  <v-col cols="12">
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
var xl = require('excel4node');
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
         text: 'Efficiency',
         value: 'is_efficient'
       }, {
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
      this.reads = plot_data
      console.log(this.reads[0])
   },
   methods:{
      exportAsExcel() {
         var plot_data = this.reads
         var title = this.headers.map(i => i.text)
         var wb = new xl.Workbook();
         var ws = wb.addWorksheet('Sheet 1');
         for (var i = 0; i < 13; i++) {
            console.log(this.headers[i].text)
            ws.cell(1, i+1).string(this.headers[i].text)
         }
         plot_data.forEach((e, i) => {
            ws.cell(i+2, 1).number(e[this.headers[0].value])
            ws.cell(i+2, 2).string(e[this.headers[1].value])
            ws.cell(i+2, 3).bool(e[this.headers[2].value])
            ws.cell(i+2, 4).bool(e[this.headers[3].value])
            ws.cell(i+2, 5).number(e[this.headers[4].value])
            ws.cell(i+2, 6).bool(e[this.headers[5].value])
            ws.cell(i+2, 8).number(e[this.headers[7].value])
            ws.cell(i+2, 9).number(e[this.headers[8].value])
            ws.cell(i+2, 10).number(e[this.headers[9].value])
            ws.cell(i+2, 12).bool(e[this.headers[10].value])
            ws.cell(i+2, 13).bool(e[this.headers[11].value])
         })
         window.electron.export().then(res => {
            if (res.canceled) return;
            console.log(res.filePath)
            wb.write(res.filePath);
         })
         
      }
   }
   
}
</script>