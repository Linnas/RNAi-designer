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
         <v-col cols="6">
            <div id="pieDiv" ref="pieDiv"></div>
         </v-col>
         <v-col>
            <v-simple-table dense>
             <template v-slot:default>
               <thead>
                 <tr>
                   <th class="text-left">
                     location
                   </th>
                   <th class="text-left" v-for="i in 21" :key="i">
                     {{ i }}
                   </th>
                 </tr>
               </thead>
               <tbody>
                 <tr
                   v-for="item in luna_data"
                   :key="item[0]"
                 >
                   <td v-for="n in item" :key="n">{{ n }}</td>
                 </tr>
               </tbody>
             </template>
           </v-simple-table>
         </v-col>
         <v-col>
            <v-spacer></v-spacer>
            <v-btn @click="backHome" class="mr-2">Return</v-btn>
            <v-btn @click="dialog = true">Targets</v-btn>
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
      Plotly.newPlot('pieDiv', data).then(res => console.log(res));
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