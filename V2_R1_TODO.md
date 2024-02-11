# UML Generator TODO, February 9, 2024:

1. [x] Create new umlgenerator class
2. [x] Template the code, using IF/ELSIF statements similar to cases
   1. [x] Add wrappers to places where methods may be used/defined.
   2. [x] Regex Match/checks could be added to if/elsif statements, ie:
      1. ![Alt text](image.png)
3. [x] Using the new subStateNode class, replace parsing from the point of a substate being found
   1. [x] This should encapsulate the defining of a substate to be put inside a method\
   2. [x] Should be able to output standalone UML code, some links may be undefined, but is okay



# UML Generator TODO, February 10, 2024:
1. [ ] Replace Cylcic Case calls with standard CASE VAR OF format.
2. [ ] add default ELSE for case statements
3. [ ] Add custom commented code inputs
4. [ ] Add Method() and FB() call parsing
5. [ ] Add pre/post case parsing


# Later Features:
* [ ] convertCaseToUML() should be able to recursivly generate for nested cases
* [ ] Add enum/ integer state changing
* [ ] Scale the parser to be able to handle multi-case POU files
