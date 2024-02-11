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
              
          if isElsif:
            # self.isElsif = True
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
            # self.isIf = True
            self.parentNode = lastNode
            self.condition = condition
            self.nodeLevel = lastNode.getLevel() + 1
            

          else: # Not a conditional
            self.parentNode = lastNode 
            self.nodeLevel = self.parentNode.getLevel()
            self.condition = None

        else: # First node
          print("First Node: ")
          self.nodeLevel = 0
          self.parentNode = None
          self.condition = condition
          self.seqNum = 0
          self.isIF = isIf
          self.isElsif = isElsif
          self.isElse = isElse
          
        
        self.id = f'{str(parentState)}_Node_{str(self.seqNum)}'
        print(f"Created New Node:")
        print(self.printout())
        # End Constructor
          
    # def getIF(self) -> bool:
    #   return self.isIF
    
    # def getElse(self) -> bool:
    #   return self.isElse
    
    # def getElsif(self) -> bool:
    #   return self.isElsif
         
    def getBaseNode(self):
      # Warning: Can return None Type if first node
      tempParent = self.parentNode
      while tempParent != None:
        if tempParent.getNodeLevel() == 0:
          return tempParent
        else:
          tempParent = tempParent.getParentNode()
      return tempParent # None
    
    def getParentNode(self):
      # Warning: Can return None Type if first node
      return self.parentNode
    
    def getLevel(self) -> int:
      # Warning: Can return None Type if no nodes exist
      return self.nodeLevel
    
    def getSeqNum(self) -> int:
      # Warning: Can return None Type if no nodes exist
      return int(self.seqNum)  
    
    def setSeqNum(self, num)-> None:
      if type(num) == type(int(1)):
        self.seqNum = str(num)
      else:
        print("setSeqNum(num): num must be of type(int)")
      return  

    def getId(self) -> str:
      # Warning: Can return None Type if no nodes exist
      return str(self.id)
    
    def getCondition(self) -> str:
      # Warning: Can return None Type
      return self.condition
    
    def invertCondition(self) -> None:
      # Warning: Does not update "None" type
      self.condition = self.getNotCondition()
      return
    
    def getNotCondition(self) -> str:
      if self.condition != None:
          if "NOT" in self.condition:
              return self.condition.replace("NOT ", "").lstrip().rstrip()
          else:
              return "(" + "NOT " + self.condition.lstrip().rstrip() + ")"
      else:
        return None
      
    def setNextNode(self, node) -> None:
      self.NextNode = node
      return
    
    def printout(self) -> str:
      return f"Node sequence#: {self.seqNum}\n\tid:{self.id}\n\tlevel:{self.nodeLevel}\n\tparent:{self.parentNode}\n"
      