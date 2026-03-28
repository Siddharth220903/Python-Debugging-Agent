from .database_creation import DatabaseCreation

if __name__=="__main__": 
    database_create = DatabaseCreation() 
    database_create.readPythonDocs() 
    database_create.chunkContent()
    database_create.embdDbStore()