#include <assert.h>
#include "lib.h"
int main(int argc, char** argv) {
    (void)argc;
    (void)argv;
    assert(42 == my_fun());
    return 0;
}
