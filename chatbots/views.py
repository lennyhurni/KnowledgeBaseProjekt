from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Chatbot
from .forms import ChatbotForm, ChatbotConfigForm
from documents.forms import DocumentForm
from .tasks import index_documents_task
from documents.models import Document
from .utils import get_chatbot_response

# Chatbot erstellen
@login_required
def create_chatbot(request):
    if request.method == 'POST':
        form = ChatbotForm(request.POST)
        if form.is_valid():
            chatbot = form.save(commit=False)
            chatbot.owner = request.user
            chatbot.save()
            form.save_m2m()  # Speichert die vielen-zu-vielen Beziehung
            index_documents_task.delay(chatbot.id)  # Starte die Indexierung asynchron
            messages.success(request, 'Chatbot wird erstellt und indexiert. Dies kann einige Minuten dauern.')
            return redirect('chatbot_list')
    else:
        form = ChatbotForm()
    return render(request, 'chatbots/create_chatbot.html', {'form': form})

# Chatbot löschen
@login_required
def delete_chatbot(request, chatbot_id):
    chatbot = get_object_or_404(Chatbot, id=chatbot_id, owner=request.user)
    if chatbot.owner == request.user:
        delete_index_task.delay(chatbot.id)  # Lösche die Vektoren des Chatbots aus Pinecone
        chatbot.delete()
        messages.success(request, 'Chatbot erfolgreich gelöscht.')
    else:
        messages.error(request, 'Sie haben keine Berechtigung, diesen Chatbot zu löschen.')
    return redirect('chatbot_list')

# Liste der Chatbots anzeigen
@login_required
def chatbot_list(request):
    query = request.GET.get('q')
    if query:
        chatbots = Chatbot.objects.filter(Q(owner=request.user) & (Q(name__icontains=query) | Q(folders__name__icontains=query))).distinct()
    else:
        chatbots = Chatbot.objects.filter(owner=request.user)
    return render(request, 'chatbots/chatbot_list.html', {'chatbots': chatbots})

# Chatbot konfigurieren
@login_required
def configure_chatbot(request, chatbot_id):
    chatbot = get_object_or_404(Chatbot, id=chatbot_id, owner=request.user)
    if request.method == 'POST':
        form = ChatbotConfigForm(request.POST, instance=chatbot)
        if form.is_valid():
            form.save()
            update_index_task.delay(chatbot.id)  # Aktualisiere die Indexierung, falls sich die Ordner geändert haben
            messages.success(request, 'Chatbot-Konfiguration erfolgreich aktualisiert.')
            return redirect('chatbot_list')
    else:
        form = ChatbotConfigForm(instance=chatbot)
    return render(request, 'chatbots/configure_chatbot.html', {'form': form, 'chatbot': chatbot})

# Dokument hochladen und Index aktualisieren
@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save()
            for chatbot in Chatbot.objects.filter(folders__in=[document.folder]).distinct():
                update_index_task.delay(chatbot.id)  # Aktualisiere den Index des Chatbots, falls relevante Dokumente geändert wurden
            messages.success(request, 'Dokument erfolgreich hochgeladen und Index aktualisiert.')
            return redirect('document_list')
    else:
        form = DocumentForm()
    return render(request, 'documents/upload.html', {'form': form})

# Dokument löschen und Index aktualisieren
@login_required
def delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if document.folder.owner == request.user:
        document.delete()
        for chatbot in Chatbot.objects.filter(folders__in=[document.folder]).distinct():
            update_index_task.delay(chatbot.id)  # Aktualisiere den Index des Chatbots, falls relevante Dokumente gelöscht wurden
        messages.success(request, 'Dokument erfolgreich gelöscht und Index aktualisiert.')
    else:
        messages.error(request, 'Sie haben keine Berechtigung, dieses Dokument zu löschen.')
    return redirect('document_list')

# Chatbot-Anfrage verarbeiten
@login_required
def chatbot_interact(request, chatbot_id):
    chatbot = get_object_or_404(Chatbot, id=chatbot_id, owner=request.user)
    response = None
    if request.method == 'POST':
        query = request.POST.get('query')
        response = get_chatbot_response(chatbot, query)
    return render(request, 'chatbots/chatbot_interact.html', {'chatbot': chatbot, 'response': response})

# Detailansicht für einen Chatbot
@login_required
def chatbot_detail(request, pk):
    chatbot = get_object_or_404(Chatbot, pk=pk)
    return render(request, 'chatbots/chatbot_detail.html', {'chatbot': chatbot})