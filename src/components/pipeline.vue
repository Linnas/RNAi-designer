<template>
  <v-container>
    <v-row class="mt-6 d-flex justify-center">
      <v-col cols="4" class="pr-8">
        <v-select
          :items="databases"
          label="Databases"
          solo
          v-model="database"
        ></v-select>
        <v-row>
          <v-col>
            <v-text-field
              v-model.number="siRNA_size"
              label="siRNA size"
            ></v-text-field>
        </v-col>
          <v-col>
            <v-text-field
              v-model.number="mismatch"
              label="Mismatch"
            ></v-text-field>
        </v-col>
        </v-row>
        <v-row>
          <v-col cols="4">
            <div>GC content range:</div>
          </v-col>
          <v-col cols="2">
            <v-text-field
              :value="range[0]"
              hide-details
              single-line
              type="number"
              suffix="%"
              class="my-0 py-0"
            ></v-text-field>
          </v-col>
          <v-col cols="1">
            <div class="d-flex justify-center">---</div>
          </v-col>
          <v-col cols="2">
            <v-text-field
                :value="range[1]"
                hide-details
                single-line
                type="number"
                suffix="%"
                class="mt-0 pt-0"
              ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="5">
            <div>Avoid contiguous G's or C's</div>
          </v-col>
          <v-col cols="2">
            <v-text-field
              :value="consecutive"
              hide-details
              single-line
              type="number"
              class="mt-0 pt-0"
            ></v-text-field>
          </v-col>
          <v-col>
            <div>nt or more</div>
          </v-col>
        </v-row>
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
            <v-btn rounded color="primary" x-large @click="startPipeline()" :loading="loading">parse</v-btn>
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
    range:[40, 60],
    consecutive:4,
    reads:[],
    bowtie_location:null,
    rnaplfold_location:null,
    appPath: null,
    loading: false,
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
  created() {
    window.electron.getAppPath().then(res => {
      this.bowtie_location = res+'\\Bowtie';
      this.rnaplfold_location = res + '\\RNAplfold';
    });
    
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
      this.loading = true;
      var no_efficience = true;
      const { siRNA_size, mismatch, sequences, database, items, bowtie_location, rnaplfold_location } = this;
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
        database,
        bowtie_location,
        rnaplfold_location,
        no_efficience,

      }
      console.log(query)
      this.axios.post(this.$localServer + 'run_pipeline', query).then((res) => {
        console.log(res.data);
        this.loading = false;
        var align_data = res.data.align_data;
        this.$store.state.alignData = align_data;
        this.$router.push({ name: 'aligntable'})
      }).catch(err => {
        console.log(err);
        this.loading = false;
      })
    }
    
  }
}
</script>
