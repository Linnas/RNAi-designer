<template>
   <v-container style="max-width:1385px !important">
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
            <v-btn @click="save" class="mr-2">Save</v-btn>
         </v-col>
      </v-row>
<!--       <v-dialog
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
      </v-dialog> -->
   </v-container>
</template>
<script>
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
      save() {

      }
   }
   
}
</script>