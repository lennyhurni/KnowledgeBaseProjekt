from celery import shared_task
from pinecone import Pinecone, ServerlessSpec
import cohere
from .models import Chatbot
from documents.models import Document
import os

# Initialisiere Pinecone und Cohere
pinecone_client = Pinecone(
    api_key=os.getenv('PINECONE_API_KEY')
)
cohere_client = cohere.Client(os.getenv('COHERE_API_KEY'))

@shared_task
def index_documents_task(chatbot_id):
    chatbot = Chatbot.objects.get(id=chatbot_id)
    chatbot.status = 'Indexierung läuft'
    chatbot.save()
    
    # Sammle alle Dokumente aus den zugehörigen Ordnern des Chatbots
    documents = Document.objects.filter(folder__in=chatbot.folders.all())
    texts = [doc.file.read().decode('utf-8') for doc in documents]
    
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
        index.upsert([(f'doc-{chatbot.id}-{i}', cohere_client.embed(texts=[text]).embeddings[0])])
    
    chatbot.status = 'Bereit'
    chatbot.save()