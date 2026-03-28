from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions
from tqdm import tqdm

class DatabaseCreation: 
    def __init__(self): 
        self.all_content = None
        self.final_chunks = None
        self.base_path = Path(__file__).parent / 'python-3.11.14-docs-text/'

    def readPythonDocs(self):
        self.all_content = []

        for file_path in self.base_path.rglob("*.txt"):
            try:
                
                print(f"---Attempting to read: {file_path.relative_to(self.base_path)}---")
                content = file_path.read_text(encoding='utf-8')
                print(f"---Successfuly read {len(content)} characters---\n")
                
                self.all_content.append({
                    "file_name": file_path.name,
                    "folder": file_path.parent.name,
                    "text": content
                })
            except Exception as e:
                raise(f"ERROR: Could not read {file_path}: {e}")
                return False 

        print(f"\nLoaded {len(self.all_content)} documents from across the folder structure.")
        return True
    
    def _getSplitter(self):
        custom_separators = [
            "\n\n\n",          
            "\n**********\n", 
            "\n==========\n",
            "\n----------\n", 
            "\n\n",            
            "\n",              
            " ",               
            ""                 
        ]
        try: 
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1200, 
                chunk_overlap=10, 
                separators=custom_separators
            )
            return splitter
        except: 
            raise("Unable to get a text splitter") 

    def _getEmbeddingModel(self): 
        try:
            embeddingModel = embedding_functions.DefaultEmbeddingFunction()
            return embeddingModel
        except: 
            raise("Unable to get Embedding Model")
    
    def _getClient(self):
        try:
            client = chromadb.HttpClient(
                host='localhost', port=8000
                )
            return client
        except: 
            raise("Cannot connect to client. Check if it is running.") 

    def chunkContent(self):
        self.final_chunks = []

        splitter = self._getSplitter()

        print("---Starting reading content---")
        try: 
            for entry in self.all_content:
                print(f"---Performing chunking with file {entry['file_name']} from {entry['folder']}---")
                chunks = splitter.split_text(entry['text'])
                
                for i, chunk in enumerate(chunks):
                    self.final_chunks.append({
                        "text": chunk,
                        "metadata": {
                            "source": entry['file_name'],
                            "folder": entry['folder'],
                            "chunk_id": i
                        }
                    })
            print("---Successfully created chunks---")
        except: 
            raise("ERROR: Creating chunks failed.")
        
    def embdDbStore(self): 
        embedding_model = self._getEmbeddingModel()
        client = self._getClient()
        # Ensure to create DB only if it doesn't exists
        try:
            collection = client.get_or_create_collection(
                name="python_311_docs",
                embedding_function=embedding_model,
                metadata={"hnsw:space": "cosine"} 
            )
            print("DB Creation successful.")
        except: 
            raise("Unable to create DB.")
        
        documents = [c['text'] for c in self.final_chunks]
        metadatas = [c['metadata'] for c in self.final_chunks]
        ids = [f"id_{i}" for i in range(len(self.final_chunks))]

        try:
            print("\nCreating local vector DB")
            batch_size = 100
            total = len(documents)

            for i in tqdm(range(0, total, batch_size)):
                print(f"\nProcessing batch{i}")
                collection.add(
                    documents=documents[i:i+batch_size],
                    metadatas=metadatas[i:i+batch_size],
                    ids=ids[i:i+batch_size],
                )
                print(f"\nProcessed batch{i}")

            print("\nSuccessfully stored vector DB")
        except:
            raise("ERROR: Unable to store local vector DB")  
