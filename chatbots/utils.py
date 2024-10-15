import cohere
import openai
from pinecone import Pinecone
from documents.models import Document
import os
try:
    from dotenv import load_dotenv
except ImportError:
    raise ImportError("Das Modul 'python-dotenv' ist nicht installiert. Installiere es mit 'pip install python-dotenv'")

load_dotenv()

# Initialisiere Pinecone und Cohere
pinecone_client = Pinecone(
    api_key=os.getenv('PINECONE_API_KEY')
)
cohere_client = cohere.Client(os.getenv('COHERE_API_KEY'))
openai.api_key = os.getenv('OPENAI_API_KEY')

# Funktion zur Verarbeitung einer Anfrage
def get_chatbot_response(chatbot, query):
    # Sammle alle Dokumente aus den zugehörigen Ordnern des Chatbots
    documents = Document.objects.filter(folder__in=chatbot.folders.all())
    
    # Ensure documents are correctly decoded
    texts = []
    for doc in documents:
        try:
            texts.append(doc.file.read().decode('utf-8'))
        except Exception as e:
            print(f"Error reading document {doc.id}: {e}")
            continue
    
    # Indexiere die Dokumente mit Pinecone
    index_name = 'chatbot-index'
    if index_name not in pinecone_client.list_indexes().names():
        pinecone_client.create_index(
            name=index_name,
            dimension=1536,
            metric='euclidean',
            spec=ServerlessSpec(
                cloud='aws',
                region=os.getenv('PINECONE_REGION')
            )
        )
    index = pinecone_client.Index(index_name)
    for i, text in enumerate(texts):
        # Get embedding for each document text from Cohere
        response = cohere_client.embed(texts=[text])
        embedding = response.embeddings[0]  # Extract the embedding
        index.upsert([(
            f'doc-{chatbot.id}-{i}', 
            embedding, 
            {'text': text}  # Save text as metadata
        )])
    
    # Embedding for the query using Cohere
    query_embedding = cohere_client.embed(texts=[query]).embeddings[0]
    
    # Suche nach relevanten Dokumenten für die Anfrage
    results = index.query(query_embedding, top_k=5, include_metadata=True)
    
    # Extract the context from the top matches
    context = "\n".join([res['metadata']['text'] for res in results['matches']])

    # Create a prompt for OpenAI completion
    prompt = f"Kontext: {context}\nFrage: {query}\nAntwort:"
    
    # Generate a response using OpenAI
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=150
    )
    
    return response.choices[0].text.strip()