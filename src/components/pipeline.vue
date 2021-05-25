<template>
  <v-container>
    <v-row class="mt-6">
      <v-col cols="2"></v-col>
      <v-col cols="2" class="pr-8">
        <v-select
          :items="databases"
          label="Databases"
          solo
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
          counter
          placeholder="Paste your sequence here."
          :value="sequences"
        ></v-textarea>
        <v-row>
          <v-col class="d-flex justify-center">
            <v-btn rounded color="primary" x-large>parse</v-btn>
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
<!--         <v-row dense>
          <v-col cols="6">
            <span style="color: rgba(0, 0, 0, 0.6);" class="ml-8">Accessibility calculation window</span>
          </v-col>
          <v-col cols="6">
            <v-text-field
              solo
              dense
              type="number"
              value="0.3"
            ></v-text-field>
          </v-col>
        </v-row> -->
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
    ]),
  }
}
</script>
