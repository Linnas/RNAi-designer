<template>
   <v-container>
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
           <v-card-title class="justify-center">
              Align results based on Bowtie v1.0
           </v-card-title>
           <v-data-table
               :headers="headers"
               :items="reads"
               class="elevation-1"
             >
            </v-data-table>
            <v-card-actions>
               <v-spacer></v-spacer>
               <v-btn 
                  outlined 
                  style="border-color: grey;" 
                  @click="dialog=true"
               >Next</v-btn>
            </v-card-actions>
           </v-card>
         </v-tab-item>
         <v-tab-item
            eager
         >
           <v-card
             color="basil"
             flat
             
           >
            <v-row>
               <v-col cols=8>
                  <div id="lunaDiv"></div>
               </v-col>
               <v-col cols=4>
                  <div id="pieDiv"></div>
               </v-col>
            </v-row>
           </v-card>
         </v-tab-item>
       </v-tabs-items>    
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
               <v-btn @click="checkTarget()" class="mr-1" :loading="loading">Next</v-btn>
            
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
      tab: null,
      luna_data: null,
      targets:[],
      target:null,
      loading:false,
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
           snp_sum: r[7],
         }
       });
   },
   mounted() {
      var align_data = this.$store.state.alignData;

      var hit_targets =  align_data[0].map((_, colIndex) => align_data.map(r => r[colIndex]))

      var collator = new Intl.Collator(undefined, {numeric: true, sensitivity: 'base'});
      this.targets = [...new Set(hit_targets[2])].sort(collator.compare);

      var targets_counts = _.countBy(hit_targets[2])

      var trace1 = {
         values: Object.values(targets_counts),
         labels: Object.keys(targets_counts),
         type:'pie',
         name:'hit Target',
         hole:.4,
         textinfo: "label+percent",
         textposition: "outside",
         automargin: true,
         hoverinfo: 'label+percent',
      };
      var layout = {
         height:550,
         width:300,
         margin: {"t": 0, "b": 0, "l": 0, "r": 0},
         showlegend:false

      };
      Plotly.newPlot('pieDiv', [trace1], layout)
      // Plotly.newPlot('pieDiv2', [trace2], layout)

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
               {target:'above', value: {marker:{color:'#DE354C'}}},
               {target:'below', value: {marker:{color:'#3C1874'}}}
            ]
         }]
      }]
      var layout = {
         title:{
            text:'unpaired probabilities',
            font:'Arial',
            size:4
         },
         showlegend:false,
         yaxis:{
            range:[0, 1]
         },
         xaxis: {
            range:[21, lunp_data_loc.slice(-1)[0]]
         },
         width:800,
         height:500,
         shapes:[{
            type:'line',
            x0:0,
            y0:0.1,
            x1:1000000,
            y1:0.1,
            line: {
              color: 'rgb(55, 128, 191)',
              width: 2
            }
         }]
      }
      Plotly.newPlot('lunaDiv', trace, layout, {displayModeBar: false})
   },
   methods:{
      backHome() {
         this.$router.push('/')
      },
      checkTarget() {
         this.loading = true;
         var query = {
            target: this.targets[this.target]
         };
         this.axios.post('http://localhost:8000/analysis/process_data', query).then(res => {
            console.log(res.data)   
            var plot_data = res.data;
            this.$store.state.plot_data = plot_data.table_data;
            this.loading = false;
            this.$router.push({ name: 'plotData'})
         }).catch(e => {
            console.log('--Server Error--');
            console.log(e);
         })
      }
   }
   
}
</script>