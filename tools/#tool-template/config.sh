mkdir -p /tool/apis/experiment-api/specifications/
cp -R /specifications/* /tool/apis/experiment-api/specifications/
touch /tool/apis/experiment-api/specifications/api-config.yml
echo "specificationFileName: $API-openapi.json" >> /tool/apis/experiment-api/api-config.yml
echo "host: http://localhost:$PORT" >> /tool/apis/experiment-api/api-config.yml