import os
from umlParseFunctions import *
from PlantUmlGenerator import PlantUmlGenerator
from umlParseConfig import *
import re
from datetime import datetime
# from time import sleep
from enum import Enum


class ParsingStates(Enum):
    FIND_POU=1
    FIND_POU_DECLARATION=2
    FIND_OUTER_ENUM=3
    FIND_INNER_ENUM=4
    FIND_OUTER_METHOD=5
    FIND_INNER_METHOD=6
    PARSE_METHOD = 7
    FIN = 8

    
    
def parseTcPouFile(absFilePath, Name, outputDirAbsolute):
    # Requires an absolute path
    # Saves output files in the working directory
    print(f"\n>\n>\n>\nOpening POU : {Name}\n>\n>\n>\n") 
    with open(absFilePath, "r") as fb:
        outputFileName = f"{outputDirAbsolute}\{Name}.puml"
        print(f"Generating UML : {outputFileName}...")
        with open(outputFileName, "w") as output:
            caseStates = []
            pouName = ""
            implementationString = ""

            methods = []
            methodCases = {}
            methodCaseFound = False
    
            ParseEnum = ParsingStates.FIND_POU
            #validFB = False
            outerMethodFound = False
            innerMethodFound = False
            
            for i, line in enumerate(fb.readlines()):
                
                match ParseEnum:
                    case ParsingStates.FIND_POU:
                        Match = re.search("<POU Name=\"([A-Za-z0-9_]+)\"", line)
                        if Match:
                            pouName = Match.group(1)
                            output.write(GLOBALS_["FileHeader"] + f"{pouName} State Diagram\n\n")
                            output.write(f"\n\nstate {pouName}" + "{\n\n")
                            ParseEnum = ParsingStates.FIND_POU_DECLARATION
                            print(f"[Line {i}] POU: {pouName}")


                    case ParsingStates.FIND_POU_DECLARATION:
                        if "<Declaration><![CDATA[" in line:
                            if "FB_StateMachine" in pouName:
                                ParseEnum = ParsingStates.FIND_OUTER_ENUM
                            else:
                                ParseEnum=ParsingStates.FIND_INNER_ENUM
                            print(f"[Line {i}] Found POU declaration for : {pouName}")
                            
                            
                    case ParsingStates.FIND_OUTER_ENUM:
                        if "E_OuterLoopSM_States" in line:
                            # TODO: regex the state out of the line
                            caseStates.append("eOuterLoopState")
                            print(f"[Line {i}] Found OutterLoop Enumeration for : {pouName}")
                            ParseEnum = ParsingStates.FIND_OUTER_METHOD
                            

                    case ParsingStates.FIND_INNER_ENUM:
                        Match = re.search("^\s*eInnerState\s*:\s*([\w\.]+)\s*;", line)
                        if Match:
                            # enum = Match.group(1)
                            # TODO: regex the state out of the line
                            enum = "eInnerState"
                            caseStates.append(enum)
                            print(f"[Line {i}] Found InnerLoop Enumeration : {enum}")
                            ParseEnum=ParsingStates.FIND_INNER_METHOD
                            
                            
                    case ParsingStates.FIND_OUTER_METHOD:
                      
                        if outerMethodFound:
                            if "<ST><![CDATA[" in line:
                                line = line.replace("<ST><![CDATA[", "")
                                if "]]></ST>" in line:
                                    line = line.replace("]]></ST>", "")
                                callBuffer = findCallEncoding(line)
                                if callBuffer:
                                    implementationString += callBuffer + "\n"
                                else:
                                    implementationString += removeComments(line).strip() + "\n"  
                                print(f"[Line {i}] Found OuterLoopSM() for : {pouName}")     
                                ParseEnum = ParsingStates.PARSE_METHOD  
                        elif "<Declaration><![CDATA[METHOD OuterLopSM" in line:
                            methods.append("OuterLoopSM")
                            implementationString += f"\n>>\n>>Start of Method : {methods[-1]}\n>>\n>>\n" 
                            outerMethodFound = True
                         
                        
                    case ParsingStates.FIND_INNER_METHOD:
                        if innerMethodFound:
                            if "<ST><![CDATA[" in line:
                                line = line.replace("<ST><![CDATA[", "")
                                if "]]></ST>" in line:
                                    line = line.replace("]]></ST>", "")
                                callBuffer = findCallEncoding(line)
                                if callBuffer:
                                    implementationString += callBuffer + "\n"
                                else:
                                    implementationString += removeComments(line).strip() + "\n"
                                print(f"[Line {i}] Found InnerLoopSM() for : {pouName}")     
                                ParseEnum = ParsingStates.PARSE_METHOD
                        elif "<Declaration><![CDATA[METHOD InnerLoopSM" in line:
                            methods.append("InnerLoopSM")
                            implementationString += f"\n>>\n>>Start of Method : {methods[-1]}\n>>\n>>\n" 
                            innerMethodFound = True
                            
                            
                    case ParsingStates.PARSE_METHOD:
                        if "]></ST>" in line:
                            line = line.replace("]]></ST>", "")
                            callBuffer = findCallEncoding(line)
                            if callBuffer:
                                implementationString += callBuffer + "\n"
                            else:
                                implementationString += removeComments(line) + "\n"
                            print(f"[Line {i}] Found End of Method : {methods[-1]}")     
                            ParseEnum = ParsingStates.FIN
                        else:
                            callBuffer = findCallEncoding(line)
                            if callBuffer:
                                implementationString += callBuffer + "\n"
                            else:
                                implementationString += removeComments(line) + "\n" 
                                
                                
                    case ParsingStates.FIN:
                        break # Exit Switch Case
                   
            implementationString = removeEmptyLines(implementationString)
            
            # Save The Parsed String
            with open(f"{outputDirAbsolute}/{Name}_ParsedXML.txt", "w") as imp:
                # imp.write("IMPLEMENTATION STRING:\n\n")    
                for line in implementationString.splitlines():
                    imp.write(f"\t{line}\n") 
                    
                imp.write("\n\nStates found:\n")
                for state in caseStates:
                    imp.write(f"\t{state}\n")
                
                imp.write("Methods Found:\n")
                for meth in methods:
                    imp.write(f"\t{meth}\n")  
                
                imp.write("Method-Case Pairs Found:\n")
                for meth, case in methodCases.items():
                    imp.write(f"\t{meth} : {case}\n")
            
            
            # Get the PlantUML Code       
            umlGenerator = PlantUmlGenerator()
            if len(caseStates) > 0:
              caseVariable = caseStates[-1]
              output.write(umlGenerator.convertCaseToUML(implementationString, caseVariable)) 
            output.write("\n\n}\n")
            output.write(GLOBALS_["FileFooter"])       


    print(f"\n>\n>\n>\nClosed POU : {Name}\n>\n>\n>\n")                
            
def main():
    dev__ = False
    umlGeneratorLink = "https://www.planttext.com/"
    programPath = os.getcwd()
    
    if not dev__:
        pouMainDirPath = input("Please Copy/Paste the *Absolute* path to a Twincat POU Directory.\nNOTE: This directory should contain at least 1 '.TcPou' file-type.\n>> ")      
        pouDirectories = []
        pouDirectories.append(pouMainDirPath)
        
        pouFilePaths = []
        while len(pouDirectories) > 0: 
            os.chdir(pouDirectories[0])
            for file in os.listdir():
                filePath = f"{pouDirectories[0]}\{file}"
                if os.path.isdir(filePath):
                    pouDirectories.append(filePath)
                elif ".TcPOU" in file:
                        pouFilePaths.append(filePath)
                        print(f"Found File : {pouFilePaths[-1]}")          
            pouDirectories.pop(0)
        
    timeString = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    if not "PlantUML_Output" in os.listdir(programPath):
        os.mkdir(f"{programPath}\PlantUML_Output")
    outputDir = f"{programPath}\PlantUML_Output\{timeString}"
    os.mkdir(outputDir)
    
    if dev__:
        parseTcPouFile(GLOBALS_["TestTcPou"], f"output", outputDir)
    else:
        for file in pouFilePaths:
            if Match := re.search("FB_(\w+)\.TcPOU", str(file)):
                print(Match.group(0))
                parseTcPouFile(file, Match.group(1), outputDir)
        print(f"\nFinished Parsing File(s), '.puml' output files can be found in generated in: {os.getcwd()}/{outputDir}")
        print(f"UML Diagrams can be generated @ {umlGeneratorLink}")

    
    input("Press Enter to close. . .\n>> ")
    return # exit



if __name__ == "__main__":
    main()