package java.test;

import com.bfi.bravo.client.master.MasterClient;

class Gost {

    // private int why;
    // private String knapa;
    // private static final Logger logger = LoggerFactory.getLogger(Controller.class);
    // private UserService userService;

    // @Value("${microservice.confins.url}")
    // private String testUrl;

    // @Autowired
    // private MasterClient masterClient;

    // @Autowired
    // private ConfinsClient confinsClient;

    // @Autowired
    // private WebClient webClient;

    // @Autowired
    // private RabbitTemplate rabbitTemplate;

    // @Autowirde
    // private final KafkaTemplate<String, String> kafkaTemplate;
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
    //     sendMessagees("ssssss", "sss");

    // }

    // public void sendMessagees(String topic, String message) {
    //     kafkaTemplate.send(topic, message);
    //     System.out.println("Message sent: " + message);
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

    // public void baz() {
    //     sendMessage(queue, "asd");
    //     sendMessage("rabbitMqQueuePayment", "sss");
    // }

    // String url = "http://ldalda/order";
    // String queue = "rabbitMqQueue";

    // public void sendMessage(String queue, String message) {
    //     rabbitTemplate.convertAndSend(queue, message);
    //     System.out.println("Message sent: " + message);
    // }

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
    // String queue = "CART_ENDPOINT";
    // private String CART_URL = String.format("http://%s/shipping/", getenv("CART_ENDPOINT"));
    // private String CART_URL = String.format("http://%s/shipping/", queue);

    // private String getenv(String key, String def) {
    //     String val = System.getenv(key);
    //     val = val == null ? def : val;

    //     return val;
    // }

    // public int add(int a, int b) {
    //     int sum = a + b;
    //     if(a == 0) {
    //         a = b;
    //     } else if (a == 1) {
    //         a = c;
    //     }
    //     return sum;
    // }

    // public ResponseSuccessTemplate<AlterationDtoResp> updateRequestEditBankInformation(
    //     BankInformationDto request) throws JsonProcessingException {
    //   log.info("Update request edit Bank Information Agent: {}", request);
    //   hitSpicaScreeningAlteration(approvalId);

    //   AlterationDtoResp alterationDtoResp = AlterationDtoResp.builder()
    //       .transactionId(approvalId)
    //       .message("Update Request Edit Bank Information Success")
    //       .build();

    //   return ResponseSuccessTemplate.<AlterationDtoResp>builder()
    //       .respCode(String.valueOf(HttpStatus.OK.value()))
    //       .respDesc(HttpStatus.OK.getReasonPhrase()).data(alterationDtoResp)
    //       .timestamp(LocalDateTime.now()).build();
    // }

    // public ResponseSuccessTemplate<AlterationDtoResp> updatseRequestEditBankInformation(
    //     BankInformationDto request) throws JsonProcessingException {
    //   log.info("Update request edit Bank Information Agent: {}", request);
    //   ScreeningAlterationDtoReq screeningReq = ScreeningAlterationDtoReq.builder()
    //       .docNumber(approvalId).build();
    //   String screeningResp = spicaWS.callScreeningAgentAlteration(jsonConverter.toJson(screeningReq));
    //   log.info("Response screening agent alteration : " + screeningResp);

    //   AlterationDtoResp alterationDtoResp = AlterationDtoResp.builder()
    //       .transactionId(approvalId)
    //       .message("Update Request Edit Bank Information Success")
    //       .build();

    //   return ResponseSuccessTemplate.<AlterationDtoResp>builder()
    //       .respCode(String.valueOf(HttpStatus.OK.value()))
    //       .respDesc(HttpStatus.OK.getReasonPhrase()).data(alterationDtoResp)
    //       .timestamp(LocalDateTime.now()).build();
    // }

    // public void hitSpicaScreeningAlteration(String approvalId) {
    //     ScreeningAlterationDtoReq screeningReq = ScreeningAlterationDtoReq.builder()
    //         .docNumber(approvalId).build();
    //     String screeningResp = spicaWS.callScreeningAgentAlteration(jsonConverter.toJson(screeningReq));
    //     log.info("Response screening agent alteration : " + screeningResp);
    // }

    private Response createDefaultAuthUser(AuthDto dto) {
        LOGGER.info("[createDefaultAuthUser][CALL TO AUTH][AuthDto: {}]", dto.toString());
        HttpHeaders headers = new HttpHeaders();
        HttpEntity<AuthDto> entity = new HttpEntity<>(dto, null);
        String auth_service_url = getServiceUrl("ts-auth-service");

        List<ServiceInstance> auth_svcs = discoveryClient.getInstances("ts-auth-service");
        if(auth_svcs.size() >0 ){
            ServiceInstance auth_svc = auth_svcs.get(0);
            LOGGER.info("[createDefaultAuthUser][CALL TO AUTH][auth_svc host: {}][auth_svc port: {}]", auth_svc.getHost(), auth_svc.getPort());
        }else{
            LOGGER.info("[createDefaultAuthUser][CALL TO AUTH][can not get auth url]");
        }

        ResponseEntity<Response<AuthDto>> res  = restTemplate.exchange("http://ts-auth-service:12031/api/v1/auth",
                HttpMethod.POST,
                entity,
                new ParameterizedTypeReference<Response<AuthDto>>() {
                });
        return res.getBody();
    }

}

