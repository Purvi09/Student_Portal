from django.shortcuts import render,redirect, get_object_or_404
from .models import Notes,Homework,Todo
from .forms import *
from django.contrib import messages
from django.views import generic
from youtubesearchpython import VideosSearch
import requests
import wikipedia
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request,'dashboard/home.html')

@login_required
def notes (request):
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user, title=request.POST['title'], description=request.POST['description'])
            notes.save()
            messages.success(request, f"Notes added from {request.user.username} successfully!")
            
    else:
        form = NotesForm()

    notes = Notes.objects.filter(user=request.user)
    context = {'notes': notes, 'form': form}
    return render(request, 'dashboard/notes.html', context)

@login_required
def delete_note(request, pk=None):
    
    Notes.objects.get(id=pk).delete()
    return redirect("notes")


class NotesDetailView(generic.DetailView):
    model = Notes

@login_required
def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST.get('is_finished')
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False

            homeworks = Homework(
                user=request.user,
                subject=request.POST.get('subject'),
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                due=request.POST.get('due'),
                is_finished=finished
            )
            homeworks.save()
            messages.success(request, f'Homework Added from {request.user.username}!!')
    else:
        form=HomeworkForm()
    homework = Homework.objects.filter(user=request.user)

    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False

    context = {'homeworks': homework, 'homeworks_done': homework_done,'form':form}
    return render(request,'dashboard/homework.html',context)

@login_required
def update_homework(request, pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')

@login_required
def delete_homework(request,pk=None) :
    Homework.objects.get(id=pk).delete()
    return redirect('homework')

def youtube(request):
    if(request.method=='POST'):
        form=DashboardForm(request.POST)
        text=request.POST['text']
        video=VideosSearch(text,limit=10)
        result_list = []
        for video in video.result()['result']:
            result_dict = {
                'Input': text,
                'title': video['title'],
                'duration': video['duration'],
                'thumbnail': video['thumbnails'][0]['url'],
                'channel': video['channel']['name'],
                'link': video['link'],
                'views': video['viewCount']['short'],
                'published': video['publishedTime'],
            }
            desc = ""
            if 'descriptionSnippet' in video:
                for j in video['descriptionSnippet']:
                    desc += j['text']
            result_dict['description'] = desc
            result_list.append(result_dict)
            context = {
            'form': form,
            'results': result_list,
            }
        return render(request, 'dashboard/youtube.html', context)

    form=DashboardForm()
    context={'form':form}
    return render(request,'dashboard/youtube.html',context)

@login_required
def todo(request):
    if(request.method=='POST'):
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST["is_finished"]
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except :
                finished = False
            todo = Todo(user=request.user, title=request.POST['title'], is_finished=finished)
            todo.save()
            messages.success(request, f"Todo added from {request.user.username} successfully!")
            
    else:
        form = TodoForm()
    user = request.user
    todo = Todo.objects.filter(user=user)

    if len(todo) == 0:
        todos_done = True
    else:
        todos_done = False

    context = {
        'form': form,
        'todos': todo,
        'todos_done': todos_done,
    }

    return render(request, 'dashboard/todo.html',context)

@login_required
def update_todo(request, pk=None):
    todo = get_object_or_404(Todo, id=pk)
    
    if todo.is_finished:
        todo.is_finished = False
    else:
        todo.is_finished = True
        
    todo.save()
    return redirect('todo') 

@login_required
def delete_todo(request, pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect('todo')

def books(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            url = f"https://www.googleapis.com/books/v1/volumes?q={text}"
            r = requests.get(url)
            answer = r.json()
            result_list = []

            for i in range(10):
                result_dict = {
                    'title': answer['items'][i]['volumeInfo'].get('title'),
                    'subtitle': answer['items'][i]['volumeInfo'].get('subtitle'),
                    'description': answer['items'][i]['volumeInfo'].get('description'),
                    'count': answer['items'][i]['volumeInfo'].get('pageCount'),
                    'categories': answer['items'][i]['volumeInfo'].get('categories'),
                    'rating': answer['items'][i]['volumeInfo'].get('averageRating'),
                    'thumbnail': answer['items'][i]['volumeInfo']['imageLinks'].get('thumbnail'),
                    'preview': answer['items'][i]['volumeInfo'].get('previewLink'),
                }
                result_list.append(result_dict)
                context={'form':form,'results':result_list}
            return render(request,'dashboard/books.html',context)
    else:
        form=DashboardForm()
    context={'form':form}
    return render(request,'dashboard/books.html',context)

def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text=request.POST['text']
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en_US/{text}"
        response = requests.get(url)
        answer = response.json()
        
        try:
            phonetics = answer[0]['phonetics'][0]['text'] if answer and 'phonetics' in answer[0] and answer[0]['phonetics'] else None

            audio = answer[0]['phonetics'][0]['audio'] if answer and 'phonetics' in answer[0] and answer[0]['phonetics'][0].get('audio') else None

            definition = answer[0]['meanings'][0]['definitions'][0]['definition'] if answer and 'meanings' in answer[0] and answer[0]['meanings'][0]['definitions'] else None

            example = answer[0]['meanings'][0]['definitions'][0]['example'] if answer and 'meanings' in answer[0] and answer[0]['meanings'][0]['definitions'][0].get('example') else None

            synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms'] if answer and 'meanings' in answer[0] and answer[0]['meanings'][0]['definitions'][0].get('synonyms') else None

            context = {
                'form': form,
                'input': text,
                'phonetics': phonetics,
                'audio': audio,
                'definition': definition,
                'example': example,
                'synonyms': synonyms,
            }
        except Exception as e:
        
                context = {
                    'form': form,
                    'input': ''
                }
        
        return render(request, 'dashboard/dictionary.html', context)
    else:
        form = DashboardForm()
        context = {'form': form}

    return render(request, 'dashboard/dictionary.html', context)

def wiki(request):
    if request.method == "POST":
        text = request.POST.get('text')
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)

        context = {
            "form": form,
            "title": search.title,
            "link": search.url,
            "details": search.summary
        }
        return render(request, "dashboard/wiki.html", context)
    else:
        form = DashboardForm()
        context = {
            "form": form
        }
        return render(request, "dashboard/wiki.html", context)
    
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Account Created for {username}!!")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'dashboard/register.html', context)

@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False, user=request.user)
    todos = Todo.objects.filter(is_finished=False, user=request.user)

    if len(homeworks) == 0:
        homework_done = True
    else:
        homework_done = False

    if len(todos) == 0:
        todos_done = True
    else:
        todos_done = False

    context = {
        "homeworks": homeworks,
        "todos": todos,
        "homework_done": homework_done,
        "todos_done": todos_done
    }

    return render(request, "dashboard/profile.html", context)
