const axios = require('axios');

export default {
	addDatabase({ commit }, { path, text, size, loc }) {
		return axios.post('http://localhost:8000/analysis/createDatabase', { path, text, loc }).then(res => {
			console.log(res.msg)
			commit('addDatabase', {
				uid: Date.now(),
				text,
				size,
				edit:false, 
				time:new Date().toLocaleDateString().split('/').reverse().join('-')
			})

			
		}).catch(err => console.log(err))
	},
	removeDatabase({ commit }, { database }) {
		commit('removeDatabase', {
			database
		})
	},
	toggleEdit({ commit }, { database, edit }) {
		commit('toggleEdit', {
			database,
			edit
		})
	},
	editDatabase({ commit }, { database, text }) {
		commit('editDatabase', {
			database, 
			text
		})
	}
}