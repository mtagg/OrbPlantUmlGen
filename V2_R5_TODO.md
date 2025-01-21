# UML Generator TODO, February 9, 2024:

1. [x] Create new umlgenerator class
2. [x] Template the code, using IF/ELSIF statements similar to cases
   1. [x] Add wrappers to places where methods may be used/defined.
   2. [x] Regex Match/checks could be added to if/elsif statements, ie:
      1. ![Alt text](image.png)
3. [x] Using the new subStateNode class, replace parsing from the point of a substate being found
   1. [x] This should encapsulate the defining of a substate to be put inside a method\
   2. [x] Should be able to output standalone UML code, some links may be undefined, but is okay



# UML Generator Short-term TODO:
1. [x] Replace Cylcic Case calls with standard CASE VAR OF format.
2. [x] Add pre-case parsing
3. [x] Add post-case parsing
4. [ ] add default ELSE for case statements
5. [x] Add ':=' assignments to UML generator
6. [x] Fix conditional statements that may have 'THIS^.' embedded
7. [x] Add custom commented code inputs
8. [x] Add Method() and FB() call parsing
9. [x] bError Tracking/parsing
10. [x] Track sequence number increments at the <convertSubStateToUML()> level, rather than at the Node object level.
11. [ ] Update printUmlException() to return branch, umlstring, AND print UML error.


# Later Features/ Optimizations:
1. [ ] convertCaseToUML() should be able to recursivly generate for nested cases
2. [ ] Add enum/ integer state changing
3. [ ] Scale the parser to be able to handle multi-case POU files
4. [ ] Integrate old UML generator (pre FB_StateMachine) into new generator
