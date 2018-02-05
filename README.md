# Load Test Using Locust

Distributed load test tool used in [Ario](https://ariogames.ir) development.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development
 and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Latest version of docker, you can read the installation instructions [here](https://docs.docker.com/engine/installation/).

### Installing

First you need to build the docker image:
```commandline
docker build -t arioloadtest:latest .
```

And then you can run it using the following command 

```commandline
docker run --name myloadtest -p "8089:8089" \ 
--env LOCUST_API_HOST=http://example.com \
--env LOCUST_API_URLS=/api1,/api2,/api3 \
--env LOCUST_API_HEADERS={"Authorization":"test"} \ 
--env LOCUST_USER_MIN_WAIT=500 \
--env LOCUST_USER_MAX_WAIT=200 \
arioloadtest:latest
 
```

now web ui should be available at *http://localhost:8089*

## Environment variables

The env variables should be used to configure the tool:

* **LOCUST_API_HOST** sets the base url of the API.
* **LOCUST_API_URLS** endpoints you want to test, separated by `,` 
* **LOCUST_API_HEADERS** requests headers should be set in json format
* **LOCUST_USER_MIN_WAIT** minimum wait time between each request for virtual users. 
* **LOCUST_USER_MAX_WAIT** maximum wait time between each request for virtual users. 

## Deployment

The tool can be used in distributed mode using the following commands:

on master node:

```commandline
docker run --rm --name loadtestmaster -p "8089:8089" -p "5557:5557" -p "5558:5558" ariogames/loadtest:latest locust --master
```

on slave nodes:
```commandline
docker run --rm --name loadtestslave --env LOCUST_MASTER_IP_ADDR=<MASTER_IP_ADDR> --env LOCUST_MASTER_WEB_PORT_ADDR=8089
ariogames/loadtest:latest
```

then `Post` the test configuration to master node, at the `http://<MASTER_IP_ADDR>:<MASTER_WEB_PORT>/config` endpoint:
```json
{
	"host": "http://api.example.com",
	"urls": ["/api1", "/api2"],
	"headers": {"Authorization": "test-token"},
	"min_wait": 100,
	"max_wait": 200
}
```

now browse to `http://<MASTER_IP_ADDR>:<MASTER_WEB_PORT>` and start your tests, 
you can change the test configurations any time you want and restart your tests using the web panel.

## Built With

* [Docker](https://docker.com) - The Container platform
* [pip](https://maven.apache.org/) - Dependency Management
* [Locust](https://locust.io/) - An open source load testing tool

## Authors

* **[Meraj Nouredini](https://github.com/m-nouredini)** - *Senior dev @ Ario*

## License

This project is licensed under the MIT License.

## Acknowledgments

* [Bardia](https://github.com/k3rn3l-p4n1c) helped a lot in api based configuration part
* Many thanks to [Locust](https://locust.io/)

