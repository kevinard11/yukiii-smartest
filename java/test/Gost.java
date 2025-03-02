package java.test;

import com.bfi.bravo.client.master.MasterClient;

class Gost {

    private int why;
    // private String knapa;
    // private static final Logger logger = LoggerFactory.getLogger(Controller.class);
    private UserService userService;

    @Value("${microservice.confins.url}")
    private String testUrl;

    @Autowired
    private MasterClient masterClient;

    @Autowired
    private ConfinsClient confinsClient;

    @Autowired
    private WebClient webClient;

    @Autowired
    private RabbitTemplate rabbitTemplate;

    // public int getWhy() {
    //     return this.why;
    // }

    // public void setWhy(int why) {
    //     this.why = why;
    // }

    // public String getKnapa() {
    //     return this.knapa;
    // }

    // public void setKnapa(String knapa) {
    //     this.knapa = knapa;

    // }

    // public void foo() {
    //     String[] arg1 = {"a", "b"};
    //     userService.bar(arg1, CART_URL);
    //     int a2 = this.printGo("knapa", "knapa");;
    // }

    // public void bar(String[] args, String test ) {
    //     if (false) {
    //         bar(args, "huaaa");
    //     }
    //     System.out.printf("hello");
    //     baz();
    //     foo();
    // }

    public void baz() {
        sendMessage("asd", "asd");
    }

    String url = "http://ldalda/order";

    public void sendMessage(String queue, String message) {
        rabbitTemplate.convertAndSend(queue, message);
        System.out.println("Message sent: " + message);
    }

    // private void printGo(String test, String dooododoasdas) {
    //     masterClient.getSubDistrictList(test);
    //     masterClient.getSubDistrictListByZipCode(dooododoasdas);
    //    confinsClient.generateAgreementNumber(dooododoasdas, null);
    //    RestTemplate restTemplate = new RestTemplate();
    //    String response = restTemplate.getForObject(testUrl, String.class);
    // }

    // public void main(String[] args) {
    //     HttpClient httpClient = HttpClient.newHttpClient();

    //     HttpRequest request = HttpRequest.newBuilder()
    //             .uri(URI.create("http://example.com/api/delete/1"))
    //             .DELETE()
    //             .build();

    //     HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
    // }

    // public String findasd(int d, String[] dsda) {
    //     HttpResponse<String> response = Unirest.post(testUrl)
    //     .field("username", "john_doe")
    //     .field("file", new File("path/to/file.txt"))
    //     .asString();
    //     return response.body();
    // }

    // public int findasde(int b) {
    //     return b;
    // }

    // public List<Integer> findasdc() {
    //     int c;
    //     if (d.equals(why, "asdas")) {
    //         int c = 12;
    //         bar(args, "huaaa");
    //     }  else if (true) {
    //         int elseVar = 30;
    //         System.out.println(elseVar);
    //     } else {
    //         int d = 20;
    //     }

    //     why = 12;
    //     if (true) d = 10;
    //     int b = 0;
    //     this.getWhy("asdasda");
    //     userService.sadasd('adas');

    //     while (x > 0) {
    //         int count = x - 1;
    //         x--;
    //         d = update(count);
    //     }
    //     for (int i = 0; i < 10; i++) {
    //         int forVar = i * 2;
    //         process(forVar);
    //     }
    // }


}

// To compile:
//     rm example.class ; javac example.java ; ls -l example.java example.class ; java example
