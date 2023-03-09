# OpenAI Embeddings Demo

This is a demo of using OpenAI embeddings with annual reports of companies. It leverages Azure OpenAI (could also work with OpenAI itself, but that was not tested), Azure CosmosDB, Azure Storage and Azure Functions.

## Deployment
1. Create a resource group with a OpenAI service, CosmosDB, Blob Storage and a Function App
2. Create a database and a container in CosmosDB
3. Create a container in Blob Storage and upload the annual reports
4. Copy `template.settings.json` to `local.settings.json` and fill in the values for OpenAI and CosmosDB
5. Deploy the function app to your resource group and also upload the local settings

Call the endpoints, first the `parse_report` endpoint to parse the annual reports and then the `query` endpoint to get answers from the report.

## Notes
This is demo code and has not been extensively tested, the approach of using a generic PDF reader to parse the reports is not ideal and should be replaced with a more robust approach, for instance using Azure Form Recognizer's document parsing methods.
The storage of embeddings in CosmosDB is also not ideal, it would be better to store them in a more efficient way, for instance in a vector database like Redis or some OSS offerings, the query would then have to be changed as well.

In short, this works and demo's great, but needs effort to make it robust and scalable!
