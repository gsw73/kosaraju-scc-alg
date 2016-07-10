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
def myListSort( edgeList ):
    edgeList.sort()
    return

@clock
def getEdgesFromFile( inputFile ):
    gForward = []
    gReverse = []

    # read file, converting each line into an array
    with open( inputFile, 'rt' ) as fin:
        while True:
            line = fin.readline()
            if not line:
                break
            ( i, j ) = line.split()
            f = array.array( 'i', ( int( i ), int( j ) ) )
            r = array.array( 'i', ( int( j ), int( i ) ) )
            gForward.append( f )
            gReverse.append( r )

    return gForward, gReverse

@clock
def DFSLoop( graph, n ):
    stack = collections.deque()
    t = 0
    lengthOfGraph = len( graph )
    seen = array.array( 'i', ( 0 for i in range( lengthOfGraph ) ) )
    finishingTimes = array.array( 'i', ( 0 for i in range( lengthOfGraph ) ) )
    leaderFreq = array.array( 'i', ( 0 for i in range( lengthOfGraph ) ) )

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
                arc = graph[ node ].pop()

            except IndexError:
                t += 1
                leaderFreq[ leaderNodeS ] += 1
                finishingTimes[ node ] = t

                try:
                    node = stack.popleft()

                except IndexError:
                    break

            else:
                tail = arc[ 1 ]
                if seen[ tail ]:
                    continue

                else:
                    stack.appendleft( node )
                    node = tail

    return finishingTimes, leaderFreq

@clock
def swapInFinishingTimes( finishTimes, graph ):
    ftGraph = []
    for el in graph:
        ftEl = array.array( 'i', ( finishTimes[ el[ 0 ] ], finishTimes[ el[ 1 ] ] ) )
        ftGraph.append( ftEl )
    return ftGraph

@clock
def genDFSstructure( graphFlat, n ):
    graphStruct = [ [] for i in range( n + 1 ) ]

    for el in graphFlat:
        graphStruct[ el[ 0 ] ].append( el )

    return graphStruct

def usage():
    print( 'my_prompt> python3 scc.py <nodes> <filename>' )
    return

def main():
    if len( sys.argv ) < 3:
        usage()
        return

    # n indicates number of nodes in graph, G
    n = int( sys.argv[ 1 ] )
    inputFileName = sys.argv[ 2 ]

    # read edges from file
    gForward, gReverse = getEdgesFromFile( inputFileName )

    # gForward will be in order, but gReverse needs to be sorted
    myListSort( gReverse )

    # put into list such that all tail edges are grouped in list on same row;
    # e.g., row 1 has [ (1,x), (1,y), (1,z),... ]
    dfsGraphReverse = genDFSstructure( gReverse, n )

    # calculate finishing times of reverse graph
    finishingTimesArray, leaderFreqArray = DFSLoop( dfsGraphReverse, n )

    # substitute forward node numbers with finishing time numbers
    gForwardRenumbered = swapInFinishingTimes( finishingTimesArray, gForward )

    # sort renumbered forward graph
    myListSort( gForwardRenumbered )

    # put graph into structure for DFS
    dfsGraphForward = genDFSstructure( gForwardRenumbered, n )

    # call DFS Loop on forward graph
    fta, lfa = DFSLoop( dfsGraphForward, n )

    # just need top leaders
    lfaRevSort = sorted( lfa, reverse = True )

    print( 'The five largest SCCs have this many nodes:' )
    print( lfaRevSort[:5] )

if __name__ == '__main__':
    main()
