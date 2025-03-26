package com.andromeda.clientws;

import com.andromeda.config.exeception.exeptionlist.ClientException;
import kong.unirest.HttpResponse;
import kong.unirest.Unirest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Slf4j
@Component
public class SpicaWS {

  @Value("${api.baseUrlZuulAndromeda}")
  private String baseUrlZuulAndromeda;
  @Value("${api.spica.uri-screeningAgentAlteration}")
  private String uriGenerateReportComp;

  // public String callScreeningAgentAlteration(String input) {
  //   log.info("callScreeningAgentAlteration Params: {}", input);
  //   String uri = uriScreeningAgent;
  //   log.info("uri: {}", uri);
  //   HttpResponse<String> response = Unirest.post(uri)
  //       .header("Content-Type", "application/json")
  //       .body(input).asString();
  //   log.info("Response Status Code: {}", response.getStatus());
  //   return response.getBody();
  // }

  public String callGenerateReportComp(String batchNo) {
    log.info("callGenerateReportComp Params: batchNo={}", batchNo);
    String uri = uriGenerateReportComp
        .replace("{batchNo}", batchNo);
    log.info("uri: {}", uri);
    HttpResponse<String> response = Unirest.post(uri)
        .asString();
    log.info("Response Status Code: {}", response.getStatus());
    return response.getBody();
}
}
