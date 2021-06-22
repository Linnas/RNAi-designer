<template>
   <v-container>
      <v-row class="d-flex justify-center">
         <v-col cols="6">
            <v-data-table
               :headers="headers"
               :items="reads"
               dense
               class="elevation-1 mt-16"
             >
            </v-data-table>
         </v-col>
         <v-col cols="6" fluid>
            <div id="pieDiv"></div>
            <v-spacer></v-spacer>
            <v-btn @click="dialog = true">Targets</v-btn>
         </v-col>
      </v-row>
      <v-row>
         <v-col>
            <div id="lunaDiv"></div>
         </v-col>
      </v-row>
      <v-dialog
         v-model="dialog"
         persistent
         max-width="600px">
         <v-card>
            <v-card-title class="headline primary--text">Choose your target</v-card-title>
            <v-divider></v-divider>
            <v-card-text>
               <v-radio-group v-model="target">
                  <v-radio
                    v-for="t in targets"
                    :key="t"
                    :label="t"
                  >
                     <template v-slot:label>
                        <div><strong class="grey--text">{{ t }}</strong></div>
                     </template>
                  </v-radio>
                </v-radio-group>
            </v-card-text>
            <v-card-actions>
               <v-spacer></v-spacer>
               <v-btn @click="dialog = false" class="mr-2">Cancel</v-btn>
               <v-btn @click="checkTarget()" class="mr-1">Next</v-btn>
            
            </v-card-actions>
         </v-card>
      </v-dialog>
   </v-container>
</template>
<script>
import Plotly from 'plotly.js-dist'
const _ = require('lodash')
export default {
   name: 'Tabular',
   data: () => ({
      reads: null,
      luna_data: null,
      targets:[],
      target:null,
      dialog:false,
      headers:[{
         text: 'Read Name',
         value: 'name'
       }, {
         text: 'Reference strand',
         value: 'strand'
       }, {
         text: 'Reference Name',
         value: 'rname'
       }, {
         text: 'Offset',
         value: 'offset'
       }, {
         text: 'Read sequence',
         value: 'sequence'
       }, {
         text: 'Same Align',
         value:'total'
       }, {
         text:'mismatch',
         value: 'mismatch'
       }],
   }),
   created() {
      var align_data = this.$store.state.alignData;
      var luna_data  = this.$store.state.lunaData;
      this.luna_data = luna_data;
      this.reads = align_data.map( function(r){
         return {
           name: r[0],
           strand: r[1],
           rname: r[2],
           offset: r[3],
           sequence: r[4],
           total: r[6],
           mismatch: r[7]
         }
       });
   },
   mounted() {
      var align_data = this.$store.state.alignData;

      var hit_targets =  align_data[0].map((_, colIndex) => align_data.map(r => r[colIndex]))
      var collator = new Intl.Collator(undefined, {numeric: true, sensitivity: 'base'});
      this.targets = [...new Set(hit_targets[2])].sort(collator.compare);

      var targets_counts = _.countBy(hit_targets[2])

      var data = [{
         values: Object.values(targets_counts),
         labels: Object.keys(targets_counts),
         type:'pie'
      }]
      Plotly.newPlot('pieDiv', data)

      var lunp_data = this.$store.state.lunaData;
      var lunp_data_loc  = lunp_data.map(loc => loc[0])
      var lunp_data_xmer = lunp_data.map(loc => loc[8])
      var lunp_trans     = lunp_data_xmer.map(v => v>=0.1?'above':'below')

      var trace = [{
         x: lunp_data_loc,
         y: lunp_data_xmer,
         mode:'markers',
         type:'scatter',
         name:'accessibility_value',
         marker: {
            size:4
         },
         transforms: [{
            type:'groupby',
            groups:lunp_trans,
            styles:[
               {target:'above', value: {marker:{color:'red'}}},
               {target:'below', value: {marker:{color:'blue'}}}
            ]
         }]
      }]
      var layout = {
         title:'unpaired probabilities',
         yaxis:{
            range:[0, 1]
         },
         xaxis: {
            range:[21, lunp_data_loc.slice(-1)[0]]
         },
         shapes:[{
            type:'line',
            x0:0,
            y0:0.1,
            x1:1000,
            y1:0.1,
            line: {
              color: 'rgb(55, 128, 191)',
              width: 2
            }
         }]
      }
      Plotly.newPlot('lunaDiv', trace, layout)
   },
   methods:{
      backHome() {
         this.$router.push('/')
      },
      checkTarget() {
         var query = {
            target: this.target
         };
         this.axios.post('http://localhost:8000/analysis/process_data', query).then(res => {
            console.log(res.data)
            this.loading = false;
            var plot_data = res.data.json_lst;
            this.$store.state.plot_data = plot_data;
            this.$router.push({ name: 'plotData'})
         })
      }
   }
   
}
</script>