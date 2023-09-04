#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main() {
    int* mem = malloc(26 * sizeof(int));
    int conversion = (int) mem - 260;

    int* u;
    int* g ;

    int* ptr;
    int* q;

    int* y;

    char *S, *A;

    S = malloc(sizeof("informatique")*sizeof(char));

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("&g \t\t\t%d\n", (int)&*g-conversion);

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("y \t\t\t%d\n", (int)y-conversion);

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("&*q \t\t\t%d\n", (int)&*q-conversion);

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("* (int *)u \t\t%d\n", (int)* (int *)*u-conversion);

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("&* (int *)*ptr \t\t%d\n", (int)&* (int *)*ptr-conversion);

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("*** (int ***)u \t\t%d\n", (int)*** (int ***)*u-conversion);

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("*** (int ***)*ptr \t%d\n", (int)*** (int ***)*ptr-conversion);

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("++*&g \t\t\t%d\n", ++*&*g);

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("--*ptr \t\t\t%d\n", (int)--*ptr-conversion);

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("(*ptr)++ \t\t%d\n", (int)(*ptr)++-conversion);

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("*++q \t\t\t%d\n", *++q);

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("(int *)u-g \t\t%d\n", (int)((int *)*u-*g)-conversion);

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("ptr- &g \t\t%d\n", ptr - &*g);

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("(int *)u-ptr[g] \t%d\n", (int)((int *)*u-((int)ptr[*g]-conversion))-conversion);

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("(short)g+u \t\t%d\n", (short)*g+((int)*u-conversion));

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("y[g] \t\t\t%d\n", y[*g]-conversion);

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("*S \t\t\t%c\n", *S);

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("S[S[10] - A[-2]] \t%c\n", S[S[10] - A[-2]]);

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("*(&g - g) \t\t%d\n", *(&*g- *g) );

    init( &u, &g, &ptr, &q, &y, &S, &A, mem);
    printf("*(q - g) \t\t%d\n", *(q- *g) );


printf("\n");
    return 0;
  }


void init(int** u, int** g, int** ptr, int** q, int** y, char** S, char** A, int* mem){
    mem[25] = &mem[20];
    mem[24] = 1;
    mem[23] = &mem[19];
    mem[22] = 4;
    mem[21] = 4;
    mem[20] = &mem[24];
    mem[19] = &mem[0];
    mem[18] = 1;
    mem[17] = 4;

    mem[0] = &mem[25];

    *u = &mem[19];
    *g = &mem[21];

    *ptr = &**u;
    *q = &**g;

    *y = &mem[21];
    strcpy(*S, "informatique");

    *A = *S+3;
}
