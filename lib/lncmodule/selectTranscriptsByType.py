# select genes by gene type
# after selection, use the selected genes to clean bam file

import sys
import os.path
import Queue
import threading
import subprocess

# this function will generate a temporal file to store the selected genes
def selectTranscriptsByType(typeList, gtfFile, outputDirectory):
    if not os.path.isdir(outputDirectory):
        os.mkdir(outputDirectory)
    
    if outputDirectory[-1] != '/':
        outputDirectory = outputDirectory + '/'

    # generate the correct name for gtf.selected output
    gtfFileName = gtfFile[gtfFile.rfind('/')+1:]
    outputFile = open(outputDirectory + gtfFileName + '.selected', 'w')
    outputFile.close()
    outputFile = open(outputDirectory + gtfFileName+'.selected', 'a')

    holdGeneId = ''
    with open(gtfFile, 'r') as inputFile:
        for line in inputFile:
            if line[0] == '#':
                continue
            else:
                lineElements = line.strip().split('\t')
                if lineElements[2] == 'gene':
                    # check type
                    geneType = getGtfComponent(line, 'gene_type')
                    if geneType in typeList:
                        holdGeneId = getGtfComponent(line, 'gene_id')
                        outputFile.write(line)
                else:
                    lineId = getGtfComponent(line, 'gene_id')
                    if lineId == holdGeneId:
                        outputFile.write(line)
    outputFile.close()
    return outputDirectory + gtfFileName+'.selected'
    
    # start bedtools intersect with gtfFile.selected

def bedtoolsClean(bamlist, gtfFile, nThread, outputDirectory):
    if not os.path.isdir(outputDirectory):
        os.mkdir(outputDirectory)
    with open(bamlist, 'r') as p:
        paths = p.read().splitlines()
    paths = [x for x in paths if x != '']

    if outputDirectory[-1] != '/':
        outputDirectory = outputDirectory + '/'

    # start call bedtools intersect 
    def callBedtools(q):
        path = q.get()
        name = path[path.rfind('/')+1:]
        print >> sys.stdout, 'bedtools intersect starts run ' + name
        outputFilePath = outputDirectory + name + '.clean.bam'
        outputErrorPath = outputDirectory + name + '.err.log'
        errfile = open(outputErrorPath, 'w')
        with open(outputFilePath, 'w') as outfile:
            subprocess.call(['bedtools', 'intersect', '-a', path, '-b', gtfFile, '-v'], stdout=outfile, stderr=errfile)
        errfile.close()
        q.task_done()
        print("return something")
        return 0
    
    queue =  Queue.Queue()

    for i in range(0, nThread):
        t = threading.Thread(target=callBedtools, args=(queue, ))
        t.daemon = True
        t.start()
    
    for item in paths:
        queue.put(item)
    queue.join()

    return 0
            


def getGtfComponent(input, keyword):
    geneIdPosition = input.find(keyword)
    length = len(keyword) + 2
    geneIdEndPosition = input[geneIdPosition+length:].find('"')
    return input[geneIdPosition+length:geneIdPosition+length+geneIdEndPosition]

