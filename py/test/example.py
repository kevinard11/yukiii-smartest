#!/usr/bin/python

def foo():
    arg1 = 'a'
    c = test('aasda')
    bar(globalList)

def bar( myList ):
    global globalRunCount
    globalRunCount = (globalRunCount + 1) * 2
    if globalRunCount < 2:
        bar(myList)
    print("hello")
    baz()
def baz():
    # intentionally put no space above this def
    print("world %s" % globalList)

def test(s):
    b = 120
    return b, 'asdasd'

def health():
    return 'OK'

# main program
globalRunCount = 10
globalList = ['a', 'b']
test = True
foo()
baz()
exit(0)

