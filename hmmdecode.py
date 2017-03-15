import math
import sys
import time

def getTransitionProb(curState, nextState, transMap, tagCnt):
    transProb = transMap.get(curState).get(nextState)
    '''if there is none transProb exists, add to transMap with smoothing'''
    if transProb == None:
        transProb = math.log(1.000/(tagCnt.get(curState)+len(tagCnt)))
        transMap.get(curState).update({nextState:transProb})
    return transProb

def hasDigit(word):
    for c in word:
        if c.isdigit():
            return True
    return False

    


def getEmissionProb(state, word, emissionMap):
    wordMap = emissionMap.get(word)
    if wordMap == None:
        '''ZZ patch'''
        if hasDigit(word):
            if state == "ZZ":
                return math.log(1.0)
            else:
                return math.log(0.01)
        '''unseen word, ignore emission rate'''
        return math.log(1.0)
    prob = wordMap.get(state)
    if prob == None:
        '''seen word, unseen tag, direct return 0, currently no smoothing'''
        '''return should be log(0)-> infinite small'''
        return -999999.0
    '''seen word, seen tag, return probability'''
    return prob
        
    
    


if __name__ == '__main__':
    start = time.time()
    modelFile = open("hmmmodel.txt", 'r')
    testFile = open(sys.argv[1], 'r')
    outputFile = open('hmmoutput.txt', 'w')
    '''for smoothing unseen transition'''
    tagCnt = {}
    '''map of map, P(word|tag), stucture: word:{tag:probability}'''
    emissionMap = {}
    '''map of map, stucture: first tag:{second tag:probability}'''
    transMap = {}
    
    for line in modelFile:
        line = line.strip('\n').split(' ')
        if line[0] == '1':
            '''include Q0, but it will be special treated'''
            tagCnt.update({line[1]:int(line[2])})
        elif line[0] == '2':
            if emissionMap.get(line[2]) == None:
                emissionMap.update({line[2]:{line[1]:float(line[3])}})
            else:
                emissionMap.get(line[2]).update({line[1]:float(line[3])})
        elif line[0] == '3':
            if transMap.get(line[1]) == None:
                transMap.update({line[1]:{line[2]:float(line[3])}})
            else:
                transMap.get(line[1]).update({line[2]:float(line[3])})
        
    '''would use log to calculate'''
    for lineIdx, line in enumerate(testFile):
        line = line.strip('\n').split(' ')
        '''candidateTagList: probability, backtrace path[]'''
        candidateTagList = []
        curTagList = []
        for idx, seg in enumerate(line):
            for state in tagCnt:
                if state == "Q0":
                    continue
                if idx == 0:
                    prob = 0 + getTransitionProb("Q0", state, transMap, tagCnt) + getEmissionProb(state, seg, emissionMap)
                    tempList = [prob,[state]]
                    candidateTagList.append(tempList)
                else:
                    maxProb = -sys.maxint
                    maxCandidate = []
                    for candidate in candidateTagList:
                        '''not sure about emission rate 0 should be smoothed, currently not'''
                        prob = candidate[0] + getTransitionProb(candidate[1][idx-1], state, transMap, tagCnt) + getEmissionProb(state, seg, emissionMap)
                        if prob > maxProb:
                            maxProb = prob
                            maxCandidate = candidate
                    if maxProb > -999999:
                        curPath = maxCandidate[1][:idx+1]
                        curPath.append(state)
                        curTagList.append([maxProb, curPath])
            if idx > 0:
                candidateTagList = curTagList
                curTagList = []
        '''find the max result in final matrix and output to file'''
        bestPredict = [-sys.maxint]
        for predict in candidateTagList:
            if predict[0] > bestPredict[0]:
                bestPredict = predict
        '''print bestPredict'''
        for idx, seg in enumerate(line):
            outputFile.write(seg+"/"+bestPredict[1][idx])
            if idx < len(line)-1:
                outputFile.write(" ")
            else:
                outputFile.write("\n")
        '''print "line: "+str(lineIdx)'''
                    
                
    '''print time.time() - start'''
            
            