import re

def printUmlException(umlString, eMsg):
    # prints and returns an exception message and appended umlString
        print(eMsg)
        buffer = ""
        for line in eMsg.splitlines():
          buffer+= f"'{line}\n"
        return f" {umlString} \n{buffer}\n"

def getTabs(level, offset):
    tabTotal = level + offset
    tabs = ""
    while tabTotal > 0:
        tabs += "\t"
        tabTotal-=1
    return tabs    

def setNotConditionStatement(condition):
    if condition:
        if "NOT" in condition:
            return condition.replace("NOT ", "").lstrip().rstrip()
        else:
            return "(" + "NOT " + condition.lstrip().rstrip() + ")"
    else:
        return "(ERROR: No condition found!)"  

def getIfCondition(lines, lineIndex):
    i = lineIndex
    ifBuffer = ""
    maxLinesToSearch = 20 # TODO: update this as necessary
    IF_THEN_REGEX = "^\s*IF\s*(.+)\s*THEN\s*$" # This should capture ANYTHING between "IF" & "THEN"
    while (i-lineIndex) < maxLinesToSearch:     
        if "END_IF" in lines[i] or "ELSE" in lines[i] or "ELSIF" in lines[i]:
            print(f"ERROR: unable to find THEN after finding IF for line {lineIndex}\n Returning empty string...\n")
            return "()"
        else: 
            ifBuffer += " " + lines[i].lstrip()
            # print(ifBuffer)
            Match = re.search(IF_THEN_REGEX, ifBuffer)
            if Match:
                return "(" + Match.group(1).lstrip().rstrip() + ")"
            else:
                i+=1       
    print(f"ERROR: Found IF without a THEN after {maxLinesToSearch} lines, returning empty string\n")
    return ""

def getElsifCondition(lines, lineIndex):
    i = lineIndex
    ifBuffer = ""
    maxLinesToSearch = 20 # TODO: update this as necessary
    IF_THEN_REGEX = "^\s*ELSIF\s*([\s\(\)\[\]\.\w><=:,^&%#@\*]+)\s*THEN\s*$"
    
    while (i-lineIndex) < maxLinesToSearch:
        
            if "END_IF" in lines[i] or "ELSE" in lines[i]: #or "IF " in lines[i]:
                print(f"ERROR: unable to find THEN after finding ELSIF for line {lineIndex}\n Returning empty string...\n")
                return "()"
            
            else: 
                ifBuffer += " " + lines[i].lstrip()
                # print(ifBuffer)
                Match = re.search(IF_THEN_REGEX, ifBuffer)
                if Match:
                    return "(" + Match.group(1).lstrip().rstrip() + ")"
                else:
                    i+=1
                    
    print(f"ERROR: Found ELSIF without a THEN after {maxLinesToSearch} lines, returning empty string\n")
    return ""

    
def makeBranchStringConditional(srcState, destState, condition):
  # print(f"\t{srcState} --> {destState} : {condition}\n")
  return f"\t{srcState} ----> {destState} : {condition}\n"

def makeBranchString(srcState, destState, condition = None, downArrow = False, upArrow=False, leftArrow=False, rightArror=False):
    if condition == None:
        if downArrow:
            return f"\t{srcState} ---> {destState}\n"  
        else:
            return f"\t{srcState} ---> {destState}\n"  
    else:
        if downArrow:
            return f"\t{srcState} ---> {destState} : {condition}\n"
        else: 
            return f"\t{srcState} ---> {destState} : {condition}\n"