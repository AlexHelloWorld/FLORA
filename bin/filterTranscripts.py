# generate the keep transcript list
# create the gtf with the keep transcripts

import os
import gtfToCpatBed
import filterCPAT
import filterExonNumberAndLength

def generateLncTranscriptome(inputFileName, exonNumberCutoff, lengthCutoff, cpatCutoff, cpatParameters, outputfileName):
    if not os.path.isdir('tmp/'):
        os.mkdir('tmp/')
    # convert the input gtf file (inputFileName) into bed file
    print('convert input gtf file into bed file')
    bedFilePositive = 'tmp/'+ inputFileName + '.positive.bed'
    bedFileNegative = 'tmp/'+ inputFileName + '.negative.bed'
    gtfToCpatBed.gtfToCpatBed(inputFileName, bedFilePositive, '+')
    gtfToCpatBed.gtfToCpatBed(inputFileName, bedFileNegative, '-')
    # summarize the exon number and transcript length from bed file
    # generate the list that contains transcript id that fit exonNumberCutoff and lengthCutoff
    print('summarize the exon number and length of transcripts')
    exonSummarize = 'tmp/' + inputFileName + 'exonAndLength.txt'
    exonFiltered = filterExonNumberAndLength.filterExonNumberAndLength(bedFilePositive, exonNumberCutoff, lengthCutoff, exonSummarize)

    # run CPAT
    print('start run CPAT')
    cpatPositiveFiltered = filterCPAT.filterCPAT(bedFilePositive, cpatParameters, cpatCutoff)
    cpatNegativeFiltered = filterCPAT.filterCPAT(bedFileNegative, cpatParameters, cpatCutoff)


    transcriptFiltered = set.intersection(set(exonFiltered), set(cpatPositiveFiltered), set(cpatNegativeFiltered))
    
    # keep transcripts in transcriptFiltered and write them into output
    print('output presumed long noncoding RNAs')
    output = open(outputfileName, 'w')
    output.close()
    output =  open(outputfileName, 'a')
    for line in open(inputFileName, 'r'):
        if line[0] == '#':
            continue
        transcriptId = gtfToCpatBed.getTranscriptId(line)
        if transcriptId in transcriptFiltered:
            output.write(line)
    output.close()

    
input_file = 'TCGA_GC_v27_merged.gtf'
exon_number_cutoff = 2
length_cutoff = 300
cpat_cutoff = 0.3
cpat_parameters = ['GRCh38.d1.vd1.fa', '/Users/hongyushi/Downloads/NORI/inst/extdata/Human_Hexamer.tab', '/Users/hongyushi//Downloads/NORI/inst/extdata/Human_train.RData']
output_file = 'TCGA_GC_v27_lncRNA_filtered.gtf'

generateLncTranscriptome(input_file, exon_number_cutoff, length_cutoff, cpat_cutoff, cpat_parameters, output_file)

import subprocess
subprocess.call('date')