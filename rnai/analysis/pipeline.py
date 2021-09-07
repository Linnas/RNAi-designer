import subprocess
import tempfile
import os
import numpy as np
import json
import re
import sys
import csv
from Bio         import SeqIO, SeqUtils
from Bio.Seq     import Seq
from collections import Counter
from analysis    import free_energy
from analysis    import general_helpers



class SifiPipeline(object):
    def __init__(self, bowtie_db, query_sequences, sirna_size, mismatches, accessibility_check,
                 accessibility_window, rnaplfold_location, bowtie_location, strand_check, end_check,
                 end_stability_treshold, target_site_accessibility_treshold, terminal_check,
                 no_efficience, min_gc_range, max_gc_range, right_end_type,remove_damaging_motifs,contiguous_num):


        """
        Class for si-Fi pipeline:

            si-Fi pipeline for RNAi design.
           1. Save query sequence as fasta file.
           2. Split query sequence into xmers and store as fasta file.
           3. Run BOWTIE against DB and extract all positions of off-targets and main targets.
           4. For each siRNA, do strand selection, end stability and target site accessibility for efficiency.
           5. Start RNAplfold to get pair probabilities.
           6. Store data into json file for plotting.

           si-Fi pipeline for off-target prediction.
           1. Save query sequence as fasta file.
           2. Split query sequence into xmers and store as fasta file.
           3. Run BOWTIE against DB and extract all information.
           4. For each hit, do strand selection for efficiency.
           5. Store data into json file for plotting.
        """

        self.bowtie_db = bowtie_db                                              # Bowtie DB
        self.query_sequences = query_sequences                                  # List of all query sequences in multi fasta format
        self.sirna_size = sirna_size                                            # siRNA size
        self.mismatches = mismatches                                            # Allowed mismatches                                                                                # DB path
        self.rnaplfold_location = rnaplfold_location                            # Rnaplfold path
        self.bowtie_location = bowtie_location                                  # Bowtie path

        self.strand_check = strand_check                                        # Strand selection is enabled or disabled
        self.end_check = end_check                                              # End stability selection is enabled or disabled
        self.accessibility_check = accessibility_check                          # Target site accessibility is enabled or disabled
        self.accessibility_window = accessibility_window                        # Accessibility window
        self.end_stability_treshold = end_stability_treshold                    # End stability treshold
        self.ts_accessibility_treshold = target_site_accessibility_treshold     # Target site accessibility threshold
        self.terminal_check = terminal_check
        self.no_efficience = no_efficience
        self.min_gc_range = min_gc_range
        self.max_gc_range = max_gc_range
        self.right_end_type = right_end_type 
        self.remove_damaging_motifs = remove_damaging_motifs
        self.contiguous_num = contiguous_num


        # Some constants
        self.winsize = 80                                                        # Average the pair probabil. over windows of given size
        self.span = 40                                                           # Set the maximum allowed separation of a base pair to span
        self.temperature = 22                                                    # Temperature for calculation free energ
        self.sirna_start_position = 0                                            
        self.overhang = 2                                                        # siRNA overhang
        self.end_nucleotides = 3                                                 # siRNA end nucleotides
        self.snp_location = bowtie_location + '\\snp.json' 
        with open(self.snp_location) as f:
            self.SNPs = json.load(f)                                                                              

    def run_pipeline(self):
        """Start the si-Fi pipeline either in off-target or design mode."""

        for seq_record in SeqIO.parse(self.query_sequences, "fasta"):
            # Store ID and sequence
            self.query_name = seq_record.id
            query_sequence = str(seq_record.seq)
            self.len_seq = len(query_sequence)
            self.sirna_l = []
            for i in range(0, len(query_sequence)-self.sirna_size+1):
                self.sirna_l.append(query_sequence[i:i+self.sirna_size])


            self.bowtie_data = self.run_bowtie(query_sequence)
            self.lunp_data = self.run_rnaplfold(self.query_name, query_sequence)

            return self.bowtie_data, self.lunp_data


    def process_data(self, target):

        no_target = False if bool(self.bowtie_data) else True
        fd, out_path = tempfile.mkstemp(suffix='.json')
        self.output_path = out_path
        fp = open(out_path, 'w')
        json_lst = self.data_to_json(self.query_name, self.bowtie_data, no_target, self.lunp_data, target)
        if self.remove_damaging_motifs:
             json_lst =  list(filter(lambda x: self.is_damaging(x['sirna_sequence']), json_lst))
        json_lst = list(filter(lambda x: self.max_gc_range > x['gc_content']  > self.min_gc_range, json_lst))
        json_lst = list(filter(lambda x: self.gc_contiguous(x['sirna_sequence']), json_lst))
        json.dump(json_lst, fp, indent=4)
        os.close(fd)

        return json_lst
         # json_lst, eff_sirna_histo.tolist(), main_histo.tolist()

    def run_bowtie(self, sequence):
        """Run BOWTIE alignment."""
        os.chdir(self.bowtie_location)
        # -a report all alignments per read;
        # -n max mismatches in seed
        # -y try hard to find valid alignments, at the expense of speed
        # -x index name
        # -f query input files are (multi-)FASTA .fa/.mfa
        fd, out_path    = tempfile.mkstemp()
        fdd, input_path = tempfile.mkstemp(suffix=".fasta")

        with os.fdopen(fdd, mode="r+") as fp:
            for i in range(0, len(sequence)-self.sirna_size+1):
                fp.write('> sirna'+str(i+1)+'\n')
                fp.write(sequence[i:i+self.sirna_size].upper() + '\n')

        process = subprocess.Popen(["bowtie", "-a", "-v", str(self.mismatches),  "-y",
                                    self.bowtie_db, "-f",
                                    input_path, out_path])
        process.wait()

        with os.fdopen(fd) as fp:
            bowtie_data = fp.readlines()
            bowtie_data = list(map(lambda x: x.strip().split('\t'), bowtie_data))

        os.unlink(out_path)
        os.unlink(input_path)
        return bowtie_data

    def run_rnaplfold(self, query_name, sequence):

        os.chdir(self.rnaplfold_location)

        with tempfile.TemporaryDirectory() as fp:
            prc_stdout = subprocess.PIPE
            prc = subprocess.Popen(['RNAplfold', '-W', '%d'%self.winsize,'-L', '%d'% self.span, '-u', '%d'%self.sirna_size, '-T', '%.2f'%self.temperature], stdin=subprocess.PIPE, stdout=prc_stdout, cwd=fp)
            prc.stdin.write(sequence.encode())
            prc.stdin.write('\n'.encode())
            prc.communicate()

            lunp_file = os.path.join(fp, 'plfold_lunp')
            lunp_data = np.loadtxt(lunp_file, dtype='str')
            # Delete first lines self.sirna_size-1 because they are not complete
            lunp_data = np.delete(lunp_data, np.r_[:self.sirna_size-1], 0)

        return lunp_data

    def data_to_json(self, query_name, align_data, no_target, lunp_data, main_targets):
        """Extracts the data from bowtie results and put everything into json format.
           Efficiency is calculated for each siRNA.
           If no target is found, for design mode the siRNA fasta file is used instead of Bowtie data."""

        json_lst = []
        for entity in align_data:
            if not no_target:
                sirna_name = entity[0]
                strand = entity[1]
                hit_name = entity[2]
                reference_strand_pos = int(entity[3])
                query_position = int(sirna_name.split('sirna')[1])
                sirna_sequence = entity[4]
                missmatches = entity[7] if self.mismatches else 0

                if hit_name == main_targets:
                    off_target = False
                else:
                    off_target = True
                
            else:
                # We use the siRNA fasta file to get the efficiency information for each siRNA
                sirna_name = entity[0]
                query_position = int(sirna_name.split('sirna')[1])
                sirna_sequence = entity[1]
                # We don't have this information because we got no Bowtie hits
                off_target = False
                strand = None
                hit_name = False
                reference_strand_pos = None
                missmatches = None

            if strand == '+':

                # We need the antisense siRNA (c_seq) for the energy
                # Antisense sequence = sequence position - 2
                # First two siRNas are ignored
                # Example, siRNA3 -> Antisense siRNA1 as input for c_seq
                #antisense_sequence = self.sirna_l[query_position-3][1]

                # Calculate strand selection for each siRNA
                #if self.strand_check:
                    # We must ignore the first two siRNAs because we can not calculate free energy
                if query_position == 1 or query_position == 2:
                    sirna_sequence_n2 = None
                    sirna_complement = sirna_sequence
                else:
                    sirna_sequence_n2 = self.sirna_l[query_position-3].strip()
                    sirna_complement = str(Seq(sirna_sequence_n2).reverse_complement().strip())[::-1].upper()


                lunp_data_xmer = lunp_data[query_position-1, :].astype(np.float).tolist()[self.accessibility_window]

                is_efficient,\
                strand_selection,\
                end_stability,\
                sense5_MFE_enegery,\
                anti_sense5_MFE_enegery,\
                target_site_accessibility,\
                thermo_effcicient = \
                self.calculate_efficiency(sirna_sequence, sirna_sequence_n2, lunp_data_xmer)
                
                delta_MEF_enegery = anti_sense5_MFE_enegery - sense5_MFE_enegery
                gc_percentage = SeqUtils.GC(sirna_sequence)
                SNP_exist = self.is_snp(main_targets, query_position-1)
                json_dict = {
                    "query_name": query_name,
                    "sirna_name":sirna_name,
                    "sirna_position": query_position,
                    "sirna_sequence": sirna_sequence,
                    "sirna_complement": sirna_complement,
                    "is_efficient": is_efficient,
                    "SNP_exist": SNP_exist,
                    "strand_selection": strand_selection,
                    "end_stability": end_stability,
                    "sense5_MFE_enegery": sense5_MFE_enegery,
                    "anti_sense5_MFE_enegery": anti_sense5_MFE_enegery,
                    "delta_MFE_enegery": delta_MEF_enegery,
                    "target_site_accessibility": target_site_accessibility,
                    "accessibility_value": lunp_data_xmer,
                    "is_off_target": off_target,
                    "hit_name": hit_name,
                    "gc_content":gc_percentage,
                    "reference_strand_pos":reference_strand_pos,
                    "strand": strand,
                    "mismatches": missmatches,
                    "thermo_effcicient": thermo_effcicient
                }
                if(is_efficient):
                    json_lst.append(json_dict)
        return json_lst

    def gc_contiguous(self, sequence):
        patterns = ['C'*self.contiguous_num, 'G'*self.contiguous_num]
        re_res = [re.findall(pattern, sequence) for pattern in patterns]
        return bool(re_res)

    def export(self, path):
        if not os.path.exists(path):
            fname, ext = os.path.splitext(path)
            if ext == '':
                path = fname + '.csv'
        with open(self.output_path, 'r') as fp:
            exportJsonData = json.load(fp)
            csv_columns = list(exportJsonData[0].keys())
            try:
                with open(path, 'w') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                    writer.writeheader()
                    for data in exportJsonData:
                        writer.writerow(data)
            except IOError:
                print("I/O error")
    def free_energy3(self, sirna_sequence):
        """Calculate the free energy of a sequence.

           Code was taken from Biopython.
           http://biopython.org/DIST/docs/api/Bio.SeqUtils.MeltingTemp-pysrc.html

           Example for 21mer
           siRNA GGGATGGCTCAAAGGCGTAGT
           Sense5prime_MFE siRNA position [0,1,2] -> GGG
           Antisense5prime_MFE siRNA position [17,18,19] -> GTA"""

        # Sense5_MFE
        sense_five_seq = sirna_sequence[self.sirna_start_position:self.end_nucleotides]
        # Anitsense5_MFE
        antisense_five_seq = sirna_sequence[self.sirna_size-self.overhang-self.end_nucleotides:self.sirna_size-self.overhang]

        #sense5_MFE_enegery = free_energy.calculate_free_energy(sense_five_seq)
        sense5_MFE_enegery = free_energy.calculate_free_energy(sense_five_seq)
        anti_sense5_MFE_enegery = free_energy.calculate_free_energy(antisense_five_seq)

        #print sense_five_seq, sense5_MFE_enegery, antisense_five_seq, anti_sense5_MFE_enegery
        return sense5_MFE_enegery, anti_sense5_MFE_enegery

    def free_energy_dangling_ends(self, sirna_sequence, sirna_sequence_n2):
        """Calculate the free energy of a sequence.
           c_seq is for dangling ends"""
        #print 'rc', Seq(sirna_sequence_n2).reverse_complement()

        # Sense5_MFE
        #sense_five_seq = sirna_sequence[self.sirna_start_position:self.end_nucleotides+1]
        sense_five_seq = sirna_sequence[self.sirna_start_position:self.end_nucleotides]

        #sense_c_seq = Seq(sirna_sequence_n2).reverse_complement().strip()[self.sirna_size-6:self.sirna_size-1]
        sense_c_seq = Seq(sirna_sequence_n2).reverse_complement().strip()[self.sirna_size-5:self.sirna_size-1]

        sense5_MFE_enegery = free_energy.calculate_free_energy(sense_five_seq, check=True, strict=True, c_seq=sense_c_seq[::-1], shift=1)


        if self.right_end_type == 'dangling':
            # Anitsense5_MFE for sifi siRNA not zhangbing siRNA
            antisense_five_seq = Seq(sirna_sequence_n2).reverse_complement().strip()[self.sirna_start_position:self.end_nucleotides]
            antisense_c_seq = sirna_sequence[self.sirna_size-5:self.sirna_size-1]
            anti_sense5_MFE_enegery = free_energy.calculate_free_energy(antisense_five_seq, check=True, strict=True, c_seq=antisense_c_seq[::-1], shift=1)


        if self.right_end_type == 'complement':
            antisense_five_seq = Seq(sirna_sequence[-4::]).reverse_complement()
            anti_sense5_MFE_enegery = free_energy.calculate_free_energy(antisense_five_seq)

            #print 'sense ',  sirna_sequence, sense_five_seq, sense_c_seq[::-1]
            # print 'G ', sense5_MFE_enegery

            #print 'antisense ', sirna_sequence_n2, antisense_five_seq, antisense_c_seq[::-1]
            anti_sense5_MFE_enegery = free_energy.calculate_free_energy(antisense_five_seq)
            #print 'G ', anti_sense5_MFE_enegery

        return sense5_MFE_enegery, anti_sense5_MFE_enegery

    def strand_selection(self, sirna_sequence, sirna_sequence_n2):
        """Returns whether the strand will be selected (True) or not (False) based on energy rules."""
        # For siRNA n>3 we calculate with dangling ends
        if sirna_sequence_n2 != None:
            sense5_MFE_enegery, anti_sense5_MFE_enegery = self.free_energy_dangling_ends(sirna_sequence, sirna_sequence_n2)
        else:
            #pass
            # For the first two siRNAs no dangling ends
            sense5_MFE_enegery, anti_sense5_MFE_enegery = self.free_energy3(sirna_sequence)

        if anti_sense5_MFE_enegery >= sense5_MFE_enegery:
            strand_selection = True
        else:
            strand_selection = False
        #print "G_S/G_AS ", sense5_MFE_enegery, anti_sense5_MFE_enegery
        return strand_selection

    def end_stability(self, sirna_sequence, sirna_sequence_n2):
        """Calculate whether the end stability is higher or equal threshold (default=1).
           Return True if yes and False if it is lower."""
        # For siRNA n>3 we calculate with dangling ends
        if sirna_sequence_n2 != None:
            sense5_MFE_enegery, anti_sense5_MFE_enegery = self.free_energy_dangling_ends(sirna_sequence, sirna_sequence_n2)
        else:
            #pass
            # For the first two siRNAs no dangling ends
            sense5_MFE_enegery, anti_sense5_MFE_enegery = self.free_energy3(sirna_sequence)

        # End stability
        if (anti_sense5_MFE_enegery - sense5_MFE_enegery) >= self.end_stability_treshold:
            end_stability = True
        else:
            end_stability = False
        return end_stability, sense5_MFE_enegery, anti_sense5_MFE_enegery

    def pair_probability(self, lunp_data_xmer):
        """Calculates whether the pair probability the siRNA at a certain window (default 8) is higher or equal
           the threshold (default=0.1)
           Return True if yes and False if it is lower."""
        # Get pair probability of the accessibility window (chosen by user) of siRNA
        #print "accessibility ", lunp_data_xmer
        if lunp_data_xmer >= self.ts_accessibility_treshold:
            return True
        else:
            return False

    def check_efficient(self, strand_selection, end_stability, target_site_accessibility):
        """Calculates whether a siRNA is efficient or not. Default priority rules (if checked by user):
           1. Strand selection must be True.
           2. End stability must be higher or equal threshold (default=1).
           3. Pair probability (lunp data) of xmer (chosen by user, default 8) must be higher or equal threshold (default=0.1).
           If all rules apply, a siRNA is efficient."""

        is_efficient = None
        if self.strand_check and self.end_check and self.accessibility_check:
            if strand_selection and end_stability and target_site_accessibility:
                is_efficient = True
            else:
                is_efficient = False
        if self.strand_check and self.end_check and not self.accessibility_check:
            if strand_selection and end_stability:
                is_efficient = True
            else:
                is_efficient = False
        if self.strand_check and self.accessibility_check and not self.end_check:
            if strand_selection and target_site_accessibility:
                is_efficient = True
            else:
                is_efficient = False
        if self.end_check and self.accessibility_check and not self.strand_check:
            if end_stability and target_site_accessibility:
                is_efficient = True
            else:
                is_efficient = False
        if self.strand_check and not self.end_check and not self.accessibility_check:
            if strand_selection:
                is_efficient = True
            else:
                is_efficient = False
        if self.end_check and not self.strand_check and not self.accessibility_check:
            if end_stability:
                is_efficient = True
            else:
                is_efficient = False
        if self.accessibility_check and not self.strand_check and not self.end_check:
            if target_site_accessibility:
                is_efficient = True
            else:
                is_efficient = False
        if not self.accessibility_check and not self.strand_check and not self.end_check:
            is_efficient = True

        return is_efficient

    def is_damaging(self,sirna_sequence):
        damaging_motifs = ["GGAATGT", "GAGGTAG", "AGGTAGT", "ACCCTGT", "AGCAGCA", "GCAGCAT", "GTGCAAA", "AGTGCAA", "CAGTGCA"  , "AAGTGCT"  , "AAAGTGC"    , "TCACATT", "ATTGCAC", "TCAAGTA", "TCACAGT", "CACAGTG", "AGCACCA", "GTAAACA", "GGCAGTG", "ACCCGTA", "TAAGGCA", "AAGGCAC", "CCCTGAG", "TGGTCCC", "ATGGCTT", "ACATTCA", "TGACCTA", "CCAGTGT", "AACACTG", "AATACTG", "TCCCTTT", "GCTACAT", "GGAAGAC", "CTTTGGT", "AAGGTGC", "AGCTTAT", "AGCTGCC", "GGCTCAG", "TGCATTG", "ACAGTAC", "GGAGTGT", "CGTACCG", "ATTGCTT", "GCTGGTG", "GTGGTTT", "GTAGTGT", "ACAGTAT", "GAGAACT", "TGCATAG", "TAATGCT", "ATGGCAC", "GGACGGA", "CGTGTCT", "GATATGT", "GTAACAG", "TGAAATG", "CCTTCAT", "AATCTCA", "ACTGCAT", "TGTGCTT", "GATTGTC", "GTCAGTT", "TTGTTCG", "TGTGT", "GTGGTTGTT"]

        result = [*filter(lambda x: x in sirna_sequence or str(Seq(x).reverse_complement()) in sirna_sequence, damaging_motifs)]

        #Authored by Zero Keng
        # damaging_motif = False
        # for motif in self.damaging:
        #     c_motif = str(Seq(motif).reverse_complement())
        #     if motif in sirna_sequence or c_motif in sirna_sequence:
        #         damaging_motif = True
        #         continue

        # return damaging_motif
        return not bool(result)

    def is_snp(self, hit_name, start_position):
        snp_sum = 0

        if hit_name in self.SNPs.keys(): 
            for snp in self.SNPs[hit_name]:
                if int(start_position) <= int(snp) <= int(start_position) + int(self.sirna_size) - 1:
                    snp_sum += 1
                else:
                    pass
            return 'Yes' if bool(snp_sum) else 'No' 
        else:
            return 'No'   

    def calculate_efficiency(self, sirna_sequence, sirna_sequence_n2, lunp_data_xmer):
        """"""
        is_efficient = None

        if self.no_efficience:
            is_efficient = False
            strand_selection = None
            end_stability = None
            sense5_MFE_enegery = None
            anti_sense5_MFE_enegery = None
            target_site_accessibility = None
            thermo_effcicient = None
        else:
            strand_selection = self.strand_selection(sirna_sequence, sirna_sequence_n2)
            end_stability, sense5_MFE_enegery, anti_sense5_MFE_enegery = self.end_stability(sirna_sequence, sirna_sequence_n2)
            target_site_accessibility = self.pair_probability(lunp_data_xmer)
            thermo_effcicient = self.check_efficient(strand_selection, end_stability, target_site_accessibility)

            if self.terminal_check:
                if sirna_sequence[self.sirna_size-3] == 'A' or sirna_sequence[self.sirna_size-3] == 'T':
                    #print "A/T at S19"
                    if sirna_sequence[1] == 'A' or sirna_sequence[1] == 'T':
                        #print "A/T at S1"
                        if thermo_effcicient:
                            is_efficient = True
                        else:
                            is_efficient = False
                    else:
                        if self.accessibility_check:
                            if target_site_accessibility:
                                is_efficient = True
                            else:
                                is_efficient = False
                        else:
                            is_efficient = True
                else:
                    if sirna_sequence[1] == 'G' or sirna_sequence[1] == 'C':
                        #print "C/G at S1"
                        if thermo_effcicient:
                            is_efficient = True
                        else:
                            is_efficient = False
                    else:
                        is_efficient = False
            else:
                if thermo_effcicient:
                    is_efficient = True
                else:
                    is_efficient = False
        return is_efficient, strand_selection, end_stability, sense5_MFE_enegery, anti_sense5_MFE_enegery, target_site_accessibility, thermo_effcicient
