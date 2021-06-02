import Vue from 'vue'
import VueRouter from 'vue-router'
import Pipeline from './components/pipeline.vue'
import Tabular from './components/aligntable.vue'
import plotData from './components/plotdata.vue'
Vue.use(VueRouter)

export default new VueRouter({
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
    },
    {
      path: '/plotdata',
      name:'plotData',
      component: plotData
    }
  ]
})
