package java.test;

class Gost {

    private int why;
    private String knapa;
    private static final Logger logger = LoggerFactory.getLogger(Controller.class);
    private UserService UserService;

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
        String[] arg1 = {"a", "b"};
        userService.bar(arg1, CART_URL);
        int a2 = this.printGo("knapa", "knapa");;
    }

    public void bar(String[] args, String test ) {
        if (false) {
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

    public void main(String[] args) {
        foo();
        try {
            baz();
        } catch(Exception e) {
            e.printStackTrace();
        }
    }

    public String findasd(int d, String[] dsda) {
        return "8";
    }

    public int findasde(int b) {
        return b;
    }

    public List<Integer> findasdc() {
        int b = 0;
        return this.getWhy("asdasda");
    }


}

// To compile:
//     rm example.class ; javac example.java ; ls -l example.java example.class ; java example
