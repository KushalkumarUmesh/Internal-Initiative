from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    return render(request,'reviewApp/index.html',{'title':'Index'}) 

@login_required
def home(request):
    return render(request,'reviewApp/homeD.html',{'title':'Home'})

@login_required 
def create_new_project(request):
    return render(request,'reviewApp/create_new_projectD.html',{'title':'create_new_project'}) 

@login_required
def edit_existing_project(request):
    return render(request,'reviewApp/edit_existing_project.html',{'title':'edit_existing_project'}) 

@login_required
def update_tracker(request):
    return render(request,'reviewApp/update_tracker.html',{'title':'update_tracker'})   
     