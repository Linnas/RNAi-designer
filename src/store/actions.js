export default {
	addDatabase({ commit }, { text, size }) {
		commit('addDatabase', {
			uid: Date.now(),
			text,
			size,
			edit:false, 
			time:new Date().toLocaleDateString().split('/').reverse().join('-')
		})
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