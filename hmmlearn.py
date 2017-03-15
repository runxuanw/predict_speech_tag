import time
import math
import sys

def getTag(seg):
    return seg[len(seg)-2:]

def getText(seg):
    return seg[:len(seg)-3]

def addMapEntry(entry, map):
    value = map.get(entry)
    if value == None:
        map.update({entry:1})
    else:
        map.update({entry:value+1})
            
def testEmissionProb(emissionMap):
    probMap = {}
    for key, value in emissionMap.iteritems():
        tag = key.split(' ')[0]
        if probMap.get(tag) == None:
            probMap.update({tag:value})
        else:
            probMap.update({tag:probMap.get(tag)+value})
            
    for key, value in probMap.iteritems():
        print key + " " + str(value)
    
            

if __name__ == '__main__':
    start = time.time()
    file = open(sys.argv[1], 'r')
    outputFile = open("hmmmodel.txt", 'w+')
    tagsCnt = {}
    tagsEndCnt = {}
    '''this tag to next tag'''
    transMap = {}
    
    emissionMap = {}
    '''for test the sum prob of map'''
    probMap = {}
    
    for line in file:
        line = line.strip('\n').split(' ')
        addMapEntry("Q0 " + getTag(line[0]), transMap)
        addMapEntry("Q0", tagsCnt)
        for idx, i in enumerate(line):
            tag = getTag(i)
            addMapEntry(tag, tagsCnt)
            addMapEntry(tag+" "+getText(i), emissionMap)
            if idx > 0:
                addMapEntry(getTag(line[idx-1]) + " " + tag, transMap)
            if idx == len(line)-1:
                addMapEntry(tag, tagsEndCnt)
            
    '''add smoothing'''
    for key, value in transMap.iteritems():
        firstTag = key.split(' ')[0]
        '''exclude the cnt for the end of sentence'''
        endCnt = tagsEndCnt.get(firstTag)
        if endCnt == None:
            endCnt = 0
        transMap.update({key:(value+1)*1.000/(tagsCnt.get(firstTag)-endCnt+len(tagsCnt)-1)})
        
    for key, value in emissionMap.iteritems():
        emissionMap.update({key:value*1.000/tagsCnt.get(key.split(' ')[0])})
            
    
    
    '''output to model'''
    for key, value in tagsCnt.iteritems():
        outputFile.write("1 "+key+" "+str(value)+"\n")
        
    for key, value in emissionMap.iteritems():
        outputFile.write("2 " + key + " " + str(math.log(value))+"\n")
    
    for key, value in transMap.iteritems():
        outputFile.write("3 " + key + " " + str(math.log(value))+"\n")
        
              
    '''print time.time() - start'''