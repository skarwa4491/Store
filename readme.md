Run below commands to access the store-api locally

step1: 
docker image build -t store:latest .

step2:
docker container run -dp 5005:5000 -w /app -v $(pwd):/app store

Step3:open in browser
'http://localhost:5005/swagger-ui'