package java;

class Gost {

    private int why;
    private String knapa;

    public int getWhy() {
        return this.why;
    }

    public void setWhy(int why) {
        this.why = why;
    }

    public String getKnapa() {
        return this.knapa;
    }

    public void setKnapa(String knapa) {
        this.knapa = knapa;
    }

    public void foo() {
        String[] arg1 = {"a"};
        bar(arg1, "huaaa");
    }

    public void bar(String[] args, String test ) {
        if (true) {
            bar(args, "huaaa");
        }
        System.out.printf("hello");
        baz();
        foo();
    }
    public void baz() {
        System.out.printf("world");
        printGo("eaaa", "ssad");
    }

    private void printGo(String test, String dooododoasdas) {
        System.out.println("gooo");
    }

    // main program
    public void main(String[] args) {
        foo();
        baz();
    }
}

// To compile:
//     rm example.class ; javac example.java ; ls -l example.java example.class ; java example
