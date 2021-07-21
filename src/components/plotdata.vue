<template>
   <v-container style="max-width:1385px !important">
      <v-row>
         <v-spacer></v-spacer>
         <v-btn @click="exportAsExcel()">Export</v-btn>
      </v-row>
      <v-row class="d-flex justify-center">
         <v-col cols="12">
             <v-data-table
            :headers="headers"
            :items="reads"
            class="elevation-1"
          >
          </v-data-table>
         </v-col>
         <v-col>
            <v-spacer></v-spacer>
            <v-btn @click="backHome" class="mr-2">Return</v-btn>
         </v-col>
      </v-row>
   </v-container>
</template>
<script>
var xl = require('excel4node');
export default {
   name: 'Tabular',
   data: () => ({
      reads: null,
      dialog:false,
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
         text:'Accessibility',
         value: 'accessibility_value'
       }, {
         text:'End stability',
         value: 'end_stability'
       }, {
         text:'Off target',
         value:'is_off_target'
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
         text:'Ref strand position',
         value:'reference_strand_pos'
       }, {
         text:'Target site accessibility',
         value:'target_site_accessibility'
       }, {
         text:'Thermo efficient',
         value:'thermo_effcicient'
       }]
   }),
   created() {
      var plot_data = this.$store.state.plot_data;
      this.reads = plot_data
      console.log(this.reads)
   },
   methods:{
      backHome() {
         this.$router.push('/tabular')
      },
      exportAsExcel() {
         var plot_data = this.reads
         var title = this.headers.map(i => i.text)
         console.log(title)
         console.log(plot_data)
         var wb = new xl.Workbook();
         var ws = wb.addWorksheet('Sheet 1');
         for (var i = 0; i < 13; i++) {
            console.log(this.headers[i].text)
            ws.cell(1, i+1).string(this.headers[i].text)
         }
         wb.write('fuck.xlsx')
         // plot_data.forEach((e, i) => {
         //    ws.cell(i+2, 1).number(e[this.headers[0].value])
         //    ws.cell(i+2, 2).string(e[this.headers[1].value])
         //    ws.cell(i+2, 3).bool(e[this.headers[2].value])
         //    ws.cell(i+2, 4).bool(e[this.headers[3].value])
         //    ws.cell(i+2, 5).number(e[this.headers[4].value])
         //    ws.cell(i+2, 6).bool(e[this.headers[5].value])
         //    ws.cell(i+2, 7).bool(e[this.headers[6].value])
         //    ws.cell(i+2, 8).number(e[this.headers[7].value])
         //    ws.cell(i+2, 9).number(e[this.headers[8].value])
         //    ws.cell(i+2, 10).number(e[this.headers[9].value])
         //    ws.cell(i+2, 11).number(e[this.headers[10].value])
         //    ws.cell(i+2, 12).bool(e[this.headers[11].value])
         //    ws.cell(i+2, 13).bool(e[this.headers[12].value])
         // })
         // window.electron.export().then(res => {
         //    if (res.canceled) return;
         //    console.log(res.filePath)
         //    console.log(ws)
         //    wb.write(res.filePath);
         // })
         
      }
   }
   
}
</script>