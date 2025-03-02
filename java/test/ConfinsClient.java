package com.bfi.bravo.client.confins;

import com.bfi.bravo.constant.SecurityConstants;
import com.bfi.bravo.dto.confins.AgentIncentiveAPIRequest;
import com.bfi.bravo.dto.confins.AgentIncentiveAPIResponse;
import com.bfi.bravo.dto.confins.ConfinsAgentNumRequest;
import com.bfi.bravo.dto.confins.ConfinsAgentNumResponse;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;

@FeignClient(
  url = "${microservice.confins.url}",
  name = "ConfinsClient",
  configuration = ConfinsClientConfiguration.class
)
public interface ConfinsClient {
  String AGREEMENT_NUMBER_API = "/chain/confins_api/general/v1/create_get_no_trans";
  String INCENTIVE_DETAIL_ENDPOINT = "/chain/core/api/v1/incentive_ba/informasi_bonus_agent";

  @PostMapping(value = AGREEMENT_NUMBER_API, produces = MediaType.APPLICATION_JSON_VALUE)
  ConfinsAgentNumResponse generateAgreementNumber(
    @RequestHeader(value = SecurityConstants.AUTHORIZATION_HEADER_KEY) String authorizationHeader,
    @RequestBody ConfinsAgentNumRequest request
  );

  @PostMapping(
    value = INCENTIVE_DETAIL_ENDPOINT,
    consumes = MediaType.APPLICATION_JSON_VALUE,
    produces = MediaType.APPLICATION_JSON_VALUE
  )
  AgentIncentiveAPIResponse getAgentIncentiveDetails(
    @RequestHeader(value = SecurityConstants.AUTHORIZATION_HEADER_KEY) String authorizationHeader,
    @RequestBody AgentIncentiveAPIRequest request
  );
}
