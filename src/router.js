import Vue from 'vue'
import VueRouter from 'vue-router'
import Pipeline from './components/pipeline.vue'
import Tabular from './components/aligntable.vue'

Vue.use(VueRouter)

const router = new VueRouter({
  routes: [
    {
      path: '/',
      name:'pipeline',
      component: Pipeline,
    },
    {
    	path: '/tabular',
    	name:'aligntable',
    	component: Tabular
    }
  ]
})