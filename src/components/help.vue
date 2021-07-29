<template>

	<v-dialog v-model="dialog" max-width="1000px">
		<template v-slot:activator="{ on, attrs }">
			<v-btn
				text
				v-bind="attrs"
				v-on="on"
				icon
			>
				<v-icon>mdi-help-circle-outline</v-icon>
			</v-btn>
		</template>
		<v-card>
			<v-card-title class="justify-center">Terms Manual</v-card-title>
			<v-card-text>
				<div>
					<v-img src="/params01.png" max-width="500"></v-img>
					<h3><b>Databases</b>:Choose which database to be used as reference in the alignment by Bowtie</h3>
					<h3><b>siRNA size</b>:Candidate siRNA sequence length.Default:21bp</h3>
					<h3><b>Mismatches</b>:Allowd maximum mismatches in alignment.Default:0bp</h3>
					<h3><b>Right end type</b>:To be accomplished by Zero ken</h3>
					<h3><b>GC content range</b>:Allowed siRNA sequence GC content range</h3>
				</div>
				<div style="height:50px;"></div>
				<div>
					<v-img src="/params02.png" max-width="500"></v-img>
					<h3><b>5'Terminal rules</b>:"A/T at S19";"C/G at S1"</h3>
					<h3><b>Strand selection</b>:whether the strand will be selected (True) or not (False) based on energy rules.</h3>
					<h3><b>End stability difference</b>:whether the end stability is higher or equal threshold (default=1).</h3>
					<h3><b>Target site accessibility</b>:whether the pair probability the siRNA at a certain window (default 8) is higher or equal the threshold (default=0.1)</h3>
					<h3><b>Accessibility calculation window</b>:local pari probability calculation window</h3>
					<h3><b>Remove damaging motifs</b>:Some rules that judge a candidate siRNA damaging or not.</h3>
				</div>
			</v-card-text>
			<v-card-actions class="justify-center"><v-btn outlined @click="dialog=false">Close</v-btn></v-card-actions>
		</v-card>

	</v-dialog>
	
</template>
<script>
export default {
	name: 'help',
	data: () => ({
		dialog:false
	})
}
</script>