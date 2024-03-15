"""Bracket Legend:
    "()" : IF/ELSIF Conditions
    "[]" : 
    "{}" : 
    "||" : 
    None : State to State changes
"""

GLOBALS_ = {
    "FileHeader" : "\
@startuml State Diagram\n\n\
!theme plain\n\
'skin rose\n\
left to right direction\n\
hide empty description\n\
'!theme reddress-lightgreen\n\
title ",

    "FileFooter" : "\
\n@enduml\n",


    "CaseColourCode" : "#84b1f5",
    "MethodColourCode" : "#fc036b",
    "SubStateColourCode" : "#lightblue",
    "ErrorColourCode" : "#ff3333",
    # 
    # "TestTcPou" : "./FB_DbEventLogger.TcPOU"
    # "TestTcPou" : "./FB_ModeHandler.TcPOU"
    # "TestTcPou" : "./FB_LinearActuatorNew.TcPOU"
    # "TestTcPou" : "./FB_DC_ArmMotor.TcPOU"
    # "TestTcPou" : "./MAIN_wComments.TcPOU"
    # "TestTcPou" : "./MAIN.TcPOU"
    "TestTcPou" : "./FB_StateMachine.TcPOU"
    # "TestTcPou" : "./FB_EventHandler.TcPOU"

    

}
tokens = {
    "assign" : ":=",
    "declare" : ":",
    "lend" : ";",
}