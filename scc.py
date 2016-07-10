import sys
import array
import pprint
import time
import collections
import functools

def clock( func ):
    @functools.wraps( func )
    def wrapper( *args, **kwargs ):
        t0 = time.perf_counter()
        result = func( *args, **kwargs )
        t1 = time.perf_counter()

        elapsedTime = t1 - t0
        if elapsedTime < 1e-3:
            units = 'us'
            scale = 1e-6
        elif elapsedTime < 1:
            units = 'ms'
            scale = 1e-3
        else:
            units = 's'
            scale = 1

        print( '[{1:8.2f}{2:s}] {0:s}'.format( func.__name__, (t1 - t0)/scale, units ) ) 
        return result
    return wrapper

@clock
def getEdgesFromFile( inputFile, n ):
    fGraph = [ array.array( 'i', [] ) for edge in range( n + 1 ) ]
    rGraph = [ array.array( 'i', [] ) for edge in range( n + 1 ) ]

    # read file, converting each line into an array
    with open( inputFile, 'rt' ) as fin:
        while True:
            line = fin.readline()
            if not line:
                break
            ( tail, head ) = tuple( int( val ) for val in line.split() )

            # forward graph goes from tail to head
            fGraph[ tail ].append( head )

            # reverse graph goes from head to tail
            rGraph[ head ].append( tail )

    return fGraph, rGraph

@clock
def DFSLoop( graph, n ):
    stack = collections.deque()
    t = 0
    seen = array.array( 'i', ( 0 for i in range( n + 1 ) ) )
    finishingTimes = array.array( 'i', ( 0 for i in range( n + 1 ) ) )
    leaderFreq = array.array( 'i', ( 0 for i in range( n + 1 ) ) )

    for i in range( n, 0, -1 ):
        leaderNodeS = i

        # make sure we haven't seen the node yet
        if seen[ i ]:
            continue

        # do DFS
        node = i
        while True:
            seen[ node ] = 1

            try:
                head = graph[ node ].pop()

            except IndexError:
                t += 1
                leaderFreq[ leaderNodeS ] += 1
                finishingTimes[ node ] = t

                try:
                    node = stack.popleft()

                except IndexError:
                    break

            else:
                if seen[ head ]:
                    continue

                else:
                    stack.appendleft( node )
                    node = head

    return finishingTimes, leaderFreq

@clock
def subFinishingTimes( finishTimes, gForward, n ):
    # this implementation creates a new outer structure, but resuses
    # the head array rows after renumbering them

    graph = [ None for i in range( n + 1 ) ]

    for tail in range( len( gForward ) ):

        # swap out all the heads in that row for new FT
        for i in range( len( gForward[ tail ] ) ):
            head = gForward[ tail ][ i ]
            gForward[ tail ][ i ] = finishTimes[ head ]

        # add FT head array new list using FT tail
        graph[ finishTimes[ tail ] ] = gForward[ tail ]

    return graph

def usage():
    print( 'my_prompt> python3 scc.py <nodes> <filename>' )
    return

@clock
def main():
    if len( sys.argv ) < 3:
        usage()
        return

    # n indicates number of nodes in graph, G
    n = int( sys.argv[ 1 ] )
    inputFileName = sys.argv[ 2 ]

    # read edges from file into reverse graph and forward graph
    # (I destroy reverse graph during DFS loops so need forward copy)
    gForward, gReverse = getEdgesFromFile( inputFileName, n )

    # calculate finishing times of reverse graph
    # this destroys the reverse graph's head arrays
    finishingTimesArray, leaderFreqArray = DFSLoop( gReverse, n )

    # explicitly free destroyed list
    gReverse = []

    # substitute forward node numbers with finishing time numbers
    # this destroys the forward graph by changing the head arrays
    gForwardRenumbered = subFinishingTimes( finishingTimesArray, gForward, n )

    # explicitly free destroyed list
    gForward = []

    # call DFS Loop on forward graph
    fta, lfa = DFSLoop( gForwardRenumbered, n )

    # just need top leaders
    lfaRevSort = sorted( lfa, reverse = True )

    print( 'The five largest SCCs have this many nodes:' )
    print( lfaRevSort[:5] )

if __name__ == '__main__':
    main()
