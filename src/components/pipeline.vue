<template>
  <v-container>
    <v-row class="mt-6 d-flex justify-center" v-show="!tableTab">
      <v-col cols="4" class="pr-8">
        <v-select
          :items="databases"
          label="Databases"
          solo
          :value='database'
        ></v-select>
        <v-text-field
          v-model.number="siRNA_size"
          label="siRNA size"
        ></v-text-field>
        <v-text-field
          v-model.number="mismatch"
          label="Mismatch"
        ></v-text-field>
      </v-col>

      <v-col cols="4">
        <v-textarea
          solo
          name="sequence-input"
          label=""
          height="350"
          :value="sequences | trimSequence"
          counter
          @input="value=>sequences=value"
          placeholder="Paste your sequence here."
        ></v-textarea>
        <v-row>
          <v-col class="d-flex justify-center">
            <v-btn rounded color="primary" x-large @click="startPipeline()">parse</v-btn>
          </v-col>
        </v-row>
      </v-col>

      <v-col cols="4" class="pl-8">
        <v-row v-for="(item, index) in items" :key="item.label" dense>
        <v-col cols="6">
          <v-checkbox
            v-model="item.status"
            :label="item.label"
            class="mt-0"
          ></v-checkbox>
        </v-col>
        <v-col cols="3">
          <v-text-field
            solo
            dense
            v-if="index !== 0 && index !== 1"
            type="number"
            :value="item.value"
          ></v-text-field>
        </v-col>
        </v-row>
      </v-col>
    </v-row>
    <v-row v-show="tableTab">
       <v-data-table
          :headers="headers"
          :items="reads"
          class="elevation-1"
        >
        </v-data-table>
    </v-row>
  </v-container>
</template>

<script>
import { mapState } from 'vuex'
export default {
  name: 'Pipeline',
  data: () => ({
    siRNA_size: 21,
    mismatch:0,
    sequences:'',
    database:'',
    tableTab: false,
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
    reads:[],
    items:[{
      status:true,
      label:'5\' Terminal nucleotide rule'
    },{
      status:true,
      label:'Strand selection'
    }, {
      status:true,
      label:'End stability difference',
      value:1.00
    }, {
      status:true,
      label:'Target site accessibility threshod',
      value:0.10
    }, {
      status:true,
      label:'Accessibility calculation window',
      value:8
    }]
  }),
  computed: {
    ...mapState([
      "databases"
    ])
  },
  filters: {
    trimSequence: function(value){
      if (!value) return ''
      value = value.toString()
      return value.trim().replace(/\n/g, '')
    }
  },
  methods: {
    startPipeline() {
      var no_efficience = true;
      const { siRNA_size, mismatch, sequences, items } = this;
      if (items[0].status && items[1].status && items[2].status && items[3].status)
          no_efficience = false
      const query = {
        siRNA_size, mismatch, sequences, 
        terminal_check:items[0].status,
        strand_check:items[1].status,
        end_check:items[2].status,
        end_stability_treshold:items[2].value,
        accessibility_check:items[3].status,
        target_site_accessibility_treshold:items[3].value,
        accessibility_window:items[4].value,
        database:'hg19',
        bowtie_location:'C:/Users/sirius/Desktop/rnai/Bowtie/',
        rnaplfold_location:'C:/Users/sirius/Desktop/rnai/RNAplfold/',
        no_efficience,

      }
      console.log(query)
      this.axios.post('http://localhost:8000/analysis/run_pipeline', query).then((res) => {
        console.log(res.data);
        var align_data = res.data.align_data
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
        })
        console.log(this.reads)
        this.tableTab = true
      })
    }
    
  }
}
</script>
