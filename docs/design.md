# New Relic Synthetics Exporter Design Doc

## Background

Some of our teams use New Relic Synthetics to monitor services from an external vantage.  This provides useful insight into service behavior.  Unfortunately, we do our alerting with Prometheus and prefer to have our alerts in one spot, particularly since Prometheus and Alert Manager's rules are more flexible than New Relic's alerts.

To fix this, we want to extract synthetic check results from New Relic and expose them to Prometheus.

## Design overview

New Relic does not, unfortunately, expose the results of a synthetics check directly via an API call (glaring oversight, IMO, although I'm sure there is a reason for it).  The existing [API](https://docs.newrelic.com/docs/apis/synthetics-rest-api/monitor-examples/manage-synthetics-monitors-rest-api) is geared towards synthetic management.

So what to do?  Fortunately the [Insights Query API](https://docs.newrelic.com/docs/insights/insights-api/get-data/query-insights-event-data-api) allows crafting a query that will get the current status of a synthetic monitor.  

A simple proof-of-concept is something like this:

```
-> curl -H "Accept: application/json" -H "X-Query-Key: <query key>" \ "https://insights-api.newrelic.com/v1/accounts/<account-number>/query?nrql=SELECT+%2A+FROM+SyntheticCheck+SINCE+5+MINUTES+AGO" \
| jq '.'

{
  "results": [
    {
      "events": [
        {
          "type": "SCRIPT_API",
          "minion": "...",
          "minionId": "...",
          "duration": 1205.041278,
          "result": "SUCCESS",
          "totalRequestBodySize": 0,
          "totalResponseHeaderSize": 272,
          "id": "...",
          "timestamp": 1527065693774,
          "secureCredentials": "",
          "monitorId": "...",
          "monitorName": "Some monitor",
          "locationLabel": "Singapore, SG",
          "totalRequestHeaderSize": 613,
          "totalResponseBodySize": 98,
          "typeLabel": "Scripted API",
          "location": "AWS_AP_SOUTHEAST_1"
        },
        {
          "type": "SCRIPT_BROWSER",
          "minion": "...",
          "minionId": "...",
          "duration": 3757,
          "result": "SUCCESS",
          "totalRequestBodySize": 1127,
          "totalResponseHeaderSize": 22855,
          "id": "...",
          "timestamp": 1527065665218,
          "secureCredentials": "",
          "monitorId": "...",
          "monitorName": "Some other monitor",
          "locationLabel": "Dublin, IE",
          "totalRequestHeaderSize": 82132,
          "totalResponseBodySize": 133869,
          "typeLabel": "Scripted Browser",
          "location": "AWS_EU_WEST_1"
        },
<SNIP>
    }
}
```

Then the main exporter simply needs to call this API periodically and refresh the timestamp values for each of the synthetics detected.  

This API call requires an X-Query-Key parameter set in the HTTP query header. This key is retrieved from the Insights API management URL for the account.  E.g. `https://insights.newrelic.com/accounts/<ACCOUNT>/manage/api_keys`

## Prometheus metric design

The exporter will export the following metric:

   * `newrelic_synthetics_up`

The value for this metric will be 1 if the result of the synthetic check is 'SUCCESS' or 0 if the result is 'FAILURE'.  The following labels will be exported:

   * `monitor_id` -- the UUID of the synthetic, used to reconstruct the URL to the monitor
   * `monitor_name` -- the name of the monitor, as used in the New Relic UI (e.g. "My Synthetic Check")
   * `location_name` -- the location of the monitor in human readable form (e.g. "Dublin, IE")
   * `location` -- the datacenter where the check was run (e.g. "AWS_EU_WEST_1")
   * `account` -- the account ID that can be used to reconstruct the URL to the monitor
