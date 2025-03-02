package com.bfi.bravo.client.master;

import com.bfi.bravo.dto.master.AddressSearchResponse;
import com.bfi.bravo.dto.master.SubDistrictResponse;
import io.micrometer.core.annotation.Timed;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

@FeignClient(url = "${microservice.master.url}", name = "MasterClient")
public interface MasterClient {
  String SUB_DISTRICT_LIST_ENDPOINT = "/v1/address/sub_district";
  String ADDRESS_SEARCH_ENDPOINT = "/v1/address/search";

  @GetMapping(value = SUB_DISTRICT_LIST_ENDPOINT, produces = "application/json")
  @Timed(value = "masterdata.getSubDistrictList")
  SubDistrictResponse getSubDistrictList(@RequestParam(name = "sub_district_code") String subDistrictCode);

  @GetMapping(value = SUB_DISTRICT_LIST_ENDPOINT, produces = "application/json")
  @Timed(value = "masterdata.getSubDistrictListByZipCode")
  SubDistrictResponse getSubDistrictListByZipCode(@RequestParam(name = "zip_code") String zipCode);

  @GetMapping(value = SUB_DISTRICT_LIST_ENDPOINT, produces = "application/json")
  @Timed(value = "masterdata.getSubDistrictListByZipCodeAndLimit")
  SubDistrictResponse getSubDistrictListByZipCodeAndLimit(
    @RequestParam(name = "zip_code") String zipCode,
    @RequestParam(name = "limit") Integer limit
  );

  @GetMapping(value = ADDRESS_SEARCH_ENDPOINT, produces = "application/json")
  @Timed(value = "masterdata.getAddressListByName")
  AddressSearchResponse getAddressListByName(
    @RequestParam(name = "q") String q,
    @RequestParam(name = "limit") Integer limit
  );
}
