import re


def findCallEncoding(line):
    CALL_REGEX = "^\s*([\/]{2,}\s*<<<CALL:\s*([^<>]+)\s*>>>)"
    Match = re.search(CALL_REGEX, line)
    if Match:
        # print(f"<<<{Match.group(2).lstrip().rstrip()}>>>") #DEBUG
        return f"<<<{Match.group(2).lstrip().rstrip()}>>>" # Reformat for further parsing 
    else:
        return None
 

def removeComments(line):
     Match = re.search("^.*([\/]{2,}.*)$", line)
     buffer = ""
     if Match:
         # Check for special instruction
         CustomMatch = re.search("(<<<[^\<\>]+>>>)", line)    
         if CustomMatch:
            return CustomMatch.group(1).strip()
         else:
            return Match.group(0).replace(Match.group(1), "")
     else:
         return line
     
def removeEmptyLines(lines):
    buffer = ""
    for line in lines.splitlines():
        if line.strip() != "":
            buffer += line + "\n"
    return buffer


def collectStates(code, states, substates):
    caseStack = []
    for line in code.splitlines():
        # print(line)
        Match = re.search("^\s*CASE\s*(\w+\.*)\s*OF\s*$", line)
        if Match:
            # print(Match.group(1))
            
            if len(caseStack) == 0:
                caseStack.append(Match.group(1))
                print(f"Found Parent State: {caseStack[-1]}") #, of type: {Match.group(3)}")
                states.append(caseStack[-1].lstrip().rstrip())
                
            elif len(caseStack) > 0:
                #TODO: Check if 'dot' notation is sufficient for nesting cases in parent cases
                nestedState = caseStack[-1] + "_" + Match.group(1)
                caseStack.append(nestedState)
                print(f"\tFound Nested State: {caseStack[-1]}") #, of type: {Match.group(3)}")
                substates.append(caseStack[-1].lstrip().rstrip())
        else:
            try:
                if "END_CASE" in line:
                    # print(line)
                    caseStack.pop()
            except:
                print("ERROR: Tried to pop from empty caseState stack within collectStates().")    
                       
