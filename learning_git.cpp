#include <iostream>
using namespace std;

void first_program() {
    cout << "Hello World\n";
}
// Removed
void find_min() {
    cout << "Min" << endl;
}

void find_max() {
    cout << "Max" << endl;
}

void printAnimal() {
    cout << "kind: " << "dog" << endl;
    cout << "weight: " << 64 << "kg" << endl;
}

void swap(int* a, int* b) {
    int tmp = *a;
    *a = *b;
    *b = tmp;
}

void printPerson() {
    cout << "age: " << 19 << endl;
    cout << "name: " << "vo huu thang\n";
    cout << "mssv: " << 23120355 << endl;
}

int main() {
    cout << "Thang dep trai the!" << endl;
    return 0;
}