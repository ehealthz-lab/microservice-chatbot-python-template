**TEMPLATE PYTHON**

Template to add new microservices in the microservice chatbot architecture in Python language.

Usage:

- The interaction should be declared in botscripts/basic_chat.aiml following the AIML format.
- The tasks performed by this microservice architecture should be defined in resources/operation_kernel.py file.
- The certificates in the certificate folder, the credentials/security.conf file and the config.conf file should be configured as per the requirements.
- The Docker container should be built to add the new microservices into the architecture.

Example Docker usage:

- $ docker build -t yourDockerHub/nameMicroservice:version .
- $ docker push yourDockerHub/nameMicroservice:version

app.py is the file that starts the microservice.

config.conf: configuration file.

Dockerfile: is the file that creates the Docker container.

requirements.txt: list of the requirements for the Python environment.

botscripts: contains the AIML file.

certificates: contains the certificates used in the microservice.

credentials: contains the code necessary for the authentication.

objects: contains the token class and the message template.

registrationAPIgateway: contains the registration and deregistration in the API gateway.

resources: contains the tasks that this microservice is going to do.

This template works with FHIR DSTU3 server.

For more details please write an email to surya@unizar.es