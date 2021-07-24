<template>
  <v-container fluid>
    <v-row class="mt-6 d-flex justify-center">
      <v-col cols="4" class="px-14">
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
          <v-col cols="12">
            <div class="subtitle">Right end type:</div>
          </v-col>
          <v-col cols="12">
            <v-radio-group
              v-model="right_end_type"
              row
            >
              <v-radio
                label="complement"
                value="complement"
              ></v-radio>
              <v-radio
                label="dangling"
                value="dangling"
              ></v-radio>
            </v-radio-group>
          </v-col>
        </v-row>
        
        <v-row>
          <v-col>
            <v-range-slider
              v-model="range"
              :max="100"
              :min="0"
              hide-details
              class="align-center"
            >
              <template v-slot:prepend>
                <v-text-field
                  :value="range[0]"
                  class="mt-0 pt-0"
                  hide-details
                  single-line
                  type="number"
                  style="width: 60px"
                  @change="$set(range, 0, $event)"
                ></v-text-field>
              </template>
              <template v-slot:append>
                <v-text-field
                  :value="range[1]"
                  class="mt-0 pt-0"
                  hide-details
                  single-line
                  type="number"
                  style="width: 60px"
                  @change="$set(range, 1, $event)"
                ></v-text-field>
              </template>
            </v-range-slider>
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
            <v-btn rounded x-large @click="startPipeline()" :loading="loading">parse</v-btn>
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
            v-if="index !== 0 && index !== 1 && index !== 5"
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
    right_end_type:'dangling',
    loading: false,
    items:[{
      status:true,
      label:'5\' Terminal nucleotide rule'
    },{
      status:true,
      label:'Strand selection'
    },  {
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
    }, {
      status:false,
      label:'Remove damaging motifs',
    },]
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
      this.loading = true;
      var no_efficience = true;
      const { siRNA_size, mismatch, right_end_type, sequences,consecutive, database, items, bowtie_location, rnaplfold_location, range } = this;
      if (items[0].status && items[1].status && items[2].status && items[3].status)
          no_efficience = false
      const query = {
        siRNA_size, mismatch, sequences,
        right_end_type, 
        terminal_check:items[0].status,
        strand_check:items[1].status,
        end_check:items[2].status,
        remove_damaging_motifs:items[5].status,
        end_stability_treshold:items[2].value,
        accessibility_check:items[3].status,
        target_site_accessibility_treshold:items[3].value,
        accessibility_window:items[4].value,
        database,
        min_gc_range:range[0],
        max_gc_range:range[1],
        no_efficience,
        contiguous_num:consecutive

      }
      console.log(query)
      this.axios.post(this.$localServer + 'run_pipeline', query).then((res) => {
        console.log(res.data);
        this.loading = false;
        var align_data = res.data.align_data;
        var luna_data  = res.data.luna_data;
        this.$store.commit('addReadData', align_data)
        this.$store.commit('addLunaData', luna_data)
        this.$router.push({ name: 'aligntable'})
      }).catch(err => {
        console.log(err);
        this.loading = false;
      })
    }
    
  }
}
</script>
