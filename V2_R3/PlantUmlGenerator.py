# Python Imports
import re
from enum import Enum
import traceback 
# User Imports
from PlantUmlGeneratorHelperMethods import *
from stateNode import StateNode
from umlParseConfig import *
                                      
class UMLGenerationState(Enum):
    FIND_CASE_START = 0 # Parses pre-case logic and finds "CASE {} OF"
    FIND_FIRST_STATE_START = 1 # finds start of a case^ substate
    FIND_STATE_END = 2 # builds an array, or just skips lines to find next or END_CASE
    PARSE_SUB_STATE = 3 # Calls helper to build UML for found state, then new start == prev end, and finds new end
    PARSE_POST_CASE = 4 # Collect code following a case, until end of method
    FINISH_CASE = 5 # END_CASE found, parses post-case logic for file
    
               
class PlantUmlGenerator():
    
    def __init__(self) -> None:
        self.NEW_CYCLIC_CASE_RE = f"^\s+CASE\s+Cyclic(Inner|Outer)Case\([^(]+\w+\((\w+)\)\)\s+OF"
        self.NEW_STANDARD_CASE_RE = f"^\s*CASE\s+([\w\.]+)\s+OF\s*$" # TODO: Can i get rid of the \. in group 1???
        self.NEW_SUBSTATE_RE = "\s*\w*\.*(\w+)\s*:[^=\'\";]*$"
        self.ENUM_STATE_SWITCH_RE = ":=\s*\w*\.*(\w+)\s*\.*;\s*$"
        self.GENERAL_IF_THEN_RE = "^\s*IF.*(THEN|)$"
        self.GENERAL_ELSIF_THEN_RE = "\s*ELSIF\s*([\s\(\)\[\]\.\w><=:.,]+)\s*(THEN|\s*\n)\s*$"
        self.CALL_COMMENT_RE = "^\s*<<<([^<>\s]+)>>>\s*$"
        self.END_IF_RE = "\s*END_IF\s*$"
        # TODO: take implementation string and split into lines here

    def getLastSameLevelCondition(self, nodeArray):
      parent = self.getLastSameLevelConditionalParent(nodeArray)
      if parent != None:
        condition = parent.getCondition()
      if condition == None:
        return ""
      else:
        return condition
        
    def getLastSameLevelConditionalParent(self, nodeArray):
      if nodeArray[-1] == None:
        return None
      nodeLevel = nodeArray[-1].getLevel()
      tempNode = nodeArray[-1]
      while tempNode != None:
        if tempNode.getLevel() != nodeLevel:
          break
        if tempNode.getCondition() != None:
          return tempNode
        tempNode = tempNode.getParentNode()
      return nodeArray[-1]  

    def umlDeclareIF(self, node):
      return getTabs(node.getLevel(),1) + f"state {node.getId()} <<choice>>\n"
    
    def umlDeclareJoin(self, node):
      return getTabs(node.getLevel(),1) + f"state {node.getId()} <<join>>\n"
    
    def umlDeclareNamedNode(self,node, error=False):
      colour = ''
      if error:
        colour = GLOBALS_["ErrorColourCode"]
      return getTabs(node.getLevel(),1) + f"state \"{node.getName()}\" as {node.getId()} {colour}\n"
    
    def umlWriteTransition(self, parentNode, node, transitionCondition=None):
      if transitionCondition == None:
        return makeBranchString(parentNode.getId(), node.getId())
      else:
        return makeBranchString(parentNode.getId(), node.getId(), transitionCondition)
      
    def convertSubStateToUML(self, caseCodeLines, caseVar, subState, startLine, endLine):
        """
        Takes an array of code lines (split by line) from the line after a subState declaration, 
        untill the line prior to the next one (or endcase)
        """
        stateNodes = [StateNode] # BUG: will this be None for the first index????
        stateNodes.append(None)
        sequenceNum = 0
        JoinNode = None
        ReturnToJoin = False
        AppendJoin = False
        umlString = ""
        branchString = ""
        errorExit = subState+'_ERROR'
        
        umlString += f"state \"ERROR\" as {errorExit} <<exitPoint>> {GLOBALS_['ErrorColourCode']}\n"
        # branchString += makeBranchString(errorExit, f'ERROR <<exitPoint>> {GLOBALS_["ErrorColourCode"]}', 'bError:=TRUE')
        
        for i, line in enumerate(caseCodeLines):
          if i == endLine:
            # Contains the umlString with full substate uml declarations and transitions...
            # ... Followed by a block of transitions of states already defined within the block.
            # TODO: future may be okay to add branchString at the time of parsing to umlString
            return umlString, branchString
          
          elif i >= startLine:
            
            # search for IF statement
            if (Match := re.search(self.GENERAL_IF_THEN_RE, line)):
              try:
                sequenceNum+=1
                newNode = StateNode(lastNode=stateNodes[-1], parentState=subState, sequenceNum=sequenceNum, isIf=True, condition=getIfCondition(caseCodeLines, i))
                umlString += self.umlDeclareIF(newNode)
                
                # write transition from parent to new node
                if newNode.getParentNode() == None:
                  umlString +=  makeBranchString("[*]", newNode.getId(), "START")
                else:
                  branchString += self.umlWriteTransition(newNode.getParentNode(), newNode, newNode.getParentNode().getCondition())
                
                stateNodes.append(newNode)
                
                if newNode.getLevel() <= 1:
                  # Need to create a base collection node, because we need to transition to this join as we traverse nested conditions
                  sequenceNum+=1
                  JoinNode = StateNode(lastNode=newNode.getParentNode(), parentState=subState, sequenceNum=sequenceNum, isJoin=True)
                  ReturnToJoin = True
                  
              except:
                eMsg = f"[Line {i}] ERROR: Failed to create new IF node.\nReturning Early..."
                traceback.print_exc()
                return printUmlException(umlString, eMsg)
                 
            # search for ELSIF statement
            elif Match := re.search(self.GENERAL_ELSIF_THEN_RE, line):
              # Non nested, new state at same level, previous IF/ELSIF condition NOT TRUE
              try:
                sequenceNum+=1
                newNode = StateNode(lastNode=stateNodes[-1], parentState=subState, sequenceNum=sequenceNum, isElsif=True, condition=getElsifCondition(caseCodeLines, i))
                umlString += self.umlDeclareIF(newNode)
                
                # Return the Most recent node to Join node if needed
                if ReturnToJoin == True and stateNodes[-1].getCondition() == None:
                  umlString += self.umlDeclareJoin(JoinNode)
                  branchString += self.umlWriteTransition(stateNodes[-1], JoinNode)
                  AppendJoin = True
                ReturnToJoin == True # reset for the elsif block
                    
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
                      
                
                # Return the Most recent node to Join node if needed
                if ReturnToJoin == True and stateNodes[-1].getCondition() == None:
                  umlString += self.umlDeclareJoin(JoinNode)
                  branchString += self.umlWriteTransition(stateNodes[-1], JoinNode)
                  AppendJoin = True
                ReturnToJoin == True # reset for the else block
                
                currentNodeLevel = stateNodes[-1].getLevel()    
                
                # Clear nodes until we reach last conditional parent
                while stateNodes[-1].getLevel() == currentNodeLevel:
                  if stateNodes[-1].getParentNode() == None:
                    break # Break if we are back at the first node
                  if stateNodes[-1].getIsIf() or stateNodes[-1].getIsElsif():
                    # TODO: Do we want to write the transition of the previous states anywhere???
                    # branchString += self.umlWriteTransition(stateNodes[-1], stateNodes[-1].getBaseNode(), None)
                    break
                  stateNodes.pop()
                
                # Invert the last same-level condition
                if stateNodes[-1] != None:
                  stateNodes[-1].invertCondition()
                else:
                  # TODO ERROR
                  pass

              except:
                traceback.print_exc()
                eMsg = f"[Line {i}] ERROR: Failed to invert last IF/ELSIF to ELSE Node.\nReturning Early..."
                return printUmlException(umlString, eMsg)

            # search for END_IF statement          
            elif Match := re.search(self.END_IF_RE, line):
              try:
                
                # Return the Most recent node to Join node if needed
                if ReturnToJoin == True and stateNodes[-1].getCondition() == None:
                  umlString += self.umlDeclareJoin(JoinNode)
                  branchString += self.umlWriteTransition(stateNodes[-1], JoinNode)
                  AppendJoin = True
                    # will add the join node after popping the current layer...
                   
                # clear up all nodes at the current IF/ELSIF/ELSE level
                currentNodeLevel = stateNodes[-1].getLevel()          
                
                while stateNodes[-1].getLevel() == currentNodeLevel:
                  if stateNodes[-1].getParentNode() == None:
                    stateNodes.pop()      
                    # If we get back to first substate node, we will just start fresh with the next node.
                    break
                  stateNodes.pop()      
                  
                # Add in the JoinNode for future nodes.    
                if AppendJoin == True:
                  # umlString += self.umlDeclareJoin(JoinNode)
                  stateNodes.append(JoinNode)
                  AppendJoin = False
                  ReturnToJoin = False   
                
              except:
                eMsg = f"[Line {i}] ERROR: Failed to END_IF.\nReturning Early..."
                traceback.print_exc()
                return printUmlException(umlString, eMsg)      
                    
            # search for FB_StateMachine style sub-state switching
            elif "ChangeInnerState(" in line or "ChangeOuterState(" in line:
                # print(line)
                if "eOuter" in caseVar and "ChangeInner" in line:
                    # Skips inner variable reset found in outer loop...
                    # ...inner loop should never call the outer loop change method.
                    continue
                try:   
                  ReturnToJoin = False
                  if Match := re.search("^\s*Change(Inner|Outer)State\(([\w\s\.]+:=\s*|\s*)(\w+\.|\s*)(\w+)\s*\)", line):
                    # Add to the branch string showing transition at subState level, using current condition (if any)
                    destState = f"{caseVar}_{Match.group(4)}"
                    srcState = subState
                    newName = f"ChangeState"
                    transition = f"{srcState}->{destState}"
                    sequenceNum+=1
                    newNode = StateNode(lastNode=stateNodes[-1], parentState=subState, sequenceNum=sequenceNum, name=newName)
                    umlString += self.umlDeclareNamedNode(newNode)
                                   
                    if newNode.getParentNode() != None:
                      umlString += self.umlWriteTransition(newNode.getParentNode(), newNode, newNode.getParentNode().getCondition())
                      umlString += makeBranchString(newNode.getId(), '[*]', transition)
                      branchString += makeBranchString(srcState,destState, transition, downArrow=True)
                    else:
                      umlString += makeBranchString('[*]', '[*]', transition)
                      branchString += makeBranchString(srcState, destState, transition,downArrow=True)
                    
                except:  
                  traceback.print_exc()    
                  eMsg = f"[Line {i}] ERROR: Failed to parse Change(Inner|Outer)State() Call.\nRETURNING EARLY...\n"
                  return printUmlException(umlString, eMsg)
            
            # # TODO: Search for Enumeration state changes here   
            # elif Match := re.search(self.ENUM_STATE_SWITCH_RE, line):
            #   pass
            
            # # TODO: Search for Integer State change
            # elif Match := re.search("^\s"+caseVar+"\s*:=\s*(\w+)\w*;", line):
            #   pass  
            
            # Search for any fbEventHandler Calls for napID specific parsing
            elif Match := re.search("^\s*fbEventHandler\((.*E_Event\.(\w*|).*)\)\s*;\s*$", line):
              try:
                newName = f"fbEventHandler({Match.group(2)})"
                sequenceNum+=1
                newNode = StateNode(lastNode=stateNodes[-1], parentState=subState, sequenceNum=sequenceNum, name=newName)
                umlString += self.umlDeclareNamedNode(newNode)
                if newNode.getParentNode() == None:
                  umlString +=  makeBranchString("[*]", newNode.getId(), "START")
                else:
                  branchString += self.umlWriteTransition(newNode.getParentNode(), newNode, newNode.getParentNode().getCondition())
                stateNodes.append(newNode)
              except:    
                traceback.print_exc()      
                eMsg = f"[Line {i}] ERROR: Failed to parse call to fbEventHandler().\nReturning Early..."
                printUmlException(umlString, eMsg)
              
            # Search for any calling method/FB
            elif Match := re.search("^\s*([\w\.]+)\(.*\)\s*;", line):
              filteredMatch = Match.group(1) + "()"
              try:
                sequenceNum+=1
                # newNode = StateNode(lastNode=stateNodes[-1], parentState=subState, name=Match.group(1))
                newNode = StateNode(lastNode=stateNodes[-1], parentState=subState, sequenceNum=sequenceNum, name=filteredMatch)
                umlString += self.umlDeclareNamedNode(newNode)
                if newNode.getParentNode() == None:
                  umlString +=  makeBranchString("[*]", newNode.getId(), "START")
                else:
                  branchString += self.umlWriteTransition(newNode.getParentNode(), newNode, newNode.getParentNode().getCondition())
                stateNodes.append(newNode)
              except:    
                traceback.print_exc()      
                eMsg = f"[Line {i}] ERROR: Failed to parse in-code Method/FB Call.\nReturning Early..."
                printUmlException(umlString, eMsg)
            
            # Check for commented code in all cases
            elif Match := re.search(self.CALL_COMMENT_RE, line):
              try:
                sequenceNum+=1
                newNode = StateNode(lastNode=stateNodes[-1], parentState=subState, sequenceNum=sequenceNum, name=Match.group(1))
                umlString += self.umlDeclareNamedNode(newNode)
                if newNode.getParentNode() == None:
                  umlString +=  makeBranchString("[*]", newNode.getId(), "START")
                else:
                  branchString += self.umlWriteTransition(newNode.getParentNode(), newNode, newNode.getParentNode().getCondition())
                stateNodes.append(newNode)
              except:    
                traceback.print_exc()      
                eMsg = f"[Line {i}] ERROR: Failed to parse '<<<{Match.groups(1)}>>>' Commented Code.\nReturning Early..."
                printUmlException(umlString, eMsg)
                
            # Check for bError being flagged
            elif Match := re.search("(bError\s*:=\s*TRUE)", line):
              try:
                ReturnToJoin = False
                lastConditionalState = self.getLastSameLevelConditionalParent(stateNodes)
                if lastConditionalState != None:
                  branchString += makeBranchString(stateNodes[-1].getId(), errorExit, lastConditionalState.getCondition())
                else: 
                  # Probably shouldnt be showing an error without a condition, lol....
                  print(f"[Line {i}] WTF you doing with bError=TRUE but no condition??!?!?!?!")
                  branchString += makeBranchString(stateNodes[-1].getId(), errorExit)
              except:
                traceback.print_exc()
                eMsg = f"[Line {i}] ERROR: Failed to parse bError line: \n\t{Match.groups(0)}\nReturning Early..."
                printUmlException(umlString, eMsg)
            
            # Append all other extraneous assignments
            elif ":=" in line and "sErrorDetails" not in line:
              try:
                sequenceNum+=1
                newName = line.strip()
                newNode = StateNode(lastNode=stateNodes[-1], parentState=subState, sequenceNum=sequenceNum, name=newName)
                umlString += self.umlDeclareNamedNode(newNode)
                if newNode.getParentNode() == None:
                  umlString +=  makeBranchString("[*]", newNode.getId(), "START")
                else:
                  branchString += self.umlWriteTransition(newNode.getParentNode(), newNode, newNode.getParentNode().getCondition())
                stateNodes.append(newNode)
                ReturnToJoin = True
              except:    
                traceback.print_exc()      
                eMsg = f"[Line {i}] ERROR: Failed to parse ':=' Assignment Line'.\nReturning Early..."
                printUmlException(umlString, eMsg)
                
    def convertCaseToUML(self, parsedCaseCode, caseVar):
      """
        Inputs:
          self
          parsedCaseCode: a block of code that should contain only a full method with one case
          caseVar: the parsed case variable, should be found within "CASE \. OF"
          
      """
      # TODO: implement multiple case parsing (recursive?????)
      # TODO: Take a previous node that leads to this case method as input
      # TODO: Output the final node that leads out of this case/method
      """ Using array as a stack:
      array.append(state) will append to back of array
      array[-1] will return element at the back of array
      array.pop() will pop/return back element at array[-1]
      """
            

      GenState = UMLGenerationState.FIND_CASE_START
      umlString = ""                  # Return string    
      stateStart = None               # Input to convertSubStateToUML()
      stateEnd = None                 # Input to convertSubStateToUML()
      # stateNodes = []   
      subStates = []                  # Holds substates within a case found in the caseStates stack
      caseStates = []                 # Holds the raw values found in code so they are searchable later
      # caseStatesHash = {}             # Holds the raw state key, found in ST, and unique UML state value for generation
      branchString = ""               # Buffer to store state changes, these are last to append to caseStates[-1] after subStates are all defined
      # stateBranchString = ""          # Tracks branches to case statements via method calls
      preCaseCode = ""
      postCaseCode = ""

      # Loop throught the implementation for each state and build UML 
      print(f"\nParsing for {caseVar}:")
      implementationLines = parsedCaseCode.splitlines() 
      for i, line in enumerate(implementationLines):
        
        match GenState:
          
          case UMLGenerationState.FIND_CASE_START:
            # TODO: Parse pre-case logic here.
            # TODO: This would need to be expanded to accept all types of cases
            # ie: look for CASE {} OF in general, but create a method that..
            # ... Parses for the cyclic outter vs inner special cases
            # if Match := re.search(self.NEW_STANDARD_CASE_RE, line):
            if "CASE Cyclic" in line:
              try:
                if caseVar in line:
                    caseStates.append(caseVar)
                    # umlString += getTabs(0,0) + f"state \"{preCaseCode}\" as PreCaseCode\n"
                    # umlString += getTabs(0,0) + f"[*] --> PreCaseCode : START\n"
                    # umlString += getTabs(0,0) + f"PreCaseCode --> {caseStates[-1]}\n"
                    umlString += getTabs(0,0) + f"state {caseStates[-1]} {GLOBALS_['CaseColourCode']} " + "{\n"        
                    print(f"[Line {i}]\tStarted CASE {caseStates[-1]} OF...")
                    GenState = UMLGenerationState.FIND_FIRST_STATE_START
              except:   
                eMsg = f"[Line {i}] ERROR: Failed to FIND_CASE_START (StateMachine).\nRETURNING EARLY...\n"
                return printUmlException(umlString, eMsg)
              
            # # General Case Start (still depends on parser finding a state variable)
            # elif (Match := re.search(self.NEW_STANDARD_CASE_RE,line)):
            #   try:
            #     if caseVar in line:
            #         caseStates.append(caseVar)
            #         #umlString += getTabs(0,0) + f"state \"{preCaseCode}\" as PreCaseCode\n"
            #         #umlString += getTabs(0,0) + f"[*] --> PreCaseCode : START\n"
            #         #umlString += getTabs(0,0) + f"PreCaseCode --> {caseStates[-1]}\n"
            #         umlString += getTabs(0,0) + f"state {caseStates[-1]} {GLOBALS_['CaseColourCode']} " + "{\n"        
            #         print(f"[Line {i}]\tStarted CASE {caseStates[-1]} OF...")
            #         GenState = UMLGenerationState.FIND_FIRST_STATE_START
            #   except:   
            #     eMsg = f"[Line {i}] ERROR: Failed to FIND_CASE_START (General Case).\nRETURNING EARLY...\n"
            #     return printUmlException(umlString, eMsg)
            elif not (Match := re.search('^\>\>.*$',line)) and line != "":
              preCaseCode += line + "\\n"
          case UMLGenerationState.FIND_FIRST_STATE_START:
              try:
                if Match := re.search(self.NEW_SUBSTATE_RE, line): 
                    subStates.append(f"{caseStates[-1]}_{Match.group(1)}")
                    print(f"[Line {i}]\t\t\t{subStates[-1]}")
                    
                    # Mark the beginning of the substate parser as the next line
                    stateStart = i + 1
                    GenState = UMLGenerationState.FIND_STATE_END
                    if len(subStates) == 1: # Redundant check...
                        umlString += getTabs(len(caseStates),0) + f"[*] --> {subStates[-1]} : START\n"
                        umlString += getTabs(len(caseStates),0) + f"state {subStates[-1]} " + GLOBALS_["SubStateColourCode"] + " {\n"
                    else:
                      eMsg = f"[Line {i}] ERROR: more than 1 substate in first substate.\nlen(subState)={len(subStates)}.\nRETURNING EARLY...\n"
                      return printUmlException(umlString, eMsg)
              except:
                eMsg = f"[Line {i}] ERROR: Failed to FIND_FIRST_STATE_START.\nlen(subState)={len(subStates)}.\nRETURNING EARLY...\n"
                return printUmlException(umlString, eMsg)
              
          case UMLGenerationState.FIND_STATE_END:
            try:
              # Search for next substate
              if Match := re.search(self.NEW_SUBSTATE_RE, line):
                nextState = f"{caseStates[-1]}_{Match.group(1)}"
                stateEnd = i
                
                # TODO: The next few lines could probably be cleaned up if we used 'self' vars
                tempUmlString, tempBranchString = self.convertSubStateToUML(implementationLines,caseVar,subStates[-1],stateStart,stateEnd)
                umlString += tempUmlString
                branchString += tempBranchString
                umlString += getTabs(len(caseStates),0) + "}\n"
                stateStart = stateEnd+1 # previous state end is the next states start
                subStates.append(nextState)
                print(f"[Line {i}]\t\t\t{subStates[-1]}")
                umlString += getTabs(len(caseStates),0) + f"state {subStates[-1]} " + GLOBALS_["SubStateColourCode"] + " {\n"
                
              # TODO: find 'default' ELSE statements here:
                
              # Search for END_CASE
              elif "END_CASE" in line:
                
                stateEnd = i
                # print(f"Start={stateStart}, End:{stateEnd}")
                tempUmlString, tempBranchString = self.convertSubStateToUML(implementationLines,caseVar,subStates[-1],stateStart,stateEnd)
                print(f"[Line {i}]\tEND_CASE found at caseStates length : {len(caseStates)}")
                umlString += tempUmlString
                branchString += tempBranchString
                umlString += getTabs(0,1) + "}\n" # Close last state
                
                
                if len(caseStates) == 1: 
                    # No nested states, break to next state from the last substate we were in
                    umlString += getTabs(0,1) + "}\n" # Close case
                    umlString += branchString
                    GenState = UMLGenerationState.PARSE_POST_CASE
                else:
                    eMsg = f"[Line {i}] ERROR: Found END_CASE with len(caseStates) != 1.\nReturning Early..."
                    return printUmlException(umlString, eMsg)
                  
            except:    
              traceback.print_exc()
              eMsg = f"[Line {i}] ERROR: Failed to FIND_STATE_END.\nReturning Early..."
              return printUmlException(umlString, eMsg)   
            
          case UMLGenerationState.PARSE_SUB_STATE:
            # TODO: May be redundant to have this switch state
            pass
          
          case UMLGenerationState.PARSE_POST_CASE:
            if "States found:" in line: 
              GenState = UMLGenerationState.FINISH_CASE
            elif line != "":
              print(line)
              postCaseCode += line + "\\n"
          
          case UMLGenerationState.FINISH_CASE:
            pass
            
      umlString += f"{caseStates[-1]} : {preCaseCode.strip()}\n"
      umlString += f"{caseStates[-1]} : {postCaseCode.strip()}\n"
      return umlString    


                  
      