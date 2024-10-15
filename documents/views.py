from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Folder, Document
from .forms import DocumentForm, FolderForm

# Dokumente hochladen
@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.folder = Folder.objects.get(id=request.POST.get('folder'), owner=request.user)
            document.save()
            messages.success(request, 'Dokument erfolgreich hochgeladen.')
            return redirect('document_list')
    else:
        form = DocumentForm()
        folders = Folder.objects.filter(owner=request.user)
    return render(request, 'documents/upload.html', {'form': form, 'folders': folders})

# Dokumente löschen
@login_required
def delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id, folder__owner=request.user)
    if document.folder.owner == request.user:
        document.delete()
        messages.success(request, 'Dokument erfolgreich gelöscht.')
    else:
        messages.error(request, 'Sie haben keine Berechtigung, dieses Dokument zu löschen.')
    return redirect('document_list')

# Ordner erstellen
@login_required
def create_folder(request):
    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.owner = request.user
            folder.save()
            messages.success(request, 'Ordner erfolgreich erstellt.')
            return redirect('document_list')
    else:
        form = FolderForm()
    return render(request, 'documents/create_folder.html', {'form': form})

# Liste der Dokumente anzeigen
@login_required
def document_list(request):
    folders = Folder.objects.filter(owner=request.user)
    documents = Document.objects.filter(folder__in=folders)
    paginator = Paginator(documents, 10)  # 10 Dokumente pro Seite
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'documents/document_list.html', {'folders': folders, 'page_obj': page_obj})

# Detailansicht eines Dokuments
@login_required
def document_detail(request, document_id):
    document = get_object_or_404(Document, id=document_id, folder__owner=request.user)
    return render(request, 'documents/document_detail.html', {'document': document})