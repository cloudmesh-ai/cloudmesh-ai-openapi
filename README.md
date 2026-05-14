# Cloudmesh AI OpenAPI Service Generator

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/cloudmesh-ai/cloudmesh-ai-openapi/blob/main/LICENSE)

## Publication

A draft paper is available at

* <https://github.com/laszewski/laszewski.github.io/raw/master/papers/vonLaszewski-openapi.pdf>

The source to the paper is at

* <https://github.com/cyberaide/paper-openapi>

## Prerequisites

* We recommend Python 3.9 or newer.
* We recommend pip version 21.0 or newer
* We recommend that you use a venv (see developer install)


## Installation

The installation is rather simple and is documented next.

```
python -m venv ~/ENV3
source ~/ENV3/bin/activate
mkdir cm
cd cm
pip install cloudmesh-installer
cloudmesh-installer get openapi
cms help
cms init
```

If you like to know more about the installation of cloudmesh, please
visit the [Cloudmesh
Manual](https://cloudmesh.github.io/cloudmesh-manual/installation/install.html).

## Command Overview

When getting started using cloudmesh `openapi`, please first call to
get familiar with the options you have:

```
cms help openapi
```

Detailed usage is provided in the [MANUAL.md](MANUAL.md) file.

## Quick Start

Next we provide a very simple quickstart guide to steps to generate a
simple microservice that returns the CPU information of your computer.
We demonstrate how to generate, start, and stop the service.

Navigate to `~/cm/cloudmesh-ai-openapi` folder. In this folder you will
have a file called `cpu.py` from which we will generate the server.

First, generate an OpenAPI YAML file with the convenient command

```
cms openapi generate get_processor_name \
    --filename=./tests/server-cpu/cpu.py
```

This will create the file `cpu.yaml` that contains the OpenAPI
specification. To start the service from this specification simply use
the command

```
cms openapi server start ./tests/server-cpu/cpu.yaml
```

Now that the service is up and running, you can issue a request for
example via the commandline with

```
curl -X GET "http://localhost:8080/cloudmesh/get_processor_name"
```

The default port used for starting the service is 8080. In case you
want to start more than one REST service, use a different port in
following command:

```
cms openapi server start ./tests/generator-azureai/azure-ai-text-function.yaml --port=<**Use a different port than 8080**>
```

* Access the REST service using [http://localhost:8080/cloudmesh/ui/](http://localhost:8080/cloudmesh/ui/)

* After you have started the azure-ai-image-function or azure-ai-text-function on default port 8080, run following command to upload the image or text_image file

  ```
  curl -X POST "http://localhost:8080/cloudmesh/upload" -H  "accept: text/plain" -H  "Content-Type: multipart/form-data" -F "upload=@tests/generator-azureai/<image_name_with_extension>;type=image/jpeg"
  ```

  Keep your test image files at `./tests/generator-azureai/` directory

* With *azure-ai-text-function* started on port=8080, in order to test the azure ai function for text detection in an image, run following command

  ```
  curl -X GET "http://localhost:8080/cloudmesh/azure-ai-text-function_upload-enabled/get_text_results?image_name=<image_name_with_extension_uploaded_earlier>" -H "accept: text/plain"
  ```

* With *azure-ai-image-function* started on port=8080, in order to
  test the azure ai function for describing an image, run following
  command

  ```
  curl -X GET "http://localhost:8080/cloudmesh/azure-ai-image-function_upload-enabled/get_image_desc?image_name=<image_name_with_extension_uploaded_earlier>" -H "accept: text/plain"
  ```

* With *azure-ai-image-function* started on port=8080, in order to
  test the azure ai function for analyzing an image, run following
  command

  ```
  curl -X GET "http://localhost:8080/cloudmesh/azure-ai-image-function_upload-enabled/get_image_analysis?image_name=<image_name_with_extension_uploaded_earlier>" -H "accept: text/plain"
  ```

* With *azure-ai-image-function* started on port=8080, in order to
  test the azure ai function for identifying tags in an image, run
  following command

  ```
  curl -X GET "http://localhost:8080/cloudmesh/azure-ai-image-function_upload-enabled/get_image_tags?image_name=<image_name_with_extension_uploaded_earlier>" -H "accept: text/plain"
  ```

* Check the running REST services using following command:

  ```
  cms openapi server ps
  ```

* Stop the REST service using following command(s):

  ```
  cms openapi server stop azure-ai-image-function
  cms openapi server stop azure-ai-text-function
  ```

## List of Tests

The following table lists the different test we have, we provide additional
information for the tests in the test directory in a README file. Summaries
are provided below the table


| Test   | Short Description  | Link  |
| --- | --- | --- |
| Generator-calculator   | Test to check if calculator api is generated correctly. This is to test multiple function in one python file   | [test_01_generator.py](tests/generator-calculator/test_01_generator.py)
| Generator-testclass   |Test to check if calculator api is generated correctly. This is to test multiple function in one python class file  | [test_02_generator.py](tests/generator-testclass/test_02_generator.py)
| Server-cpu    | Test to check if cpu api is generated correctly. This is to test single function in one python file and function name is different than file name  | [test_03_generator.py](tests/server-cpu/test_03_generator.py)
| Server-cms   | Test to check if cms api is generated correctly. This is to test multiple function in one python file. | [test_04_generator.py](tests/server-cms/test_04_generator.py)
| Registry    | test_001_registry.py - Runs tests for registry. Description is in tests/README.md| [Link](tests/README.md)
| Image-Analysis | image_test.py - Runs benchmark for text detection for Google Vision API and AWS Rekognition. Description in image-analysis/README.md | [image](tests/image-analysis/README.md)


For more information about test cases ,please check [tests info](tests/README.md)


 * [test_001_registry](tests/test_001_registry.py)
 * [test_003_server_manage_cpu](tests/test_003_server_manage_cpu.py)
 * [test_010_generator](tests/test_010_generator.py)
 * [test_011_generator_cpu](tests/test_011_generator_cpu.py)
 * [test_012_generator_calculator](tests/test_012_generator_calculator.py)
 * [test_015_generator_azureai](tests/test_015_generator_azureai.py)
 * [test_020_server_manage](tests/test_020_server_manage.py)
 * [test_server_cms_cpu](tests/test_server_cms_cpu.py)

Note that there a many more tests that you can explore.

## Acknowledgments

Work conducted to integrate this work in research projects was funded by the NSF
CyberTraining: CIC: CyberTraining for Students and Technologies
from Generation Z with the awadrd numbers 1829704 and 2200409.