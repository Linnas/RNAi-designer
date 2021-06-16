from django.shortcuts import render
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json
import shutil
from analysis import database_helpers
from analysis import  pipeline
from analysis import general_helpers

from django.conf import settings
from os import path

rnaplfold_location = path.join(settings.BASE_DIR, 'RNAplfold')
bowtie_location    = path.join(settings.BASE_DIR, 'Bowtie')

@csrf_exempt
def create_database(request):
	if request.method == 'POST':
		order = json.loads(request.body)
		db_name = order['text']
		database_file_location  = order['path']

	info_message, bowtie_path, fdate, fsize = database_helpers.create_bowtie_database(db_name,database_file_location,bowtie_location)
	response = dict()
	if bowtie_path:
		response['msg'] = info_message
		response['date'] = fdate
		response['size'] = fsize
	else:
		response['msg'] = 'Failed to build database from sequences.'
	return JsonResponse(response)
	
@csrf_exempt
def get_all_databases_info(request):

	response = database_helpers.all_dbs(bowtie_location)
	return JsonResponse(response)

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

	if sequence_temp_file:
		sifi = pipeline.SifiPipeline(order['database'], sequence_temp_file, order['siRNA_size'],\
		 order['mismatch'], order['accessibility_check'], order['accessibility_window'], rnaplfold_location,\
		  bowtie_location, order['strand_check'], order['end_check'], order['end_stability_treshold'],\
		   order['target_site_accessibility_treshold'], order['terminal_check'], order['no_efficience'], order['min_gc_range'], order['max_gc_range'])
		
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

@csrf_exempt
def removeDatabase(request):

	response = dict()
	if request.method == 'POST':
		order = json.loads(request.body)
		name  = order['name']

	msg, deleted = database_helpers.delete_databases(name, bowtie_location)

	if deleted:
		response['msg'] = 'Success'

	else:
		response['msg'] = 'Failed'

	return JsonResponse(response)

@csrf_exempt
def shareDatabase(request):

	response = dict()
	if request.method == 'POST':
		order = json.loads(request.body)
		name  = order['name']
		out_dir = order['dist_dir']

	shared = database_helpers.share_database(name, out_dir, bowtie_location)

	if shared:
		response['msg'] = 'Success'

	else:
		response['msg'] = 'Failed'

	return JsonResponse(response)