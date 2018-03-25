import SudokuBoard
import Variable
import Domain
import Trail
import Constraint
import ConstraintNetwork
import time
from collections import defaultdict

class BTSolver:

    # ==================================================================
    # Constructors
    # ==================================================================

    def __init__ ( self, gb, trail, val_sh, var_sh, cc ):
        self.network = ConstraintNetwork.ConstraintNetwork(gb)
        self.hassolution = False
        self.gameboard = gb
        self.trail = trail

        self.varHeuristics = var_sh
        self.valHeuristics = val_sh
        self.cChecks = cc

    # ==================================================================
    # Consistency Checks
    # ==================================================================

    # Basic consistency check, no propagation done
    def assignmentsCheck ( self ):
        for c in self.network.getConstraints():
            if not c.isConsistent():
                return False
        return True

    """
        Part 1 TODO: Implement the Forward Checking Heuristic

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        Note: remember to trail.push variables before you assign them
        Return: true is assignment is consistent, false otherwise
    """
    def forwardChecking ( self ):
        # make a set to get rid of duplicate vars
        vars = set()

        #rewrite Get Modified constraints to reduce exponential growth
        for c in self.network.constraints:
            if c.isModified():
                for var in c.vars:
                    if var.isModified() and var.isAssigned():

                        #add var to vars if it was assigned and modified last turn
                        vars.add(var)
        
        # Change all variables back to  unmodified                 
        for v in self.network.variables:
            v.setModified( False )

        #cycle thru each var in vars
        for var in vars:

            #get the value of var
            varVal = var.getAssignment()

            #get all Neighbors of var
            NList = self.network.getNeighborsOfVariable(var)

            #for var check each neighbors domain and remove if vars assigned value is in domain
            for n in NList:
                if n != var and n.getDomain().contains(varVal):

                    #push var to trail and remove var val from neighbors domain
                    self.trail.push(n)
                    n.removeValueFromDomain(varVal)

                    #check if domain change leaves gamestate in consistent state
                    if not self.network.isConsistent():
                        return False

        return True

        """
        Part 2 TODO: Implement both of Norvig's Heuristics

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        (2) If a constraint has only one possible place for a value
            then put the value there.

        Note: remember to trail.push variables before you assign them
        Return: true is assignment is consistent, false otherwise
    """
    def norvigCheck ( self ):
        # Assigned vars, set of vars that have been modified and assigned
        assignedVars = set()

        # modified vars, set of vars that have been modified but bot assigned
        modifiedVars = set()

        #rewrite Get Modified constraints to reduce exponential growth
        for c in self.network.constraints:
            if c.isModified():
                for var in c.vars:
                    if var.isModified() and var.isAssigned():

                        #reset var modified to false
                        var.setModified( False )

                        #add var to vars if it was assigned and modified last turn
                        assignedVars.add(var)
                    
                    elif var.isModified() and not var.isAssigned():

                        #reset var modified to false
                        var.setModified( False )


        #cycle thru each var in assigned vars
        for var in assignedVars:

            #get the value of var
            varVal = var.getAssignment()

            #get all Neighbors of var
            NList = self.network.getNeighborsOfVariable(var)

            #for var check each neighbors domain and remove if vars assigned value is in domain
            for n in NList:
                if n != var and n.getDomain().contains(varVal):

                    #add neighbor to modified vars
                    modifiedVars.add(n)

                    #push var to trail and remove var val from neighbors domain
                    self.trail.push(n)
                    n.removeValueFromDomain(varVal)

                    #check if domain change leaves gamestate in consistent state
                    if not self.network.isConsistent():
                        return False
        
    
        #cycle thru modified vars
        for var in modifiedVars:

            #if a var has a domain of size one assign it that value
            if( not var.isAssigned()):
                domain = var.getDomain()
                if(domain.size() == 1):
                    self.trail.push(var)
                    var.assignValue(domain[0])
                    #check if domain change leaves gamestate in consistent state
                    if not self.network.isConsistent():
                        return False
        



        return True

    """
         Optional TODO: Implement your own advanced Constraint Propagation

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournCC ( self ):
        return None

    # ==================================================================
    # Variable Selectors
    # ==================================================================

    # Basic variable selector, returns first unassigned variable
    def getfirstUnassignedVariable ( self ):
        for v in self.network.variables:
            if not v.isAssigned():
                return v

        # Everything is assigned
        return None

    """
        Part 1 TODO: Implement the Minimum Remaining Value Heuristic

        Return: The unassigned variable with the smallest domain
    """
    def getMRV ( self ):
        # get all variables
        vars = self.network.getVariables()

        #Used to keep track of if MRV_Var has been assigned
        firstValAssigned = False

        # cycle thru all variables
        for var in vars:

            # check if var has been assigned
            if(not var.isAssigned()):

                # check if MRV_Var has been assigned
                if(not firstValAssigned):
                    firstValAssigned = True

                    #set MRV_Var to variable
                    MRV_Var = var

                    #If MRV_Var is as small as possible end getMRV prematurly
                    if MRV_Var.size() < 2:
                        return MRV_Var
                else:
                    #If var domain is smaller then MRV_Val set MRV_Var to var
                    if(MRV_Var.size() > var.size()):
                        MRV_Var = var

                        #If MRV_Var is as small as possible end getMRV prematurly
                        if MRV_Var.size() < 2:
                            return MRV_Var

        if(not firstValAssigned):
            return None

        return MRV_Var

    """
        Part 2 TODO: Implement the Degree Heuristic

        Return: The unassigned variable with the most unassigned neighbors
    """
    def getDegree ( self ):
        #Highest nieghbor count so far
        mostNeighbors = -1

        #The maximum amount of neighbors
        maxN = (self.gameboard.N ** 3) - self.gameboard.p - self.gameboard.q

        #cycle thru all variables
        for var in self.network.variables:

            #if var has not been assigned 
            if  not var.isAssigned():

                # get all Neighboring vars of var
                varNeighbors = self.network.getNeighborsOfVariable(var)
                counter = 0
                
                #count all of neighbors that have not been assigned
                for n in varNeighbors:
                    if not n.isAssigned():
                        counter +=1

                #if current var has more nieghbors then any previous var make var new maxval
                if counter > mostNeighbors:
                    maxVal = var
                    mostNeighbors = counter

                    #if counter is max potential neigbors return var
                    if(counter == maxN):
                        break
        return maxVal

    """
        Part 2 TODO: Implement the Minimum Remaining Value Heuristic
                       with Degree Heuristic as a Tie Breaker

        Return: The unassigned variable with, first, the smallest domain
                and, second, the most unassigned neighbors
    """
    def MRVwithTieBreaker ( self ):
         # get all variables
        vars = self.network.getVariables()

        #Highest nieghbor count so far
        mostNeighbors = -1

        #Used to keep track of if MRV_Var has been assigned
        firstValAssigned = False

        # cycle thru all variables
        for var in vars:

            # check if var has been assigned
            if(not var.isAssigned()):

                # check if MRV_Var has been assigned
                if(not firstValAssigned):
                    firstValAssigned = True

                    #set MRV_Var to variable
                    MRV_Var = var

                    # get all Neighboring vars of var
                    varNeighbors = self.network.getNeighborsOfVariable(var)
                    counter = 0

                    #count all of neighbors that have not been assigned
                    for n in varNeighbors:
                        if not n.isAssigned():
                            counter +=1

                    #if current var has more nieghbors then any previous var make var new maxvar
                    if counter > mostNeighbors:
                        MRV_Var = var
                        mostNeighbors = counter


                else:
                    #If var domain is smaller then MRV_Val set MRV_Var to var
                    if(MRV_Var.size() > var.size()):
                        MRV_Var = var

                    #If var domain same as other var domain then do degree tie breaker
                    elif MRV_Var.size() == var.size():

                        # get all Neighboring vars of var
                        varNeighbors = self.network.getNeighborsOfVariable(var)
                        counter = 0

                        #count all of neighbors that have not been assigned
                        for n in varNeighbors:
                            if not n.isAssigned():
                                counter +=1
                        
                        #if current var has more nieghbors then any previous var make var new maxvar
                        if counter > mostNeighbors:
                            MRV_Var = var
                            mostNeighbors = counter
                            
        if(not firstValAssigned):
            return None

        return MRV_Var

    """
         Optional TODO: Implement your own advanced Variable Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVar ( self ):
        return None

    # ==================================================================
    # Value Selectors
    # ==================================================================

    # Default Value Ordering
    def getValuesInOrder ( self, v ):
        values = v.domain.values
        return sorted( values )

    """
        Part 1 TODO: Implement the Least Constraining Value Heuristic

        The Least constraining value is the one that will knock the least
        values out of it's neighbors domain.

        Return: A list of v's domain sorted by the LCV heuristic
                The LCV is first and the MCV is last
    """

    def getValuesLCVOrder (self, v):
        # Get Domain
        values = v.getDomain()

        if(values.size() > 0 and values.size() < 2):
            valList = []
            valList.append(values.values[0])
            return valList

        # Get Neighbors of v
        Neighbors = self.network.getNeighborsOfVariable(v)

        #make a Dictionary
        dictValues = defaultdict(int)

        # cycle through each domain val for v
        for val in values.values:
            
            #counter used to keep track of neighbors effected each of v domain values
            counter = 0

            #check each neighbor of v with current domain
            for Neighbor in Neighbors:

                # Increment counter if domain value in nieghbor
                if( val in Neighbor.getDomain().values):
                    counter += 1

            #add domain val and counter val to dictionary
            dictValues[val] = counter

            # end search early if counter if less then one no need to continue search
            if(counter < 1):
                valList = []
                valList.append(val)
                return valList

        #sort Dictionary and place into list
        valList = []
        for key, value in sorted(dictValues.items(), key=lambda v: (v[1])):
            valList.append(key)

        return valList

    """
         Optional TODO: Implement your own advanced Value Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVal ( self, v ):
        return None

    # ==================================================================
    # Engine Functions
    # ==================================================================

    def solve ( self ):
        if self.hassolution:
            return

        # Variable Selection
        v = self.selectNextVariable()

        # check if the assigment is complete
        if ( v == None ):
            for var in self.network.variables:

                # If all variables haven't been assigned
                if not var.isAssigned():
                    print ( "Error" )

            # Success
            self.hassolution = True
            return

        # Attempt to assign a value
        for i in self.getNextValues( v ):

            # Store place in trail and push variable's state on trail
            self.trail.placeTrailMarker()
            self.trail.push( v )

            # Assign the value
            v.assignValue( i )

            # Propagate constraints, check consistency, recurse
            if self.checkConsistency():
                self.solve()

            # If this assignment succeeded, return
            if self.hassolution:
                return

            # Otherwise backtrack
            self.trail.undo()

    def checkConsistency ( self ):
        if self.cChecks == "forwardChecking":
            return self.forwardChecking()

        if self.cChecks == "norvigCheck":
            return self.norvigCheck()

        if self.cChecks == "tournCC":
            return self.getTournCC()

        else:
            return self.assignmentsCheck()

    def selectNextVariable ( self ):
        if self.varHeuristics == "MinimumRemainingValue":
            return self.getMRV()

        if self.varHeuristics == "Degree":
            return self.getDegree()

        if self.varHeuristics == "MRVwithTieBreaker":
            return self.MRVwithTieBreaker()

        if self.varHeuristics == "tournVar":
            return self.getTournVar()

        else:
            return self.getfirstUnassignedVariable()

    def getNextValues ( self, v ):
        if self.valHeuristics == "LeastConstrainingValue":
            return self.getValuesLCVOrder( v )

        if self.valHeuristics == "tournVal":
            return self.getTournVal( v )

        else:
            return self.getValuesInOrder( v )

    def getSolution ( self ):
        return self.network.toSudokuBoard(self.gameboard.p, self.gameboard.q)