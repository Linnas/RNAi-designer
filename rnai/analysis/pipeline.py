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

    Parameters
    ----------
    bowtie_db
            bowtie database to be used for alignment. e.g. 'hg19'  
    query_sequences
            List of all query sequences in multi fasta format
    sirna_size
            the sequence length of sirna
    mismatches
            Allowed mismatches length
    accessibility_check
            Check if the secondary structure is optimal for siRNA accessibility
    accessibility_window
            Check the unparied probability of windows of given sieze.(default='8')
    rnaplfold_location
            RNAplfold package binary executable location.
    bowtie_location
            Bowtie package binary execuatble location
    strand_check
            Strand selection is enabled or disabled
    end_check
            End stability selection is enabled or disabled
    end_stability_treshold
            MFE difference between sense5' and antisense5'
    target_site_accessibility_treshold
            unpaired probability threshold for local sequences. 0 means no check is needed.
    terminal_check
            check if particular amino acids occur at specified position on siRNA sequence
    min_gc_range
            minimum GC content
    max_gc_range
            maximum GC content
    right_end_type
            terminal sequence type. can be 'dangling' or 'complement'
    remove_damaging_motifs
            remove motifs that cause damaging to cells.
    contiguous_num
            Allowed max contiguous same amino acid to occur on siRNA sequence.
    """

    WINSIZE = 80                                 
    SPAN = 40                                    
    TEMPERATURE = 22                             
    SIRNA_START_POSITION = 0                     
    OVERHANG = 2                                 
    END_NUCLOTIDES = 3                          

    def __init__(self):
        
        self._snp_data = None,
        self._bowtie_data = None,
        self._luna_data = None,
        self._output_data = None

    def run_pipeline(
        self,
        bowtie_db: str = None,
        rnaplfold_location: str = None,
        bowtie_location: str = None,
        query_sequences:str = None,
        sirna_size: int = 21,
        mismatches:int = 0,
    ):
        SNP_LOCATION = os.path.join(bowtie_location, 'snp.json')
        if not os.path.exists(SNP_LOCATION):
            raise ValueError(f'try to open SNP file at {SNP_LOCATION}, failed!')
        with open(SNP_LOCATION) as f:
            self.SNPs = json.load(f)

        for seq_record in SeqIO.parse(query_sequences, "fasta"):
            # Store ID and sequence
            query_name = seq_record.id
            query_sequence = str(seq_record.seq)

            bowtie_data = self.run_bowtie(
                query_sequence=query_sequence,
                bowtie_db=bowtie_db,
                bowtie_location=bowtie_location,
                sirna_size=sirna_size,
                mismatches=mismatches,
            )
            lunp_data = self.run_rnaplfold(
                query_name=query_name, 
                sirna_size=sirna_size,
                query_sequence=query_sequence,
                rnaplfold_location=rnaplfold_location
            )
            self._bowtie_data = bowtie_data
            self._lunp_data = lunp_data

        return bowtie_data, lunp_data


    def process_data(
        self, 
        target:str = None,
        accessibility_check:bool = True,
        accessibility_window:str = 8,
        terminal_check:bool = True,
        strand_check:bool = True,
        end_check:bool = True,
        end_stability_treshold: float = None,
        target_site_accessibility_treshold: float = None,
        min_gc_range: float = 40,
        max_gc_range: float = 60,
        right_end_type: str = None,
        remove_damaging_motifs:bool = True,
        contiguous_num:int = None
    ):
        possible_targets = set(map(lambda x:x[2], self._bowtie_data))
        no_target = False if target in possible_targets else True
        json_lst = []
        for entity in self._bowtie_data:
            sirna_name = entity[0]
            strand = entity[1]
            hit_name = entity[2]
            query_position = int(sirna_name.split('sirna')[1])
            sirna_sequence = entity[4]

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
                    sirna_sequence_n2 = self._bowtie_data[query_position-3][4].strip()
                    sirna_complement = str(Seq(sirna_sequence_n2).reverse_complement().strip())[::-1].upper()

                lunp_data_xmer = self._lunp_data[query_position-1, :].astype(np.float).tolist()[accessibility_window]

                is_efficient,\
                strand_selection,\
                end_stability,\
                sense5_MFE_enegery,\
                anti_sense5_MFE_enegery,\
                target_site_accessibility,\
                thermo_effcicient = \
                self.calculate_efficiency(
                    sirna_sequence=sirna_sequence, 
                    sirna_sequence_n2=sirna_sequence_n2, 
                    lunp_data_xmer=lunp_data_xmer,
                    accessibility_check=accessibility_check,
                    terminal_check=terminal_check,
                    strand_check=strand_check,
                    end_check=end_check,
                    end_stability_treshold=end_stability_treshold,
                    target_site_accessibility_treshold=target_site_accessibility_treshold,
                    right_end_type=right_end_type
                )

                delta_MEF_enegery = anti_sense5_MFE_enegery - sense5_MFE_enegery
                
                gc_percentage = SeqUtils.GC(sirna_sequence)
                SNP_exist = self.is_snp(target, query_position-1, len(sirna_sequence))
                json_dict = {
                    "sirna_position": query_position,
                    "sirna_sequence": sirna_sequence,
                    "is_efficient": is_efficient,
                    "SNP_exist": SNP_exist,
                    "strand_selection": strand_selection,
                    "end_stability": end_stability,
                    "sense5_MFE_enegery": round(sense5_MFE_enegery,4),
                    "anti_sense5_MFE_enegery": round(anti_sense5_MFE_enegery,4),
                    "delta_MFE_enegery": round(delta_MEF_enegery,4),
                    "target_site_accessibility": target_site_accessibility,
                    "accessibility_value": round(lunp_data_xmer,4),
                    "gc_content":round(gc_percentage,2),
                    "thermo_effcicient": thermo_effcicient
                }
                json_lst.append(json_dict)

        if remove_damaging_motifs:
             json_lst =  list(filter(lambda x: self.is_damaging(x['sirna_sequence']), json_lst))
        json_lst = list(filter(lambda x: max_gc_range > x['gc_content']  > min_gc_range, json_lst))
        json_lst = list(filter(lambda x: self.gc_contiguous(x['sirna_sequence'], contiguous_num), json_lst))

        return json_lst
         # json_lst, eff_sirna_histo.tolist(), main_histo.tolist()

    def run_bowtie(
        self,
        query_sequence=None,
        bowtie_db=None,
        bowtie_location=None,
        sirna_size=None,
        mismatches=None,
        ):
        """Run BOWTIE alignment."""
        os.chdir(bowtie_location)
        # -a report all alignments per read;
        # -n max mismatches in seed
        # -y try hard to find valid alignments, at the expense of speed
        # -x index name
        # -f query input files are (multi-)FASTA .fa/.mfa
        fd, out_path    = tempfile.mkstemp()
        fdd, input_path = tempfile.mkstemp(suffix=".fasta")

        with os.fdopen(fdd, mode="r+") as fp:
            for i in range(0, len(query_sequence)-sirna_size+1):
                fp.write('> sirna'+str(i+1)+'\n')
                fp.write(query_sequence[i:i+sirna_size].upper() + '\n')
        try:
            process = subprocess.Popen([
                "bowtie", 
                "-a", 
                "-v", 
                str(mismatches),  
                "-y",
                bowtie_db, 
                "-f",
                input_path, 
                out_path
            ])
            process.wait()
        except BaseException as error:
            raise 'An exception occurred while execution of Bowtie: {}'.format(error)


        with os.fdopen(fd) as fp:
            bowtie_data = fp.readlines()
            bowtie_data = list(map(lambda x: x.strip().split('\t'), bowtie_data))

        os.unlink(out_path)
        os.unlink(input_path)
        return bowtie_data

    def run_rnaplfold(
        self,
        query_name=None, 
        query_sequence=None,
        sirna_size=None,
        rnaplfold_location=None
        ):
        '''
        calculate locally stable secondary structure − pair probabilities

        Computes local pair probabilities for base pairs with a maximal span of L. 
        The probabilities are averaged over all windows of size L that contain the 
        base pair. For a sequence of length n and a window size of L the algorithm 
        uses only O(n+L*L) memory and O(n*L*L) CPU time. 
        Thus it is practical to "scan" very large genomes for short stable RNA structures.
        
        Output consists of a dot plot in postscript file, 
        where the averaged pair probabilities can easily be parsed and visually inspected.
        
        The -u option makes i possible to compute the probability that 
        a stretch of x consequtive nucleotides is unpaired, which is 
        useful for predicting possible binding sites. Again this probability 
        is averaged over all windows containing the region.
                
        The output is a plain text matrix containing on each line a position i 
        followed by the probability that i is unpaired, [i-1..i] is unpaired [i-2..i] 
        is unpaired and so on to the probability that [i-x+1..i] is unpaired.
        '''
        os.chdir(rnaplfold_location)

        with tempfile.TemporaryDirectory() as fp:
            prc_stdout = subprocess.PIPE
            try:
                prc = subprocess.Popen([
                    'RNAplfold', 
                    '-W', '%d'%self.WINSIZE,
                    '-L', '%d'%self.SPAN, 
                    '-u', '%d'%sirna_size, 
                    '-T', '%.2f'%self.TEMPERATURE], 
                    stdin=subprocess.PIPE, 
                    stdout=prc_stdout, 
                    cwd=fp)
                prc.stdin.write(query_sequence.encode())
                prc.stdin.write('\n'.encode())
                prc.communicate()
            except RuntimeError as error:
                raise 'An exception occurred: {}'.format(error)

            lunp_file = os.path.join(fp, 'plfold_lunp')
            lunp_data = np.loadtxt(lunp_file, dtype='str')
            # Delete first lines self.sirna_size-1 because they are not complete
            lunp_data = np.delete(lunp_data, np.r_[:sirna_size-1], 0)

        return lunp_data


    def gc_contiguous(self, sequence, contiguous_num):
        patterns = ['C'*contiguous_num, 'G'*contiguous_num]
        re_res = [re.findall(pattern, sequence) for pattern in patterns]
        return bool(re_res)

    def export(self, path):
        if not os.path.exists(path):
            fname, ext = os.path.splitext(path)
            if ext == '':
                path = fname + '.csv'
            csv_columns = list(self._output_data[0].keys())
            try:
                with open(path, 'w') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                    writer.writeheader()
                    for data in self._output_data:
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
        sense_five_seq = sirna_sequence[self.SIRNA_START_POSITION:self.END_NUCLOTIDES]
        # Anitsense5_MFE
        antisense_five_seq = sirna_sequence[len(sirna_sequence)-self.OVERHANG-self.END_NUCLOTIDES:len(sirna_sequence)-self.OVERHANG]

        #sense5_MFE_enegery = free_energy.calculate_free_energy(sense_five_seq)
        sense5_MFE_enegery = free_energy.calculate_free_energy(sense_five_seq)
        anti_sense5_MFE_enegery = free_energy.calculate_free_energy(antisense_five_seq)

        #print sense_five_seq, sense5_MFE_enegery, antisense_five_seq, anti_sense5_MFE_enegery
        return sense5_MFE_enegery, anti_sense5_MFE_enegery

    def free_energy_dangling_ends(self, sirna_sequence, sirna_sequence_n2, right_end_type):
        """Calculate the free energy of a sequence.
           c_seq is for dangling ends"""
        #print 'rc', Seq(sirna_sequence_n2).reverse_complement()

        # Sense5_MFE
        #sense_five_seq = sirna_sequence[self.self.sirna_start_position:self.end_nucleotides+1]
        sense_five_seq = sirna_sequence[self.SIRNA_START_POSITION:self.END_NUCLOTIDES]

        #sense_c_seq = Seq(sirna_sequence_n2).reverse_complement().strip()[self.sirna_size-6:self.sirna_size-1]
        sense_c_seq = Seq(sirna_sequence_n2).reverse_complement().strip()[len(sirna_sequence)-5:len(sirna_sequence)-1]

        sense5_MFE_enegery = free_energy.calculate_free_energy(sense_five_seq, check=True, strict=True, c_seq=sense_c_seq[::-1], shift=1)


        if right_end_type == 'dangling':
            # Anitsense5_MFE for sifi siRNA not zhangbing siRNA
            antisense_five_seq = Seq(sirna_sequence_n2).reverse_complement().strip()[self.SIRNA_START_POSITION:self.END_NUCLOTIDES]
            antisense_c_seq = sirna_sequence[len(sirna_sequence)-5:len(sirna_sequence)-1]
            anti_sense5_MFE_enegery = free_energy.calculate_free_energy(antisense_five_seq, check=True, strict=True, c_seq=antisense_c_seq[::-1], shift=1)


        if right_end_type == 'complement':
            antisense_five_seq = Seq(sirna_sequence[-4::]).reverse_complement()
            anti_sense5_MFE_enegery = free_energy.calculate_free_energy(antisense_five_seq)

            #print 'sense ',  sirna_sequence, sense_five_seq, sense_c_seq[::-1]
            # print 'G ', sense5_MFE_enegery

            #print 'antisense ', sirna_sequence_n2, antisense_five_seq, antisense_c_seq[::-1]
            anti_sense5_MFE_enegery = free_energy.calculate_free_energy(antisense_five_seq)
            #print 'G ', anti_sense5_MFE_enegery

        return sense5_MFE_enegery, anti_sense5_MFE_enegery

    def strand_selection(self, sirna_sequence, sirna_sequence_n2, right_end_type):
        """Returns whether the strand will be selected (True) or not (False) based on energy rules."""
        # For siRNA n>3 we calculate with dangling ends
        if sirna_sequence_n2 != None:
            sense5_MFE_enegery, anti_sense5_MFE_enegery = self.free_energy_dangling_ends(sirna_sequence, sirna_sequence_n2, right_end_type)
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

    def end_stability(self, sirna_sequence, sirna_sequence_n2, end_stability_treshold, right_end_type):
        """Calculate whether the end stability is higher or equal threshold (default=1).
           Return True if yes and False if it is lower."""
        # For siRNA n>3 we calculate with dangling ends
        if sirna_sequence_n2 != None:
            sense5_MFE_enegery, anti_sense5_MFE_enegery = self.free_energy_dangling_ends(sirna_sequence, sirna_sequence_n2, right_end_type)
        else:
            #pass
            # For the first two siRNAs no dangling ends
            sense5_MFE_enegery, anti_sense5_MFE_enegery = self.free_energy3(sirna_sequence)

        # End stability
        if (anti_sense5_MFE_enegery - sense5_MFE_enegery) >= end_stability_treshold:
            end_stability = True
        else:
            end_stability = False
        return end_stability, sense5_MFE_enegery, anti_sense5_MFE_enegery

    def pair_probability(self, lunp_data_xmer, ts_accessibility_treshold):
        """Calculates whether the pair probability the siRNA at a certain window (default 8) is higher or equal
           the threshold (default=0.1)
           Return True if yes and False if it is lower."""
        # Get pair probability of the accessibility window (chosen by user) of siRNA
        #print "accessibility ", lunp_data_xmer
        if lunp_data_xmer >= ts_accessibility_treshold:
            return True
        else:
            return False

    def check_efficient(
        self, 
        strand_check:bool = True, 
        end_check: bool = True,  
        accessibility_check: bool = True, 
        strand_selection: bool = True, 
        end_stability: bool = True, 
        target_site_accessibility: bool = True
    ):
        """Calculates whether a siRNA is efficient or not. Default priority rules (if checked by user):
           1. Strand selection must be True.
           2. End stability must be higher or equal threshold (default=1).
           3. Pair probability (lunp data) of xmer (chosen by user, default 8) must be higher or equal threshold (default=0.1).
           If all rules apply, a siRNA is efficient."""

        is_efficient = None
        if strand_check and end_check and accessibility_check:
            if strand_selection and end_stability and target_site_accessibility:
                is_efficient = True
            else:
                is_efficient = False
        if strand_check and end_check and not accessibility_check:
            if strand_selection and end_stability:
                is_efficient = True
            else:
                is_efficient = False
        if strand_check and accessibility_check and not end_check:
            if strand_selection and target_site_accessibility:
                is_efficient = True
            else:
                is_efficient = False
        if end_check and accessibility_check and not strand_check:
            if end_stability and target_site_accessibility:
                is_efficient = True
            else:
                is_efficient = False
        if strand_check and not end_check and not accessibility_check:
            if strand_selection:
                is_efficient = True
            else:
                is_efficient = False
        if end_check and not strand_check and not accessibility_check:
            if end_stability:
                is_efficient = True
            else:
                is_efficient = False
        if accessibility_check and not strand_check and not end_check:
            if target_site_accessibility:
                is_efficient = True
            else:
                is_efficient = False
        if not accessibility_check and not strand_check and not end_check:
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

    def is_snp(self, hit_name, start_position, sirna_size):
        snp_sum = 0

        if hit_name in self.SNPs.keys(): 
            for snp in self.SNPs[hit_name]:
                if int(start_position) <= int(snp) <= int(start_position) + int(sirna_size) - 1:
                    snp_sum += 1
                else:
                    pass
            return 'Yes' if bool(snp_sum) else 'No' 
        else:
            return 'No'   

    def calculate_efficiency(
        self,
        sirna_sequence: str = None,
        sirna_sequence_n2: str = None,
        lunp_data_xmer: int = None,
        accessibility_check: bool = True,
        terminal_check: bool = True,
        strand_check: bool = True,
        end_check: bool = True,
        end_stability_treshold: float = None,
        target_site_accessibility_treshold: float = None,
        right_end_type: str = None
    ):
        """
        """
        is_efficient = None 
        sirna_size = len(sirna_sequence)
        strand_selection = self.strand_selection(sirna_sequence, sirna_sequence_n2, right_end_type)
        end_stability, sense5_MFE_enegery, anti_sense5_MFE_enegery = self.end_stability(sirna_sequence, sirna_sequence_n2, end_stability_treshold, right_end_type)
        target_site_accessibility = self.pair_probability(lunp_data_xmer, target_site_accessibility_treshold)
        thermo_effcicient = self.check_efficient(
            strand_check = strand_check, 
            end_check = end_check,  
            accessibility_check = accessibility_check, 
            strand_selection= strand_selection, 
            end_stability = end_stability, 
            target_site_accessibility = target_site_accessibility
        )
        if terminal_check:
            if sirna_sequence[sirna_size-3] == 'A' or sirna_sequence[sirna_size-3] == 'T':
                #print "A/T at S19"
                if sirna_sequence[1] == 'A' or sirna_sequence[1] == 'T':
                    #print "A/T at S1"
                    if thermo_effcicient:
                        is_efficient = True
                    else:
                        is_efficient = False
                else:
                    if accessibility_check:
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
