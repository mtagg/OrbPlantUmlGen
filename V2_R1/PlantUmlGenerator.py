import re
from umlParseConfig import *

def printUmlException(umlString, eMsg):
    # prints and returns an exception message and appended umlString
        print(eMsg)
        return umlString + "' " + eMsg + "\n"

def stateInLine(states, line):
    for state in states:
        if state in line:
            return state
    return False

def getTabs(casestates,substates,ifstates,offset):
    tabTotal = len(casestates) + len(substates) + len(ifstates) + offset
    tabs = ""
    while tabTotal > 0:
        tabs += "\t"
        tabTotal-=1
    return tabs    
    
def checkArrayFor(array, value):
    for val in array:
        if val == value:
            return True
    return False      

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
    # IF_THEN_REGEX = "^\s*IF\s*([\(\)\[\]\s\w\.\*\+\-><=:,^&%#@!]+)\s*THEN\s*$"
    # IF_THEN_REGEX = "^\s*IF\s*([\(\)\[\]\s\w\.\*\+\-><=:,^&!]+)\s*THEN\s*$"
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
    # TODO: Return line index variable so the caller can skip the lines we used up finding our condition
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

def appendUmlStr(umlStr, str):
    # Adds tabs and new line char to all uml appended strings
    # appends to the provided string to umlStr
    pass
def reSearch (regex, line):
    # Returns the Match if successful search
    pass


def makeLocalToBaseBranchString(localStates, newState):
    buffer = ""
    for state in localStates:
        if state != None:
            buffer += f"\t{state} --> {newState}\n"
    localStates.clear()
    # print(f"BUFFER : {buffer}")      
    return buffer   
    
def makeBranchString(srcState, destState, condition):
    return f"\t{srcState} --> {destState} : {condition}\n"
def makeBranchString(srcState, destState):
    return f"\t{srcState} --> {destState}\n"
                                                              
def makeLastStateToFirstStateString(lastBaseState, firstState, ifStates, elseStack, ifConditions):
    if lastBaseState[-1] == firstState[-1]:
        # Loop first state to itself
        lastBaseState.pop()
        return makeBranchString(firstState[-1], firstState.pop())
    else:
        # show that the last state of the case will return to the start of the substate
        if len(ifStates) > 0 and (ifStates[-1] == lastBaseState[-1]):
            if elseStack[-1] == False:
                return makeBranchString(lastBaseState.pop(), firstState.pop(), ifConditions.pop())
            else:
                return makeBranchString(lastBaseState.pop(), firstState.pop(), setNotConditionStatement(ifConditions.pop()))
        else:
            return makeBranchString(lastBaseState.pop(), firstState.pop())          
 
    """subStateNode
        
    Returns:
        _type_: _description_
    """
class subStateNode ():
    
    def __init__(self) -> None:
        self.condition = None
        self.isElse = False
        self.level = None
        self.pastNode = None
        self.futureNode = None
        self.baseNode = None
        self.id = ''
        self.Name = '""'
        self.sequenceNumber = None

        
 
               
class PlantUmlGenerator():
    
    def __init__(self) -> None:
        self.NEW_CASE_RE = f"^\s+CASE\s+Cyclic(Inner|Outer)Case\([^(]+\w+\((\w+)\)\)\s+OF"
        # self.NEW_CASE_RE = f"^\s*CASE\s+([\w\.]+)\s+OF\s*$" # TODO: Can i get rid of the \. in group 1???
        self.NEW_SUBSTATE_RE = "\s*\.*(\w+)\s*:[^=;]*$"
        self.ENUM_STATE_SWITCH_RE = ":=\s*\w*\.*(\w+)\s*\.*;\s*$"
        self.GENERAL_IF_THEN_RE = "^\s*IF.*(THEN|)$"
        self.GENERAL_ELSIF_THEN_RE = "\s*ELSIF\s*([\s\(\)\[\]\.\w><=:.,]+)\s*(THEN|\s*\n)\s*$"
        self.CALL_COMMENT_RE = "^\s*<<<([^<>\s]+)>>>\s*$"
        self.END_IF_RE = "\s*END_IF\s*$"
        
    def getPlantUMLString(self,implementation, statesList, methodsList):
        """ Using array as a stack:
        array.append(state) will append to back of array
        array[-1] will return element at the back of array
        array.pop() will pop/return back element at array[-1]
        """
        umlString = ""      # Return string
        ifCounter = 0       # TODO: Move this to be reset for each case once bugs are fixed
        elsifCounter = 0    # TODO: Move this to be reset for each case once bugs are fixed
        callCounter = 0
        subNodes = []
        
        
        if not statesList:
            print(f"Error: No States Found.\nExiting...")
            return ""
        elif len(statesList) != len(methodsList):
            print(f"Error: {len(statesList)} Cases, {len(methodsList)} Methods\nExiting...")
            return ""
        else:
            # Generate UML code for each State found in statesList
            for state in statesList:

                # Reset State Parsing Variables:
                caseStates = []                 # Holds the raw values found in code so they are searchable later
                caseStatesHash = {}             # Holds the raw state key, found in ST, and unique UML state value for generation
                subStates = []                  # Holds substates within a case found in the caseStates stack
                ifStates = []                   # Should be same size as len(ifConditions)
                lastBaseState = []              # Holds the last known base-level state of any Case subState, this could either be: 1. Method-call, 2. FB-call, 3. If-statement
                firstState = []                 # Holds only the first state entered within each subState, the last state of each subState will then revert back to firstState
                # TODO lastIfState = []         # Holds the most recent base-level IF state
                # TODO lastIfCondition = []     # Holds the most recent base-level IF condition
                lastLocalIfState = []           # Saves local nested states within IF states, length should be ( len(ifStates) )
                statesToNextBaseState = []      # DEV: Should collect a list of all nested states that require links to the next base-level state
                ifConditions = []               # Easier to use two lists as stacks rather than a hash table for if statements/conditions
                branchString = ""               # Buffer to store state changes, these are last to append to caseStates[-1] after subStates are all defined
                elseStack = []                  # Tracks Else statements, created with every IF statement, initialized as false but modified if 'ELSE' is later found
                stateBranchString = ""          # Tracks branches to case statements via method calls


                # Loop throught the implementation for each state and build UML 
                print(f"\nParsing for {state}:")
                implementationLines = implementation.splitlines() 
                for i, line in enumerate(implementationLines):
                    
                    # print(line)
                    # Start by attempting to locate the start of any case statement
                    if "CASE Cyclic" in line:
                        print(line)
                        print(state)
                        # Match = re.search(self.NEW_CASE_RE, line) 
                        # if Match: 
                        if state in line:
                            print(line)
                            # print(Match.groups(0))
                            # caseState = Match.groups(2)
                            # BUG: Assume only one case variable and case per FB
                            # caseStates.append(Match.groups(2)) 
                            caseStates.append(state)
                            caseStatesHash.update({ state : state }) # Parent state requires no modified value in UML diagram
                            umlString += getTabs(caseStates,subStates,ifStates,1) + f"state {caseStates[-1]} {GLOBALS_['CaseColourCode']} " + "{\n"        
                            print(f"[Line {i}]\tStarted CASE {caseStates[-1]} OF...")

                    # Skip the nested case(s) - (redundant)
                    elif len(caseStates) > 1:
                        if "END_CASE" in line:
                            # We will basically just keep coninuing, either finding other nested Cases, or completing them.
                            print(f"[Line {i}]\t\t\tEND_CASE found for nested case, at caseStates length : {len(caseStates)}")
                            umlString += getTabs(caseStates,subStates,ifStates,1) + "}\n"
                            caseStatesHash.pop(caseStates.pop())
                                
                    # Case started, begin by looking for END_CASE
                    elif len(caseStates) > 0 and "END_CASE" in line:
                        print(f"[Line {i}]\tEND_CASE found at caseStates length : {len(caseStates)}")
                        if len(caseStates) == 1: 
                            # No nested states, break to next state from the last substate we were in
                            umlString += getTabs(caseStates,subStates,ifStates,1) + "}\n"
                            umlString += branchString
                            subStates.pop()
                            umlString += getTabs(caseStates,subStates,ifStates,1) + "}\n" 
                            # BUG: Loopback to first state code:
                            # if len(caseStates) - len(firstState) == 0: 
                            #     # lastBaseState length must be <= caseState length (one on stack per case/ nested case)
                            #     branchString += makeLocalToBaseBranchString(statesToNextBaseState, firstState[-1]) 
                            #     # branchString += makeLastStateToFirstStateString(lastBaseState,firstState,ifStates,elseStack,ifConditions)      
                                
                            caseStatesHash.pop(caseStates.pop())
                            umlString += stateBranchString
                            if len(subStates) > 0:
                                eMsg = f"[Line {i}] ERROR: Returning from parent state with subState still stacked.\nReturning Early...\n"
                                return printUmlException(umlString, eMsg)
                            break
                        else:
                            eMsg = f"[Line {i}] ERROR: Found END_CASE with len(caseStates) != 1.\nReturning Early..."
                            return printUmlException(umlString, eMsg)
                               
                    # Inside of a Case, look for case subState and IF stuff
                    elif len(caseStates) > 0:
                        Match = re.search(self.NEW_SUBSTATE_RE, line)
                        if Match: 
                            newState = f"{caseStatesHash[caseStates[-1]]}_{Match.group(1)}"
                            print(f"[Line {i}]\t\t\t{newState}")

                            if len(subStates) == 0:
                                # First of the Case's subStates
                                umlString += getTabs(caseStates,subStates,ifStates,1) + f"[*] --> {newState} : START\n"
                            elif len(subStates) == 1: 
                                # Close the previous substate
                                umlString += getTabs(caseStates,subStates,ifStates,1) + "}\n" 
                                subStates.pop()
                            else:
                                eMsg = f"[Line {i}] ERROR: Found new subState with len(subState)={len(subStates)}.\nRETURNING EARLY...\n"
                                return printUmlException(umlString, eMsg)
                            # BUG: Loopback to first state code:
                            # if len(caseStates) - len(firstState) == 0: 
                            #     # lastBaseState length must be <= caseState length (one on stack per case/ nested case) 
                            #     branchString += makeLocalToBaseBranchString(statesToNextBaseState, firstState[-1]) 
                            #     # branchString += makeLastStateToFirstStateString(lastBaseState,firstState,ifStates,elseStack,ifConditions)
                            
                            umlString += getTabs(caseStates,subStates,ifStates,1) + f"state {newState}" + "{\n"                            
                            subStates.append(newState) # Add substate to substate stack    
                            lastLocalIfState.clear()
                            lastBaseState.clear()
                            firstState.clear()
                            ifCounter = 0
                            elsifCounter = 0
                            callCounter = 0
                        
                        #Inside of sub-state, look for sub-state switching
                        elif "ChangeInnerState(" in line or "ChangeOuterState(" in line:
                            #BUG: The code below could be dealt with by using an inner/outer flag in the beginning of this function
                            if "eOuter" in state and "ChangeInner" in line:
                                # Skips inner variable reset found in outer loop, inner loop should never call the outer loop change method.
                                continue
                            Match = re.search("^\s*Change(Inner|Outer)State\(([\w\s\.]+:=\s*|\s*)(\w+\.|\s*)(\w+)\s*\)", line)
                            if Match:
                                destState = f"{caseStatesHash[caseStates[-1]]}_{Match.group(4)}"
                                srcState = "Error"
                                condition = ""
                                if len(ifStates) > 0:
                                    if lastLocalIfState[-1] != None:
                                        srcState = lastLocalIfState[-1]
                                        condition = ifConditions[-1]
                                    else:    
                                        if elseStack[-1] == False: 
                                            # Not in an ELSE block for the current IF statement, using condition == TRUE   
                                            srcState = ifStates[-1]
                                            condition = ifConditions[-1]
                                        else: 
                                            # Branching from the top level's ELSE block, using condition == FALSE
                                            srcState = ifStates[-1]
                                            condition = setNotConditionStatement(ifConditions[-1])
                                            
                                    branchString += f"\t{srcState} --> {destState} : {condition}\n"       
                                       
                                elif len(subStates) > 0:
                                    #  Jump to another destination from the top substate  
                                    branchString += f"\t{subStates[-1]} --> {destState}\n"
                                else:
                                    eMsg = f"[Line {i}] FOUND ENUM STATE SWITCHING WITHOUT PREVIOUS SUBSTATE OR IF STATE.\nRETURNING EARLY...\n"
                                    return printUmlException(umlString, eMsg)
                            else:
                                pass
                                # eMsg = f"[Line {i}] FOUND 'ChangeInnerState()' CALL, UNABLE TO PARSE.\nRETURNING EARLY...\n"
                                # return printUmlException(umlString, eMsg)
                            
                       
                                    
                        # Inside of sub-state, search for IF stuff
                        elif len(subStates) > 0: 
                                Match = re.search(self.GENERAL_IF_THEN_RE, line)
                                if Match:
                                    ifCounter+=1
                                    newIfState = f"{subStates[-1]}_IF_{ifCounter}" 
                                    umlString += getTabs(caseStates,subStates,ifStates,1) + f"state {newIfState} <<choice>>\n"
                                    if len(ifStates) == 0:
                                        
                                        if len(caseStates) - len(firstState) == 0:
                                            # Enter IF from lastBaseState
                                            branchString += f"\t{lastBaseState.pop()} --> {newIfState}\n"
                                            lastBaseState.append(newIfState)          # Update new last BASE state
                                        elif len(caseStates) - len(firstState) > 0:
                                            # Enter IF statement from START and set firstSTate/lastBaseState 
                                            umlString += getTabs(caseStates,subStates,ifStates,1) + f"[*] ---> {newIfState} : START\n"
                                            firstState.append(newIfState)           # Append subState's first state
                                            lastBaseState.append(newIfState)
                                            
                                        # Append branches from previous nested states to new base state
                                        # branchString += makeLocalToBaseBranchString(statesToNextBaseState, newIfState) 
                                    
                                    elif len(ifStates) > 0:
                                        branchString += f"\t{ifStates[-1]} ---> {newIfState} : {(ifConditions[-1])}\n"
                                    else:
                                        eMsg = f"[Line {i}] ERROR: found len(ifStates) == {len(ifStates)}.\n\n"
                                        return printUmlException(umlString, eMsg)

                                    # Append the new IF state variables
                                    ifStates.append(newIfState)
                                    ifConditions.append(getIfCondition(implementationLines, i))
                                    elseStack.append(False)              
                                    lastLocalIfState.append(None)                      
                                    # print(f"[Line {i}]\t\t\t\tDEBUG: #if#{len(ifStates)} : Condition = {ifConditions[-1]}") # DEBUG
                                    # print(f"[Line {i}]\t\t\t\tDEBUG: #if#{len(ifStates)} : #else#{len(elseStack)} : #ifcondition#{len(ifConditions)}") # DEBUG
                                    
                                # Inside of sub-state, search for ELSIF statements
                                else:
                                    Match = re.search(self.GENERAL_ELSIF_THEN_RE, line)
                                    if Match:
                                        # Non nested, new state at same level, previous IF/ELSIF condition NOT TRUE
                                        if len(ifStates) > 0:
                                            elsifCounter+=1
                                            newELSIFState = f"{subStates[-1]}_ELSIF_{elsifCounter}"
                                            branchString += f"\t{ifStates.pop()} ---> {newELSIFState} : {setNotConditionStatement(ifConditions.pop())}\n"
                                            ifStates.append(newELSIFState)         
                                            ifConditions.append(getElsifCondition(implementationLines, i))
                                            umlString += getTabs(caseStates,subStates,ifStates,1) + f"state {newELSIFState} <<choice>>\n"
                                            statesToNextBaseState.append(lastLocalIfState[-1])          # Save the last IF/ELSIF's final local state 
                                            lastLocalIfState[-1] = None                                 # Reset local state for the current ELSIF
                                        else:
                                            eMsg = f"[Line {i}] You messed up.. found ELSIF without IF state on the stack\nReturning Early..."
                                            return printUmlException(umlString, eMsg)

                                    # while in substate, look for ELSE statements
                                    else:
                                        Match = re.search("\s*ELSE\s*$", line)
                                        if Match:  
                                            
                                            if len(ifStates) > 0: 
                                                # Mark that the top-level IF has an ELSE statement
                                                elseStack[-1] = True
                                                statesToNextBaseState.append(lastLocalIfState[-1]) 
                                                lastLocalIfState[-1] = None
                                                
                                            else: 
                                                # "ELSE" [Default] subState found for caseState[-1]
                                                umlString += getTabs(caseStates,subStates,ifStates,1) + "}\n"
                                                subStates.pop()
                                                newDefaultState = f"{caseStatesHash[caseStates[-1]]}_DEFAULT"
                                                umlString += getTabs(caseStates,subStates,ifStates,1) + f"[*] ---> {newDefaultState} : {caseStates[-1]} == DEFAULT\n" 
                                                umlString += getTabs(caseStates,subStates,ifStates,1) + f"state {newDefaultState}" + "{\n"
                                                subStates.append(newDefaultState)
                                                # TODO: Need to make a better subState switching routine/reset of variables
                                                # TODO: Show the last state returning to firstState
                                                lastLocalIfState.clear()
                                                if len(caseStates) - len(firstState) == 0:
                                                    lastBaseState.pop()
                                                    firstState.pop()
                                                
                                        # while in substate, look for END_IF statement          
                                        else:
                                            Match = re.search(self.END_IF_RE, line)
                                            if Match: 
                                                if len(ifStates) < 1:
                                                    eMsg = f"[Line {i}] Found END_IF statement without an IF statement stacked.\nReturning Early..."
                                                    return printUmlException(umlString, eMsg)
                                                else:
                                                    ifStates.pop()      # Pop back to previous layer IF statement
                                                    elseStack.pop()     # Pop current layer's else flag 
                                                    ifConditions.pop()  # Pop current layer's IF condition
                                                    # Append any local states that need transisions to next base-state  
                                                    statesToNextBaseState.append(lastLocalIfState.pop()) 
                                                # print(f"[Line {i}]\t\t\t\tDEBUG: #if#{len(ifStates)} : #else#{len(elseStack)} : #ifcondition#{len(ifConditions)}") # DEBUG
                                                

                    ## Check for commented code in all cases
                    Match = re.search(self.CALL_COMMENT_RE, line)
                    if Match:
                        # print(callString)
                        if len(caseStates) == 0:
                            # TODO: Add method calls from base node
                            # TODO: need a variable to track root-node states
                            pass
                        elif len(caseStates) > 0:
                            callCounter += 1
                            newCall = f"{subStates[-1]}_CALL_{callCounter}"
                            callString = f"{Match.group(1)}"
                            umlString += getTabs(caseStates,subStates,ifStates,1) + f"state \"{callString}\" as {newCall}\n"
                            
                            if (len(ifStates) > 0):
                                if lastLocalIfState[-1] == None:
                                    if elseStack[-1] == False: 
                                        # Branching from IF state  
                                        branchString += f"\t{ifStates[-1]} --> {newCall} : {ifConditions[-1]}\n"
                                    else: 
                                        # Branching from ELSE state
                                        branchString += f"\t{ifStates[-1]} --> {newCall} : {setNotConditionStatement(ifConditions[-1])}\n"
                                else:
                                    # Branch from current-level local state
                                    branchString += f"\t{lastLocalIfState[-1]} --> {newCall} : {setNotConditionStatement(ifConditions[-1])}\n"       
                                # Update last local state
                                lastLocalIfState[-1] = newCall
                            else:
                                # Append branches from previous nested states to new base state
                                # if len(statesToNextBaseState) > 0:
                                #     branchString += makeLocalToBaseBranchString(statesToNextBaseState, newCall)  
                                if len(caseStates) - len(firstState) == 0:
                                    # Branching from last BASE state
                                    branchString += f"\t{lastBaseState[-1]} --> {newCall}\n"
                                    lastBaseState[-1] = newCall

                                elif len(caseStates) - len(firstState) > 0:
                                    # Entry point of subState
                                    umlString += getTabs(caseStates,subStates,ifStates,1) + f"[*] --> {newCall}\n"
                                    firstState.append(newCall)
                                    lastBaseState.append(newCall)
                                else:
                                    eMsg = f"[Line {i}] ERROR: too many firstStates({len(firstState)}) for caseStates({len(caseStates)}).\nReturning Early..."
                                    printUmlException(umlString, eMsg)
                                
                        else:
                            eMsg = f"[Line {i}] ERROR: Negative number of caseStates({len(caseStates)}).\nReturning Early..."
                            printUmlException(umlString, eMsg)
                                                                    
            return umlString