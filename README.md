# CJML-Integrator
CJML Integrator - A python application with GUI that allows to import XSS logs into Neo4J based on CJML EKG.

# Use
When application opened, it requires login credentials for Neo4J instance. After they are provided, the session is initatied with the Neo4j instance. Then, XSS file is required to be selected for application. It parses all fields stored in XSS file. The application starts automaticlly map fields based on the name structure. If the mapper skips the fields, user must assign if they are primary field, their type. When assigment is done, the application will ask to select fields, that express time. After that application starts running automaticly generated queries on Neo4J instance creating the graph. 
