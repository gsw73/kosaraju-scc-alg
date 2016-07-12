#include <cstdlib>
#include <cstdio>
#include <iostream>
#include <fstream>
#include <string>
#include <cstring>
#include <algorithm>
#include <ctime>

using namespace std;

class StackItem {

    public:
        unsigned int val;
        StackItem *next;

        StackItem() {
            val = 0;
            next = nullptr;
        }
};

class Stack {

    public:
        StackItem *head;
        unsigned int elements;

        Stack() {
            head = nullptr;
            elements = 0;
        }

        void Push( unsigned int v ) {
            StackItem *si = new StackItem;

            // set up new item
            si->val = v;
            si->next = head;

            // point head to new item
            head = si;

            // increment counter
            elements++;

            return;
        }

        unsigned int Pop() {
            if ( !head )
                return( 0 );

            StackItem *tmp = head;
            unsigned int v = head->val;
            head = head->next;

            delete tmp; 

            return v;
        }

        void Show() {
            StackItem *ptr = head;
            while( ptr ) {
                if ( ptr->next ) printf( "H(%d)->", ptr->val );
                else printf( "H(%d)", ptr->val );
                ptr = ptr->next;
            }
            return;
        }
};

class Graph {

    public:
        Stack *tails;
        unsigned int nverticies;
        string name;

        void Show();
        void DFSLoop( unsigned int *finishT, unsigned int *leaderF );
        void AddNode( unsigned int tail, unsigned int head );
    
        // constructor & destructor
        Graph( unsigned int n, string name );
        ~Graph();
};

void Graph::DFSLoop( unsigned int *finishT, unsigned int *leaderF ) {
    Stack *stack = new Stack;
    unsigned int t = 0;
    bool *seen = new bool [ ( nverticies + 1 ) ];
    memset( seen, 0, sizeof( bool ) * ( nverticies + 1 ) );
    unsigned int leaderNodeS = 0;
    unsigned int node = 0;
    unsigned int head = 0;

    for ( unsigned int i = nverticies; i > 0; i-- ) {
        leaderNodeS = i;

        // make sure we haven't seen the node yet
        if ( seen[ i ] ) continue;

        // do DFS
        node = i;
        while( true ) {
            seen[ node ] = true;

            head = tails[ node ].Pop();

            if ( !head ) {
                t += 1;
                leaderF[ leaderNodeS ] += 1;
                finishT[ node ] = t;

                node = stack->Pop();
                if ( !node ) break;
            } else {
                if ( seen[ head ] ) {
                    continue;
                } else {
                    stack->Push( node );
                    node = head;
                }
            }
        }
    }
    return;
}

Graph::Graph( unsigned int n, string display_name ) {
    tails = new Stack [ ( n + 1 ) ];

    nverticies = n;
    name = display_name;

    return;
}

Graph::~Graph() {
    delete [] tails;
    return;
}

void Graph::AddNode( unsigned int tail, unsigned int head ) {
    tails[ tail ].Push( head );

    return;
}

void Graph::Show() {
    printf( "Name:  %s has %d Nodes\n", name.c_str(), nverticies );

    for ( unsigned int tail = 1; tail < nverticies + 1; tail++ ) {
        printf( "T(%d)->", tail );
        tails[ tail ].Show();
        printf( "\n" );
    }
    return;
}

void usage() {
    printf( "my_prompt>  scc <nodes> <filename>\n" );
}

void read_graph( Graph *fg, Graph *rg, string filename ) {
    unsigned int tail;
    unsigned int head;

    ifstream fin;

    fin.open( filename.c_str(), ifstream::in );

    if ( fin.is_open() ) {
        while( 1 ) {
            fin >> tail >> head;
            if ( fin.eof() ) break;
            
            // forward graph goes tail to head
            fg->AddNode( tail, head );
            rg->AddNode( head, tail );
        }
    } else {
        printf( "can't open file %s", filename.c_str() );
        exit( 1 );
    }
    return;
}

Graph *subFinishingTimes( unsigned int *finishT, Graph *fGraph_p, unsigned int n ) {
    Graph *renumGraph_p = new Graph( n, "Forward Graph Renumbered" );
    Stack *row;
    StackItem *ptr;

    for ( unsigned int tail = 1; tail < n + 1; tail++ ) {
        // call out the stack of heads associated with this tail
        row = &fGraph_p->tails[ tail ];

        // walk through stack items, substituting in new values
        ptr = row->head;
        while( ptr ) {
            ptr->val = finishT[ ptr->val ];
            ptr = ptr->next;
        }

        // put row in "finishing times" place in new graph
        renumGraph_p->tails[ finishT[ tail ] ] = *row;
    }
    return( renumGraph_p );
}    

void show_time( float t, string name ) {
    string units;
    float divby;

    t = t/CLOCKS_PER_SEC;

    if ( t < 1e-3 ) {
        units = "us";
        divby = 1e-6;
    } else if ( t < 1 ) {
        units = "ms";
        divby = 1e-3;
    } else {
        units = "s";
        divby = 1;
    }

    printf( "[%10.2f%s] %s\n", t/divby, units.c_str(), name.c_str() );
    return;
}

int main( int argc, char *argv[] ) {
    clock_t prg_start, prg_end;
    clock_t t0, t1;

    prg_start = clock();

    if ( argc != 3 ) {
        usage();
        return( 1 );
    }

    unsigned int n = ( unsigned int )atoi( argv[ 1 ] );
    string inputFile = argv[ 2 ];

    Graph *fGraph_p = new Graph( n, "Forward Graph" );
    Graph *rGraph_p = new Graph( n, "Reverse Graph" );

    t0 = clock();
    read_graph( fGraph_p, rGraph_p, inputFile );
    t1 = clock();
    show_time( float(t1) - float(t0), "read_graph" );

    // storage for finishing times and leader frequency
    unsigned int *ft = new unsigned int [ ( n + 1 ) ];
    memset( ft, 0, sizeof( unsigned int ) * ( n + 1 ) );
    unsigned int *lf = new unsigned int [ ( n + 1 ) ];
    memset( lf, 0, sizeof( unsigned int ) * ( n + 1 ) );

    t0 = clock();
    rGraph_p->DFSLoop( ft, lf );
    t1 = clock();
    show_time( float(t1) - float(t0), "DFSLoop" );
    delete rGraph_p;

    // renumber forward graph with finishing times
    Graph *fGraphRenum_p = nullptr;
    t0 = clock();
    fGraphRenum_p = subFinishingTimes( ft, fGraph_p, n );
    t1 = clock();
    show_time( float(t1) - float(t0), "subFinishingTimes" );

    // call DFS Loop on new forward graph
    memset( ft, 0, sizeof( unsigned int ) * ( n + 1 ) );
    memset( lf, 0, sizeof( unsigned int ) * ( n + 1 ) );
    t0 = clock();
    fGraphRenum_p->DFSLoop( ft, lf );
    t1 = clock();
    show_time( float(t1) - float(t0), "DFSLoop" );

    sort( lf, lf + n + 1, greater<unsigned int>() );
    printf( "Top 5 leaders have this man nodes:  " );
    for ( unsigned int i = 0; i < 5; i++ ) {
        printf( "%d ", lf[ i ] );
    }
    printf( "\n" );

    prg_end = clock();
    show_time( float(prg_end) - float(prg_start), "main" );

    return( 0 );
}
