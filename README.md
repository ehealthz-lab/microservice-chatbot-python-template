**TEMPLATE PYTHON**

Template to add new microservices in the microservice chatbot architecture in Python language.

Usage:

- The interaction should be added in botscripts/basic_chat.aiml following the AIML format.
- In the resources/operation_kernel.py file shoud be added the tasks performed by this microservice.
- The certificate folder, the credentials/security.conf file and the config.conf file should be configured accordingly.
- The Docker container should be created to add the new microservice into the architecture.

Example Docker usage:

- $ docker build -t yourDockerHub/nameMicroservice:version .
- $ docker push yourDockerHub/nameMicroservice:version

app.py is the file that starts the microservice.

config.conf: configuration file.

Dockerfile: is the file that creates the Docker container.

requirements.txt: list of the requirements for the Python environment.

botscripts: contains the AIML file.

certificates: contains used in the microservice.

credentials: contains the code necessary for the authentication.

objects: contains the token class and the message template.

registrationAPIgateway: contains the registration and deregistration in the API gateway.

resources: contains the tasks that this microservice is going to do.

This template works with FHIR DSTU3 server.