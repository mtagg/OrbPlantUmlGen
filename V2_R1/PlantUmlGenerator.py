import re
from umlParseConfig import *
from enum import Enum
import traceback 
  
def printUmlException(umlString, eMsg):
    # prints and returns an exception message and appended umlString
        print(eMsg)
        return umlString + "' " + eMsg + "\n"

"""# def stateInLine(states, line):
#     for state in states:
#         if state in line:
#             return state
#     return False

# def getTabs(casestates,substates,ifstates,offset):
#     tabTotal = len(casestates) + len(substates) + len(ifstates) + offset
#     tabs = ""
#     while tabTotal > 0:
#         tabs += "\t"
#         tabTotal-=1
#     return tabs    """
  
def getTabs(level, offset):
    tabTotal = level + offset
    tabs = ""
    while tabTotal > 0:
        tabs += "\t"
        tabTotal-=1
    return tabs    
    
"""# def checkArrayFor(array, value):
#     for val in array:
#         if val == value:
#             return True
#     return False     """ 

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
"""
def makeLocalToBaseBranchString(localStates, newState):
    buffer = ""
    for state in localStates:
        if state != None:
            buffer += f"\t{state} --> {newState}\n"
    localStates.clear()
    # print(f"BUFFER : {buffer}")      
    return buffer   """
    
def makeBranchStringConditional(srcState, destState, condition):
  return f"\t{srcState} --> {destState} : {condition}\n"

def makeBranchString(srcState, destState):
  return f"\t{srcState} --> {destState}\n"    
                                                          
"""def makeLastStateToFirstStateString(lastBaseState, firstState, ifStates, elseStack, ifConditions):
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
            return makeBranchString(lastBaseState.pop(), firstState.pop())   """       
 

class StateNode ():
    """subStateNode
    
    lastNode : StateNode object for the last visited node prior to the current, input should be None for first node
    condition : String containing a IF/ElSIF/ELSE conditional
    input vars:

    class vars:
        name        : This is the displayed name, should have '""' double quotes around the name
        lastNode    : Either None for the first node, or the previously visited node
        futureNode  : The next node we visit, initalized as None. Updated when the next node is visited
        parentNode  : A previous node that we branch from, not necessarily in sequence, but in logical order
        seqNum      : integer to track which node we have visited in the provided code
        id          : unique String id as Node_{id}
        isElse      : indicates if the node is an Else statement
        isElsif     : indicates if the node is an Elsif statement
        isIf        : indicates if the node is an If statement
    """
    # Constructor
    def __init__(self, lastNode, parentState, name=None, condition=None, isElse=False, isElsif=False, isIf=False) -> bool:
        self.name = name             
        self.nextNode = None
        self.parentNode = None
        # print(f"Creating new node: {self.name}")
        if lastNode != None:
          lastNode.setNextNode(self)
          self.seqNum = lastNode.getSeqNum() + 1
          
          if isElse:
            self.isElse = True
            tempParent = lastNode
            while tempParent != None:
              if tempParent.getCondition() is None:
                tempParent = tempParent.getParentNode()
              else:
                # Found an adequate parent node for an ELSE statement
                self.parentNode = tempParent
                self.nodeLevel = self.parentNode.getLevel()
                self.condition = self.parentNode.getNotCondition()
                break # exit while
              if self.parentNode is None:
                print(f"Error! tried to create ELSE node: {self.name}, without a parent condition.\nExiting. . . ")
                return          
              
          elif isElsif:
            self.isElsif = True
            tempParent = lastNode
            while tempParent != None:
              if tempParent.getCondition() is None:
                tempParent = tempParent.getParentNode()
              else:
                # Found an adequate parent node for an ELSE statement
                self.parentNode = tempParent
                self.nodeLevel = self.parentNode.getLevel()
                self.condition = condition
                break # exit while
              if self.parentNode is None:
                print(f"Error! tried to create ELSIF node: {self.name}, without a parent condition.\nExiting. . . ")
                return
                
          elif isIf:
            self.isIf = True
            self.condition = condition
            self.nodeLevel = lastNode.getLevel() + 1
            
          else: # Not a conditional
            self.parentNode = lastNode
            # self.pastNode = lastNode
            self.nodeLevel = self.parentNode.getLevel()
            self.condition = None

        else: # First node
          print("First Node: ")
          self.nodeLevel = 0
        #   self.lastNode = None
          self.condition = condition
          self.seqNum = 0
          self.isIF = isIf
          self.isElsif = isElsif
          self.isElse = isElse
          
        
        self.id = f'{str(parentState)}_Node_{str(self.seqNum)}'
        print(f"Created New Node: {self.name}\n\tid:{self.id}\n\tlevel:{self.nodeLevel}\n\tparent:{self.parentNode}\n")
        
        # End Constructor
          
    def isIF(self) -> bool:
      return self.isIF
    
    def isElse(self) -> bool:
      return self.isElse
    
    def isElsif(self) -> bool:
      return self.isElsif
         
    def getBaseNode(self):
      tempParent = self.parentNode
      while tempParent != None:
        if tempParent.getNodeLevel() == 0:
          return tempParent
        else:
          tempParent = tempParent.getParentNode()
      return tempParent # None
    
    def getParentNode(self):
      return self.parentNode
    
    def getLevel(self) -> int:
      return self.nodeLevel
    
    def getSeqNum(self) -> int:
      return self.seqNum    

    def getId(self) -> str:
      return self.id
    
    def getCondition(self) -> str:
      return self.condition
    
    def getNotCondition(self) -> str:
      if self.condition != None:
          if "NOT" in self.condition:
              return self.condition.replace("NOT ", "").lstrip().rstrip()
          else:
              return "(" + "NOT " + self.condition.lstrip().rstrip() + ")"
      else:
        return ""
      
    def setNextNode(self, node) -> None:
      self.NextNode = node
      return

class UMLGenerationState(Enum):
    FIND_CASE_START = 0
    FIND_STATE_START = 1 
    FIND_STATE_END = 2
    PARSE_SUB_STATE = 3
    FINISH_CASE = 4
               
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
        

  
    def umlDeclareIF(self, node):
        return getTabs(node.getLevel(),1) + f"state {node.getId()} <<choice>>\n"
    
    def umlWriteTransition(self, parentNode, node, transitionCondition):
        if transitionCondition == None:
          return makeBranchString(parentNode.getId(), node.getId())
        else:
          return makeBranchStringConditional(parentNode.getId(), node.getId(), parentNode.getConditional())
      
    def convertSubStateToUML(self, aCaseCodeLines, sCaseVar, sSubState, nStartLine, nEndLine):
        """
        Takes an array of code lines (split by line) from the line after a subState declaration, 
        untill the line prior to the next one (or endcase)
        """
        stateNodes = [StateNode] # BUG: will this be None for the first index????
        stateNodes.append(None)
        umlString = ""
        branchString = ""
        
        for i, line in enumerate(aCaseCodeLines):
          if i == nEndLine:
            return umlString
          elif i >= nStartLine:

            # search for IF statement
            if (Match := re.search(self.GENERAL_IF_THEN_RE, line)):
              # print(line)
              try:
                newNode = StateNode(lastNode=stateNodes[-1], parentState=sSubState, isIf=True, condition=getIfCondition(aCaseCodeLines, i))
                umlString += self.umlDeclareIF(newNode)
                # write transition from parent to new node
                
                if newNode.getParentNode() == None:
                  umlString +=  makeBranchStringConditional("[*]", newNode.getId(), "START")
                else:
                  branchString += self.umlWriteTransition(newNode.getParentNode(), newNode, newNode.getParentNode().getCondition())
                stateNodes.append(newNode)
              except:
  
                eMsg = f"[Line {i}] ERROR: Failed to create new IF node.\nReturning Early..."
                traceback.print_exc()
                return printUmlException(umlString, eMsg)
                 
            # search for ELSIF statement
            elif Match := re.search(self.GENERAL_ELSIF_THEN_RE, line):
              # Non nested, new state at same level, previous IF/ELSIF condition NOT TRUE
              try:
                newNode = StateNode(lastNode=stateNodes[-1], parentState=sSubState, isElsif=True, condition=getElsifCondition(aCaseCodeLines, i))
                umlString += self.umlDeclareIF(newNode)
                # write transition from parent to new node
                if newNode.getParentNode() == None:
                  eMsg = f"[Line {i}] ERROR: Failed to create new ELSIF, parentNode==None.\nReturning Early..."
                  return printUmlException(umlString, eMsg)
                else:
                  branchString += self.umlWriteTransition(newNode.getParentNode(), newNode, newNode.getParentNode().getNotCondition())
                stateNodes.append(newNode)
              except:
                eMsg = f"[Line {i}] ERROR: Failed to create new ELSIF node.\nReturning Early..."
                return printUmlException(umlString, eMsg)

            #search for ELSE statement
            elif Match := re.search("\s*ELSE\s*$", line):  
              try:
                newNode = StateNode(lastNode=stateNodes[-1], parentState=sSubState, isElse=True)
                # We dont actually save a state for else, but we save the conditions for future states
                
                # write transition from parent to new node
                if newNode.getParentNode() == None:
                  eMsg = f"[Line {i}] ERROR: Failed to create new ELSE, parentNode==None.\nReturning Early..."
                  return printUmlException(umlString, eMsg)
                else:
                  # No need to show a transition to an else, but future nodes may require this node's conditions
                  # branchString += self.umlWriteTransition(newNode.getParentNode(), newNode, newNode.getParentNode().getNotCondition())
                  pass
                stateNodes.append(newNode)
              except:
                eMsg = f"[Line {i}] ERROR: Failed to create new ELSE node.\nReturning Early..."
                return printUmlException(umlString, eMsg)

            # search for END_IF statement          
            elif Match := re.search(self.END_IF_RE, line):
              try:
                # clear up all nodes at the current IF/ELSIF/ELSE level
                currentNodeLevel = stateNodes[-1].getLevel()          # determine current highest level
                while stateNodes[-1].getLevel() == currentNodeLevel:
                  if stateNodes[-1].getCondition == None:
                    # any non-conditionals at highest level should return to their base levels
                    branchString += self.umlWriteTransition(stateNodes[-1], stateNodes[-1].getBaseNode(), None)
                  # any IF/ELSIF/ELSE at current level should be popped
                  stateNodes.pop()
                  if stateNodes[-1] == None:
                    break
              except:
                eMsg = f"[Line {i}] ERROR: Failed to END_IF.\nReturning Early..."
                return printUmlException(umlString, eMsg)      
      
      
      
            # # search for sub-state switching
            # elif "ChangeInnerState(" in line or "ChangeOuterState(" in line:
            #     #BUG: The code below could be dealt with by using an inner/outer flag in the beginning of this function
            #     if "eOuter" in caseVar and "ChangeInner" in line:
            #         # Skips inner variable reset found in outer loop, inner loop should never call the outer loop change method.
            #         continue
            #     Match = re.search("^\s*Change(Inner|Outer)State\(([\w\s\.]+:=\s*|\s*)(\w+\.|\s*)(\w+)\s*\)", line)
            #     if Match:
            #         destState = f"{caseStatesHash[caseStates[-1]]}_{Match.group(4)}"
            #         srcState = "Error"
            #         condition = ""
            #         if len(ifStates) > 0:
            #             if lastLocalIfState[-1] != None:
            #                 srcState = lastLocalIfState[-1]
            #                 condition = ifConditions[-1]
            #             else:    
            #                 if elseStack[-1] == False: 
            #                     # Not in an ELSE block for the current IF statement, using condition == TRUE   
            #                     srcState = ifStates[-1]
            #                     condition = ifConditions[-1]
            #                 else: 
            #                     # Branching from the top level's ELSE block, using condition == FALSE
            #                     srcState = ifStates[-1]
            #                     condition = setNotConditionStatement(ifConditions[-1])
                                
            #             branchString += f"\t{srcState} --> {destState} : {condition}\n"       
                            
            #         elif len(subStates) > 0:
            #             #  Jump to another destination from the top substate  
            #             branchString += f"\t{subStates[-1]} --> {destState}\n"
            #         else:
            #             eMsg = f"[Line {i}] FOUND ENUM STATE SWITCHING WITHOUT PREVIOUS SUBSTATE OR IF STATE.\nRETURNING EARLY...\n"
            #             return printUmlException(umlString, eMsg)
            #     else:
            #         pass
            #         # eMsg = f"[Line {i}] FOUND 'ChangeInnerState()' CALL, UNABLE TO PARSE.\nRETURNING EARLY...\n"
            #         # return printUmlException(umlString, eMsg)
      
        return umlString + branchString
      
    def convertCaseToUML(self, parsedCaseCode, caseVar):
        """ Using array as a stack:
        array.append(state) will append to back of array
        array[-1] will return element at the back of array
        array.pop() will pop/return back element at array[-1]
        """
            
        stateNodes = []
        genState = UMLGenerationState.FIND_CASE_START
        umlString = ""      # Return string    
        stateStart = None
        stateEnd = None
        
        # Reset State Parsing Variables:
        caseStates = []                 # Holds the raw values found in code so they are searchable later
        caseStatesHash = {}             # Holds the raw state key, found in ST, and unique UML state value for generation
        subStates = []                  # Holds substates within a case found in the caseStates stack
        ifStates = []                   # Should be same size as len(ifConditions)
        lastBaseState = []              # Holds the last known base-level state of any Case subState, this could either be: 1. Method-call, 2. FB-call, 3. If-statement
        firstState = []                 # Holds only the first state entered within each subState, the last state of each subState will then revert back to firstState
        lastLocalIfState = []           # Saves local nested states within IF states, length should be ( len(ifStates) )
        statesToNextBaseState = []      # DEV: Should collect a list of all nested states that require links to the next base-level state
        ifConditions = []               # Easier to use two lists as stacks rather than a hash table for if statements/conditions
        branchString = ""               # Buffer to store state changes, these are last to append to caseStates[-1] after subStates are all defined
        elseStack = []                  # Tracks Else statements, created with every IF statement, initialized as false but modified if 'ELSE' is later found
        stateBranchString = ""          # Tracks branches to case statements via method calls


        # Loop throught the implementation for each state and build UML 
        print(f"\nParsing for {caseVar}:")
        implementationLines = parsedCaseCode.splitlines() 
        for i, line in enumerate(implementationLines):
            
            # print(line)
            # Start by attempting to locate the start of any case statement
            if "CASE Cyclic" in line:
                if caseVar in line:
                    # BUG: Assume only one case variable and case per FB
                    caseStates.append(caseVar)
                    umlString += getTabs(1,1) + f"state {caseStates[-1]} {GLOBALS_['CaseColourCode']} " + "{\n"        
                    print(f"[Line {i}]\tStarted CASE {caseStates[-1]} OF...")

            # # Skip the nested case(s) - (redundant)
            # elif len(caseStates) > 1:
            #     if "END_CASE" in line:
            #         # We will basically just keep coninuing, either finding other nested Cases, or completing them.
            #         print(f"[Line {i}]\t\t\tEND_CASE found for nested case, at caseStates length : {len(caseStates)}")
            #         umlString += getTabs(caseStates,subStates,ifStates,1) + "}\n"
            #         caseStatesHash.pop(caseStates.pop())
                        
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
                        
            # Inside of a Case, look for case subState
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
                

                  
            ## Check for commented code in all cases
            # Match = re.search(self.CALL_COMMENT_RE, line)
            # if Match:
            #     # print(callString)
            #     if len(caseStates) == 0:
            #         # TODO: Add method calls from base node
            #         # TODO: need a variable to track root-node states
            #         pass
            #     elif len(caseStates) > 0:
            #         callCounter += 1
            #         newCall = f"{subStates[-1]}_CALL_{callCounter}"
            #         callString = f"{Match.group(1)}"
            #         umlString += getTabs(caseStates,subStates,ifStates,1) + f"state \"{callString}\" as {newCall}\n"
                    
            #         if (len(ifStates) > 0):
            #             if lastLocalIfState[-1] == None:
            #                 if elseStack[-1] == False: 
            #                     # Branching from IF state  
            #                     branchString += f"\t{ifStates[-1]} --> {newCall} : {ifConditions[-1]}\n"
            #                 else: 
            #                     # Branching from ELSE state
            #                     branchString += f"\t{ifStates[-1]} --> {newCall} : {setNotConditionStatement(ifConditions[-1])}\n"
            #             else:
            #                 # Branch from current-level local state
            #                 branchString += f"\t{lastLocalIfState[-1]} --> {newCall} : {setNotConditionStatement(ifConditions[-1])}\n"       
            #             # Update last local state
            #             lastLocalIfState[-1] = newCall
            #         else:
            #             # Append branches from previous nested states to new base state
            #             # if len(statesToNextBaseState) > 0:
            #             #     branchString += makeLocalToBaseBranchString(statesToNextBaseState, newCall)  
            #             if len(caseStates) - len(firstState) == 0:
            #                 # Branching from last BASE state
            #                 branchString += f"\t{lastBaseState[-1]} --> {newCall}\n"
            #                 lastBaseState[-1] = newCall

            #             elif len(caseStates) - len(firstState) > 0:
            #                 # Entry point of subState
            #                 umlString += getTabs(caseStates,subStates,ifStates,1) + f"[*] --> {newCall}\n"
            #                 firstState.append(newCall)
            #                 lastBaseState.append(newCall)
            #             else:
            #                 eMsg = f"[Line {i}] ERROR: too many firstStates({len(firstState)}) for caseStates({len(caseStates)}).\nReturning Early..."
            #                 printUmlException(umlString, eMsg)
                        
            #     else:
            #         eMsg = f"[Line {i}] ERROR: Negative number of caseStates({len(caseStates)}).\nReturning Early..."
            #         printUmlException(umlString, eMsg)
                                                            
        return umlString