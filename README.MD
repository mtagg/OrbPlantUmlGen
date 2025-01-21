# README for ST2PlantUML_V2_Rx:

### Revision Notes:
#### V3_R3:
   1. Join blocks added to substates
   2. Added general ":=" assignments as states
   3. Removed 'START' from all starting transitions
   4. Sub-state switching arrows all enter/exit from left
#### V2_R4:
   1. Color coded sub state switching 
   2. Added new lines in various states/transitions to make diagrams less horizontal.
   3. removed "eInnerState_" from substate titles.
   4. Moved all inner substate transitions to be declared within the substate's curly brackets, and not appended to the end
      1. All sub-state to sub-state transitions are still appended to the end of each .puml file


### How it works:
    1. First step is parsing the Tc.POU file:
       1. Search FB declaration:
          1. Find OuterLoopState enumeration declaration as 
             1. If none found, assumed to be inherited from FB_StateMachine
             2. If found, assumed to be parsing FB_Statemachine
          2. Find InnerLoopState enumeration declaration
             1. If none found, assumed to be FB_StateMachine
             2. If found, assumed to be an FB_StateMachine inheriter.
          3. If 1 or 2 failed, issues a warning and exits.

       2. IF FB_StateMachine:
          1. Skips lines until Method: OutterLoopSM
          2. Uses OutterLoopState as the case variable
          3. Scans through until END_CASE
             1. 
       3. IF NOT FB_StateMachine:
          1. Skips lines until Method: InnerLoopSM



### RULES/Limitations:
    1. Only **ONE** Case statement may be defined per FB (excluding the outter loop inherited from FB_StateMachine), this should be defined within InnerLoopSM() method
    2. Due to the more complicated call-chains that occur with the FB_StateMachine implementations, the UML diagram generator relys on the NAP_HD Software Standards being followed.
    3. Only case statements for InnerLoopSM() and OuterLoopSM() methods will be parsed, and the variables are "eInnerState" and "eOuterLoopState", respectively. deviations from this format will not be parsed properly.
    4. "CASE {cyclic method call} OF" must exist on a single line
    5. IF/ELSIF statements may extend their conditions onto multiple lines
    6. state changes must be done using the FB_StateMachine methods:
       1. ChangeInnerState()
       2. ChangeOuterState()
    7. Any method/call wanting to be included but be indicated within the code as such: "//<<<{method/call}>>>" ,  on its own line - anything between <<<>>> will be copied as written, use only characters permitted by plantUML.
    8. any code line beginning with "IF" may cause issues if it isnt an IF statement. ie: naming a variable "IF_CONDITION" and then assigning it "IF_CONDITION := FALSE" may result in errors, but the UML output should still be okay.




### Bugs/ known issues:
   1. Nested Cases are not handled correctly, manual adjustments to some state UML code will be necessary (V0.6)
   2. Most logic outside of CASE [StateVariable] OF blocks is ignored, besides methods (V0.6)
   3. No default exit from each substate found in a CASE block will be stated. (V0.6)
   4. 
	
   