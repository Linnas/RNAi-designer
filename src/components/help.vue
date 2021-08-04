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
				<div class="main-content">
					<v-img src="/params01.png" max-width="500"></v-img>
					<p><strong>Databases</strong>:Choose which database to be used as reference in the alignment by Bowtie</p>
					<p><strong>siRNA size</strong>:Candidate siRNA sequence length.Default:21bp</p>
					<p><strong>Mismatches</strong>:Allowd maximum mismatches in alignment.Default:0bp</strong>
					<p><strong>Right end type</strong>:Self-explanatory</p>
					<p><strong>GC content range</strong>:Allowed siRNA sequence GC content range</p>
				</div>
				<div style="height:50px;"></div>
				<div class="main-content">
					<v-img src="/params02.png" max-width="500"></v-img>
					<p><b>5'Terminal rules</b>:"A/T at S19";"C/G at S1"</p>
					<p><b>Strand selection</b>:whether the strand will be selected (True) or not (False) based on energy rules.</p>
					<p><b>End stability difference</b>:whether the end stability is higher or equal threshold (default=1).</p>
					<p><b>Target site accessibility</b>:whether the pair probability the siRNA at a certain window (default 8) is higher or equal the threshold (default=0.1)</p>
					<p><b>Accessibility calculation window</b>:local pari probability calculation window</p>
					<p><b>Remove damaging motifs</b>:Some rules that judge a candidate siRNA damaging or not.</p>
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
<style>
	@media screen and (min-width: 60em) {
		p {
			font-size: 1.125rem;
			color: rgba(0, 0, 0, 1.0);
		}
	}
</style>