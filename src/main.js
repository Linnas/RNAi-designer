import Vue from 'vue'
import Axios from 'axios'
import App from './App.vue'
import store from './store/'
import VueAxios from 'vue-axios'
import vuetify from './plugins/vuetify'

Vue.config.productionTip = false
Vue.use(VueAxios, Axios)

new Vue({
  vuetify,
  store,
  render: h => h(App)
}).$mount('#app')
