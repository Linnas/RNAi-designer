export default {
	addDatabase(state, database) {
		state.databases.push(database)
	},
	removeDatabase(state, database) {
		state.databases.splice(state.databases.indexOf(database), 1)
	},
	toggleEdit(state, { database, edit }) {
		database.edit = edit
	},
	editDatabase(state, { database, text = database.text}) {
		database.text = text
	},
	addReadData(state, data) {
		state.alignData = data
	},
	addLunaData(state, data) {
		state.lunaData = data
	}
}