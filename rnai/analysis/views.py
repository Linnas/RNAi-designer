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
	is_sequence = general_helpers.validate_seq(sequences)
	# fasta = general_helpers.validate_fasta_seq(sequences)

	if is_sequence:
	    sequences = '>' + 'my_sequence' + '\n' + sequences
	    sequence_temp_file = general_helpers.save_seq_file(sequences)
	# elif fasta == 1:
	# 	sequence_temp_file = general_helpers.save_seq_file(sequences)
	# elif fasta > 1:
	# 	sequence_temp_file = False
	# 	print("Please enter only one sequence or use the batch mode.")
	else:
		# sequence_temp_file = False
		raise ValueError('Please enter a valid nucleic acid sequence!')
	if sequence_temp_file:
		sifi = pipeline.SifiPipeline()
		align_data, luna_data = sifi.run_pipeline(
			bowtie_db = order['database'],
	        rnaplfold_location = rnaplfold_location,
	        bowtie_location = bowtie_location,
	        query_sequences = sequence_temp_file,
	        sirna_size = order['siRNA_size'],
	        mismatches = order['mismatch']
	    )
		response['align_data'] = align_data
		response['luna_data']  = luna_data.tolist()
	return JsonResponse(response)

@csrf_exempt
def process_data(request):

	response = dict()
	if request.method == 'POST':
		order = json.loads(request.body)
		table_data = sifi.process_data(
			target = order['target'],
			accessibility_check = order['accessibility_check'],
	        accessibility_window = order['accessibility_window'],
	        terminal_check = order['terminal_check'],
	        strand_check = order['strand_check'],
	        end_check = order['end_check'],
	        end_stability_treshold = order['end_stability_treshold'],
	        target_site_accessibility_treshold = order['target_site_accessibility_treshold'],
	        min_gc_range = order['min_gc_range'],
	        max_gc_range = order['max_gc_range'],
	        right_end_type = order['right_end_type'],
	        remove_damaging_motifs = order['remove_damaging_motifs'],
	        contiguous_num = order['contiguous_num']
			)
		response['table_data']     = table_data
		# response['json_lst']       = json_lst
		# response['eff_sirna_plot'] = eff_sirna_plot
		# response['main_histo']     = main_histo
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

@csrf_exempt
def exportTable(request):

	if request.method == 'POST':
		order = json.loads(request.body)
		path = order['path']

		sifi.export(path)

		response = {'code':'200'}

	return JsonResponse(response)