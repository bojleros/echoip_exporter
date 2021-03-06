# echoip_exporter
Prometheus exporter that checks echoip json output against predefined tests.


## Description

This exporter was written since i got troubles with my ISP (credits goes to ...Vectra Poland). Due to reoccuring failures i was forced to look for a tool that will automatically generate a record of downtime. Since i am going to have a failover link blackbox_exporter was of no use. It is unable to parse json output from echoip that is mandatory for detection of single link failures instead of detecting 'no-internet-at-all' events.

## Configuration

By default exporter will poll ifconfig.co every 60 seconds. The only variable that is needed is environmental 'TESTS' (example below):

```
export TESTS='{"is_vectra_domain": {"field": "hostname", "test":"regex", "value":".*vectranet.pl"}, "is_exact_ip": {"field": "ip_decimal", "test":"eq", "value":"1567197064.1"}, "longitude_gt20": {"field": "longitude", "test":"gt", "value":"20.5"}, "latitude_40_60": {"field": "latitude", "test":"inrange", "value":"40:50"} }'
```

This environmental variable defines a list of tests , each having it's own gauge in prometheus endpoint output. Tests are executed by comparing echoip json field pointed by "field" key against value stored in "value" key. There are 3 values possible:

```
1 - test returns true
0 - test return false
-1 - echoip refresh exception (dns errorr , unreachable , timeout, etc ...)
```

Example prometheus endpoint output:

```
# HELP echoip_last_refresh_timestamp
# TYPE echoip_last_refresh_timestamp gauge
echoip_last_refresh_timestamp{endpoint="ifconfig.co"} 1.55525392e+09
# HELP echoip_evaluation_result 1 - true, 0 - false, -1 - connection error
# TYPE echoip_evaluation_result gauge
echoip_evaluation_result{endpoint="ifconfig.co",test="is_vectra_domain"} 1.0
echoip_evaluation_result{endpoint="ifconfig.co",test="is_exact_ip"} 0.0
echoip_evaluation_result{endpoint="ifconfig.co",test="longitude_gt20"} 1.0
echoip_evaluation_result{endpoint="ifconfig.co",test="latitude_40_60"} 1.0
```

### Optional environmental variables

```
SERVER_URL - default "https://ifconfig.co" - you can use your own echoip endpoint since ifconfig.co does not guarantee response if you querry too often
REFRESH_INTERVAL - default 60 - how often to poll echoip endpoint for updates (in seconds)
REFRESH_TIMEOUT - default 3 - echoip response timeout (in seconds)
PORT - default 19666 - tcp endpoint for prometheus to query
METRIC_PREFIX - default "echoip"
```

## Running

You can run it as a standalone code just by setting environmentals and calling main.py. It is 2019 however and we have a docker and kubernetes:

```
docker run -p 19666:19666 -e TESTS='your tests json goes here' bojleros/echoip_exporter:latest
```

For kubernetes look into examples directory.
