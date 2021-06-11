const axios = require('axios');

export default {
	addDatabase({ commit }, { path, text }) {
		return axios.post('http://localhost:8000/analysis/createDatabase', { path, text}).then(res => {
			var { msg , date, size } = res.data
			console.log(msg, date, size)
			commit('addDatabase', {
				text,
				size,
				type:'ebwt',
				time:date
			})		
		}).catch(err => console.log(err))
	},
	removeDatabase({ commit }, { database }) {
		console.log(database)
		axios.post('http://localhost:8000/analysis/removeDatabase', { name: database.text }).then(res => {
			if (res.data.msg == 'Success'){
				commit('removeDatabase', database)
			} else {
				console.log('Failed to delete database!')
			}
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