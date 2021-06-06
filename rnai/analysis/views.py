from django.shortcuts import render
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json
from analysis import database_helpers
from analysis import  pipeline
from analysis import general_helpers


@csrf_exempt
def create_database(request):
	if request.method == 'POST':
		order = json.loads(request.body)
		db_name = order['text']
		database_file_location  = order['path']
		bowtie_location = order['loc']

	info_message, bowtie_path = database_helpers.create_bowtie_database(db_name,database_file_location,bowtie_location)
	response = dict()
	if bowtie_path:
		response['msg'] = info_message
	else:
		response['msg'] = 'Failed to build database from sequences.'
	return JsonResponse(response)
@csrf_exempt
def get_all_databases_info(request):

	db_location = ''
	if request.method == 'POST':
		order = json.loads(request.body)
		db_location = order['db_location']

	response = database_helpers.all_dbs(db_location)
	return JsonResponse(response)

'''


rnaplfold_location
bowtie_location

'''
@csrf_exempt
def run_pipeline(request):

	global sifi
	order = dict()
	response = dict()
	sequence_temp_file = ''

	if request.method == 'POST':
		order = json.loads(request.body)

	sequences = order['sequences']
	plain_text = general_helpers.validate_seq(sequences)
	fasta = general_helpers.validate_fasta_seq(sequences)

	if plain_text:
	    sequences = '>' + 'my_sequence' + '\n' + sequences
	    sequence_temp_file = general_helpers.save_seq_file(sequences)
	elif fasta == 1:
		sequence_temp_file = general_helpers.save_seq_file(sequences)
	elif fasta > 1:
		sequence_temp_file = False
		print("Please enter only one sequence or use the batch mode.")
	else:
		sequence_temp_file = False
		print('Please enter a valid nucleic acid sequence!')
	print(order)
	if sequence_temp_file:
		sifi = pipeline.SifiPipeline(order['database'], sequence_temp_file, order['siRNA_size'],\
		 order['mismatch'], order['accessibility_check'], order['accessibility_window'], order['rnaplfold_location'],\
		  order['bowtie_location'], order['strand_check'], order['end_check'], order['end_stability_treshold'],\
		   order['target_site_accessibility_treshold'], order['terminal_check'], order['no_efficience'])
		
		result = sifi.run_pipeline()
		response['align_data'] = result
	return JsonResponse(response)

@csrf_exempt
def process_data(request):

	response = dict()
	if request.method == 'POST':
		order = json.loads(request.body)
		target = order['target']
		table_data, json_lst, eff_sirna_plot, main_histo = sifi.process_data(target)
		response['table_data']     = table_data
		response['json_lst']       = json_lst
		response['eff_sirna_plot'] = eff_sirna_plot
		response['main_histo']     = main_histo
	return JsonResponse(response, safe=False)
