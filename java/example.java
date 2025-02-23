package java;

class example {

    private int apa;
    private String text;

    public int getApa() {
        return this.apa;
    }

    public void setApa(int apa) {
        this.apa = apa;
    }

    public String getText() {
        return this.text;
    }

    public void setText(String text) {
        this.text = text;
        printGo("text");
    }

    public void foo() {
        String[] arg1 = {"a"};
        bar(arg1, "huaaa", "ssad");
        getApa();
    }

    public void bar(String[] args, String text, String eeee) {
        if (true) {
            bar(args, "huaaa", "asdad");
        }
        System.out.printf("hello");
        baz();
        foo();
    }
    public void baz() {
        System.out.printf("world");
        printGo("eaaa");
        getApa();
        setApa(1);
    }

    private void printGo(String text) {
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
