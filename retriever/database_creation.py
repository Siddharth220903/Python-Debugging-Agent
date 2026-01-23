from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions
import os
from tqdm import tqdm
from pathlib import Path
script_dir = Path(__file__).parent


def readPythonDocs(base_directory):

    base_path = Path(base_directory)
    all_content = []

    for file_path in base_path.rglob("*.txt"):
        try:
            
            print(f"---Attempting to read: {file_path.relative_to(base_path)}---")
            content = file_path.read_text(encoding='utf-8')
            print(f"---Successfuly read {len(content)} characters---\n")
            
            all_content.append({
                "file_name": file_path.name,
                "folder": file_path.parent.name,
                "text": content
            })
            
        except Exception as e:
            print(f"ERROR: Could not read {file_path}: {e}")

    print(f"\nLoaded {len(all_content)} documents from across the folder structure.")
    return all_content

def chunkContent(all_content):
    final_chunks = []
    
    print("---Starting reading content---")
    for entry in all_content:
        print(f"---Performing chunking with file {entry['file_name']} from {entry['folder']}---")
        chunks = splitter.split_text(entry['text'])
        
        for i, chunk in enumerate(chunks):
            final_chunks.append({
                "text": chunk,
                "metadata": {
                    "source": entry['file_name'],
                    "folder": entry['folder'],
                    "chunk_id": i
                }
            })
    print("---Successfully created chunks---")
    return final_chunks

def embdDbStore(chunks): 
    db_directory = f"{script_dir}/python_docs_vector_db"
    
    embedding_model = embedding_functions.DefaultEmbeddingFunction()
    client = chromadb.PersistentClient(path=db_directory)

    # Ensure to create DB only if it doesn't exists
    collection = client.get_or_create_collection(
        name="python_311_docs",
        embedding_function=embedding_model,
        metadata={"hnsw:space": "cosine"} 
    )

    documents = [c['text'] for c in chunks]
    metadatas = [c['metadata'] for c in chunks]
    ids = [f"id_{i}" for i in range(len(chunks))]

    print("\n---Creating local vector DB---")
    batch_size = 100
    total = len(documents)

    for i in tqdm(range(0, total, batch_size)):
        print(f"\n---Processing batch{i}----")
        collection.add(
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size],
        )
        print(f"\n---Processed batch{i}----")

    print("\n---Successfully stored vector DB---")
    return 

if __name__ == "__main__":

    docs_data = readPythonDocs(f'{script_dir}/python-3.11.14-docs-text/')

    # Separators based on structure of .txt files 
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

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200, 
        chunk_overlap=150, 
        separators=custom_separators
    )

    processed_chunks = chunkContent(docs_data)
    embdDbStore(processed_chunks)