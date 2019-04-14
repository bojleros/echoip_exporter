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
# HELP last_refresh_timestamp
# TYPE last_refresh_timestamp gauge
last_refresh_timestamp 1.555232876e+09
# HELP is_vectra_domain
# TYPE is_vectra_domain gauge
is_vectra_domain 1.0
# HELP is_exact_ip
# TYPE is_exact_ip gauge
is_exact_ip 0.0
# HELP longitude_gt20
# TYPE longitude_gt20 gauge
longitude_gt20 1.0
# HELP latitude_40_60
# TYPE latitude_40_60 gauge
latitude_40_60 0.0
```

### Optional environmental variables

```
SERVER_URL - default "https://ifconfig.co" - you can use your own echoip endpoint since ifconfig.co does not guarantee response if you querry too often
REFRESH_INTERVAL - default 60 - how often to poll echoip endpoint for updates (in seconds)
REFRESH_TIMEOUT - default 3 - echoip response timeout (in seconds)
PORT - default 19666 - tcp endpoint for prometheus to query
```

## Running

You can run it as a standalone code just by setting environmentals and calling main.py. It is 2019 however and we have a docker and kubernetes:

```
Document docker here
```

```
Document kubernetes here
```
