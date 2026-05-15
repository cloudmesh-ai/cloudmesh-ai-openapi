import pathlib
import textwrap
import re
from dataclasses import is_dataclass

import requests
from cloudmesh.ai.common.io import Console
from cloudmesh.ai.common.debug import VERBOSE
from docstring_parser import parse


# TODO: Use latest version of openapi
# TODO: Use a dynamic way to derive the version of module/class being generated

class Generator:

    basicAuthTemplate = textwrap.dedent("""
          securitySchemes:
            basicAuth: # <-- arbitrary name for the security scheme
              type: http
              scheme: basic
              x-basicInfoFunc: {filename}.basic_auth
        
        security:
          - basicAuth: [] # <-- use the same name here
        """)

    openAPITemplate = textwrap.dedent("""
        openapi: 3.0.0
        info:
          title: {title}
          description: "{description}"
          version: "{version}"
        servers:
          - url: {serverurl}
            description: "{description}"
        paths:
          /{name}:
             get:
              summary: "{description}"
              description: Optional extended description in CommonMark or HTML.
              operationId: {filename}.{name}
              parameters:
                {parameters}
              responses:
                {responses}
        {upload}
        {components}
        """)

    openAPITemplate2 = textwrap.dedent("""
        openapi: 3.0.0
        info:
          title: {title}
          description: "{description}"
          version: "{version}"
        servers:
          - url: {serverurl}
            description: "{description}"
        paths:
          {paths}
        {upload}
        {components}
        """)

    uploadTemplate = textwrap.dedent("""
        /upload:
          post:
            summary: upload a file
            operationId: {filename}.upload
            requestBody:
              content:
                multipart/form-data:
                  schema:
                    type: object
                    properties:
                      upload:
                        type: string
                        format: binary
            responses:
              '200':
                description: "OK"
                content:
                  text/plain:
                    schema:
                      type: string
                      """)

    def parse_type(self, _type):
        """Look up and output supported OpenApi data type using python data type as input.

        Args:
            _type (str or type): The input data type that will be converted to an openapi compliant data type.

        Returns:
            str: The openapi compliant data type.
        """

        parser = {
            'int': 'type: integer',
            'bool': 'type: boolean',
            'float': 'type: number',
            'str': 'type: string',
            'list': 'type: array',
            'array': 'type: array',
            'dict': 'type: object'
        }

        if is_dataclass(_type):
            return f'$ref: "#/components/schemas/{_type}'
        # exits with KeyError if unsupported type is given

        try:
            t = parser[_type]
        except KeyError:
            print(f'unsupported data type supplied for {_type}')
            raise Exception
        return t

    def generate_parameter(self, name, _type, description):
        """Generate a single OpenApi YAML formatted parameter section.

        Args:
            name (str): Input python function parameter name.
            _type (str or type): Input python function parameter type.
            description (str): Input python function parameter description.

        Returns:
            str: The parameter spec section.
        """

        # Note: did not use f string approach to populate parameter values in strings due to indentation issues.
        #   It seems that f string approach interprets newlines in the parameter values after embedding in string and
        #   we need it to happen before.

        if type(_type) == str:
            _type = self.parse_type(_type)
        else:
            _type = self.parse_type(_type.__name__)

        if _type.find('array') != -1:
            spec = textwrap.dedent("""
                - in: query
                  name: {name}
                  description: "{description}"
                  schema:
                    {_type}
                    items: 
                      type: number""").format(name=name.strip(),
                                       description=description.strip(),
                                       _type=_type.strip())
        elif _type.find('object') != -1:
            spec = textwrap.dedent("""
                - in: query
                  name: {name}
                  description: "{description}"
                  schema:
                    {_type}
                    additionalProperties: true""").format(name=name.strip(),
                                       description=description.strip(),
                                       _type=_type.strip())
        else:
            spec = textwrap.dedent("""
                - in: query
                  name: {name}
                  description: "{description}"
                  schema:
                    {_type}""").format(name=name.strip(),
                                       description=description.strip(),
                                       _type=_type.strip())

        return spec

    def generate_response(self, code, _type, description):
        """Generate a single OpenApi YAML formatted response section.

        Args:
            code (str): Openapi response code.
            _type (str or type): Openapi response type.
            description (str): Openapi response description.

        Returns:
            str: The openapi response section spec.
        """

        if type(_type) == str:
            # Only retrieve openapi data type for responses that return a value
            if _type == "No Response":
                VERBOSE("Processing operation with no response")
            else:
                _type = self.parse_type(_type)
        else:
            _type = self.parse_type(_type.__name__)

        if _type == "No Response":
            spec = textwrap.dedent("""
              '{code}':
                description: "{description}"
            """).format(code=code.strip(),
                        description=description.strip()
                        )
        elif not _type.startswith('object'):
            # int, bool, float, str, list
            if (_type.find('array') != -1):
                spec = textwrap.dedent("""
                  '{code}':
                    description: "{description}"
                    content:
                      text/plain:
                        schema:
                          {_type}
                          items: {{}}""").format(code=code.strip(),
                                             description=description.strip(),
                                             _type=_type.strip())
            else:
                spec = textwrap.dedent("""
                  '{code}':
                    description: "{description}"
                    content:
                      text/plain:
                        schema:
                          {_type}""").format(code=code.strip(),
                                             description=description.strip(),
                                             _type=_type.strip())
        else:
            # dict (generic json) or dataclass ($ref)
            if (_type.find('object') != -1):
                spec = textwrap.dedent("""
                  '{code}':
                    description: "{description}"
                    content:
                      application/json:
                        schema:
                          {_type}
                          additionalProperties: True""").format(code=code.strip(),
                                             description=description.strip(),
                                             _type=_type.strip())
            else:
                spec = textwrap.dedent("""
                  '{code}':
                    description: "{description}"
                    content:
                      application/json:
                        schema:
                          {_type}""").format(code=code.strip(),
                                             description=description.strip(),
                                             _type=_type.strip())
        return spec

    def generate_properties(self, attr, _type):
        """Generate a single OpenApi YAML formatted schema properties section.

        Args:
            attr (str): Openapi schema property attribute name.
            _type (str or type): Openapi schema property attribute type.

        Returns:
            str: The openapi schema property spec.
        """

        if type(_type) == str:
            _type = self.parse_type(_type)
        else:
            _type = self.parse_type(_type.__name__)

        spec = textwrap.dedent(f"""
          {attr}:
            {_type}""")
        return spec

    def generate_schema(self, _class):
        """Generate a single OpenApi YAML formatted schema section using python dataclass as input.

        Args:
            _class (type): Python type class object.

        Returns:
            str: The openapi schema section spec.
        """
        class_name = _class.__name__
        if not is_dataclass(_class):
            raise TypeError(
                f'{class_name} is not a dataclass. '
                'Use the @dataclass decorator to define the class properly')
        properties = str()
        for attr, _type in _class.__annotations__.items():
            properties = properties + self.generate_properties(attr, _type)
        spec = textwrap.dedent(f"""
          {class_name}:
            type: object
            properties:
              {properties}""")
        return spec

    def populate_parameters(self, func_obj):
        """Convert all the input parameters of a python function into a single OpenApi YAML formatted
        parameters section.

        Args:
            func_obj (callable): Python function object.

        Returns:
            str: The openapi parameters section spec.
        """
        spec = str()
        description = None
        for parameter, _type in func_obj.__annotations__.items():
            if parameter == 'return':
                continue  # dicts are unordered, so use continue
                # intead of break to be safe
            else:
                docstring = parse(func_obj.__doc__)
                for param in docstring.params:
                    if param.arg_name == parameter:
                        description = textwrap.indent(param.description, ' ' * 15)
                spec = spec + self.generate_parameter(
                    parameter,
                    _type,
                    description if description else "no description provided in docstring")
                VERBOSE(spec)

        return spec

    def generate_path(self,
                       class_name=None,
                       description=None,
                       long_description=None,
                       funcname=None,
                       parameters=None,
                       responses=None,
                       filename=None,
                       all_function=None):
        """Generate a single OpenApi YAML formatted operation ID section.

        Args:
            class_name (str, optional): Python class name or module name.
            description (str, optional): Python class description.
            long_description (str, optional): Python class long description.
            funcname (str, optional): Python function name.
            parameters (str, optional): Openapi formatted parameters section spec.
            responses (str, optional): Openapi formatted responses section spec.
            filename (str, optional): Python module file name.
            all_function (bool, optional): Flag that means we process all functions in input file.

        Returns:
            str: The openapi operation id section spec.
        """

        l_description = long_description \
            if long_description != None \
            else 'None (Optional extended description in CommonMark or HTML)'

        if all_function:
            operationId = f"{filename}.{funcname}"
        else:
            operationId = f"{filename}.{class_name}.{funcname}"

        spec = textwrap.dedent("""
            /{class_name}/{funcname}:
               get:
                summary: "{description}"
                description: "{l_description}"
                operationId: {operationId}
                parameters:
                  {parameters}
                responses:
                  {responses}
        """).format(
            description=description,
            l_description=l_description.strip(),
            class_name=class_name,
            funcname=funcname,
            parameters=parameters.strip(),
            responses=responses.strip(),
            operationId=operationId
        )
        # remove 'parameters:' section if empty
        if parameters == '':
            spec = re.sub('\s*parameters:', '', spec)
        return spec

    def generate_openapi_class(self,
                                class_name=None,
                                class_description=None,
                                filename=None,
                                func_objects=None,
                                serverurl=None,
                                outdir=None,
                                yamlfile=None,
                                dataclass_list=None,
                                all_function=False,
                                enable_upload=False,
                                basic_auth_enabled=False,
                                write=True):
        """Main entry point into the module. Generates the full OpenApi YAML formatted
        specification for a python class or module with multiple functions.

        Args:
            class_name (str, optional): Python class name.
            class_description (str, optional): Python class description.
            filename (str, optional): Python module file name.
            func_objects (dict, optional): All function objects in input python file.
            serverurl (str, optional): URL for flask service.
            outdir (str, optional): Output directory where openapi spec yaml will be written.
            yamlfile (str, optional): File name for openapi spec yaml.
            dataclass_list (list, optional): List containing all data class objects.
            all_function (bool, optional): Flag to process all functions in input python file. Defaults to False.
            enable_upload (bool, optional): Flag to support file upload function. Defaults to False.
            basic_auth_enabled (bool, optional): Flag to enable basic authentication. Defaults to False.
            write (bool, optional): Flag to write out openapi spec yaml to a file. Defaults to True.

        Returns:
            None: No return value, but writes to file if write flag is set.
        """

        # Initializing and setting global variables
        paths = ""
        description = class_description \
            if class_description \
            else "No description found"
        version = "1.0"  # TODO:  hard coded for now
        filename = pathlib.Path(filename).stem

        # Loop through all functions
        for k, v in func_objects.items():  # k = function_name, v = function object
            VERBOSE(v)
            func_name = v.__name__
            # otherwise it will process the upload function, which doesn't have a defined response
            if func_name == 'upload' and enable_upload == True:
                continue
            Console.info('*'*40)
            Console.info(f"Currently processing function: {func_name}")

            docstring = parse(v.__doc__)

            func_description = docstring.short_description

            func_ldescription = docstring.long_description
            if func_ldescription:
                func_ldescription = textwrap.indent(func_ldescription.strip(), ' ' * 17)

            VERBOSE(func_description)
            VERBOSE(func_ldescription)

            # Define parameters section(s) for openapi yaml
            parameters = self.populate_parameters(v)
            if parameters != "":
                # Console.info(f"Processing parameters for function {func_name}")
                parameters = textwrap.indent(parameters, ' ' * 6)
                VERBOSE(parameters, label="openapi function parameters")
            else:
                Console.info(f"Function {func_name} has no parameters defined.")

            # Define responses section(s) for openapi yaml
            if 'return' in v.__annotations__:
                # Console.info(f"Processing response for function {func_name}")
                responses = self.generate_response('200',
                                                   v.__annotations__['return'],
                                                   'OK')
            else:
                # Console.info(f"Processing NO response for function {func_name}")
                responses = self.generate_response('204',
                                                   "No Response",
                                                   'This operation returns no response.')

            responses = textwrap.indent(responses, ' ' * 6)
            VERBOSE(responses, label="openapi function responses")

            # Define paths section(s) for openapi yaml
            paths = paths + self.generate_path(class_name,
                                               func_description,
                                               func_ldescription,
                                               func_name,
                                               parameters,
                                               responses,
                                               filename,
                                               all_function)

            VERBOSE(paths, label="openapi function path")

        # Indent full paths section for openapi yaml
        paths = textwrap.indent(paths, ' ' * 2)
        VERBOSE(paths, label="openapi function paths")

        # Define components section(s) for openapi yaml
        components = ""
        schemas = ""
        if len(dataclass_list) > 0:
            components = textwrap.dedent("""
                      components:
                        schemas:
                          """)
            for dc in dataclass_list:
                schemas = schemas + textwrap.indent(self.generate_schema(dc), ' ' * 6)
        VERBOSE(components, label="openapi function components")

        upload = ''
        if enable_upload:
            upload = self.uploadTemplate.format(filename=filename)
            upload = textwrap.indent(upload, ' ' * 2)

        if basic_auth_enabled and len(dataclass_list) == 0:
          components = "components:" + self.basicAuthTemplate.format(filename=filename)
        elif basic_auth_enabled:
          components = components + self.basicAuthTemplate.format(filename=filename)

        # Update openapi template to create final version of openapi yaml
        spec = self.openAPITemplate2.format(
            title=class_name,
            description=description,
            version=version,
            paths=paths.strip(),
            serverurl=serverurl,
            filename=filename,
            upload=upload,
            components=components.strip()
        )

        # Write openapi yaml to file
        if write:
            try:
                if yamlfile != "" and yamlfile is not None:
                    version = open(yamlfile, 'w').write(spec.strip())
                else:  # should really never get here
                    version = open(f"{outdir}/{class_name}.yaml", 'w').write(spec.strip())
            except IOError:
                Console.error("Unable to write yaml file")
            except Exception as e:
                print(e)

        return

    def generate_openapi(self,
                          f=None,
                          filename=None,
                          serverurl=None,
                          outdir=None,
                          yamlfile=None,
                          dataclass_list=None,
                          enable_upload=False,
                          basic_auth_enabled=False,
                          write=True):
        """Main entry point into the module. Generates the full OpenApi YAML formatted
        specification for a module with one single function.

        Args:
            f (callable, optional): Python function object.
            filename (str, optional): Python module file name.
            serverurl (str, optional): Server URL for flask service.
            outdir (str, optional): Output directory where openapi spec yaml will be written to.
            yamlfile (str, optional): Openapi spec yaml file name.
            dataclass_list (list, optional): List containing all data class objects.
            enable_upload (bool, optional): Flag to support file upload function. Defaults to False.
            basic_auth_enabled (bool, optional): Flag to enable basic authentication. Defaults to False.
            write (bool, optional): Flag to write out openapi spec yaml to a file. Defaults to True.

        Returns:
            None: No return value, but writes to file if write flag is set.
        """

        description = f.__doc__.strip().split("\n")[0]
        version = "1.0"  # TODO:  hard coded for now
        title = f.__name__
        parameters = self.populate_parameters(f)
        if parameters != "":
            parameters = textwrap.indent(parameters, ' ' * 8)
            VERBOSE(parameters, label="openapi function parameters")
        else:
            Console.info(f"Function {title} has no parameters defined")

        if 'return' in f.__annotations__:
            # Console.info(f"Processing response for function {title}")
            responses = self.generate_response('200',
                                               f.__annotations__['return'],
                                               'OK')
        else:
            # Console.info(f"Processing NO response for function {title}")
            responses = self.generate_response('204',
                                               "No Response",
                                               'This operation returns no response.')
        responses = textwrap.indent(responses, ' ' * 8)
        VERBOSE(responses, label="openapi function responses")

        components = ''
        schemas = ''
        if len(dataclass_list) > 0:
            components = textwrap.dedent("""
              components:
                schemas:
                  """)
            for dc in dataclass_list:
                schemas = schemas + textwrap.indent(self.generate_schema(dc), ' ' * 6)

        VERBOSE(components, label="openapi function components")

        filename = pathlib.Path(filename).stem
        upload = ''
        if enable_upload:
            upload = self.uploadTemplate.format(filename=filename)
            upload = textwrap.indent(upload, ' ' * 2)

        if basic_auth_enabled and len(dataclass_list) == 0:
          components = "components:" + self.basicAuthTemplate.format(filename=filename)
        elif basic_auth_enabled:
          components = components + self.basicAuthTemplate.format(filename=filename)

        spec = self.openAPITemplate.format(
            title=title,
            name=f.__name__,
            description=description,
            version=version,
            parameters=parameters.strip(),
            responses=responses.strip(),
            serverurl=serverurl,
            filename=filename,
            upload=upload,
            components=components
        )

        # remove 'parameters:' section if empty
        if parameters == '':
            spec = re.sub('\s*parameters:', '', spec)
        if write:
            try:
                if yamlfile != "" and yamlfile is not None:
                    version = open(yamlfile, 'w').write(spec)
                else:  # should really never get here
                    version = open(f"{outdir}/{title}.yaml", 'w').write(spec)
            except IOError:
                Console.error("Unable to write yaml file")
            except Exception as e:
                print(e)

        return


    # TODO: integrate the below functions into the package
    '''
    def file_put(root_url, service, filename, verbose=False):

        url = f'http://{root_url}/cloudmesh/{service}/file/put'
        print("URL", url)
        files = {'file': open(filename, 'rb')}
        r = requests.post(url, files=files)
        return r.text

    def file_list(root_url):
        r = requests.get(f'http://{root_url}/file/list')
        return r.text

    def file_get(root_url, service, filename):

        url = f'http://{root_url}/cloudmesh/{service}/file/get/{filename}'

        print("URL", url)

        r = requests.get(url)
        return r.text
    '''
