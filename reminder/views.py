from django.shortcuts import render,redirect
from django.views.generic import View
from reminder.forms import UserForm,LoginForm,TodoForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from reminder.models import Todos
from django.utils.decorators import method_decorator
# Create your views here.
# -------------------signin required decorator-----------------------------------------
def signin_required(fn):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            messages.error(request,'Invalid Session')
            print('invalid')
            return redirect('signin')
        else:
            return fn(request,*args,**kwargs)
    return wrapper  
# -------------------owner permission required decorator-----------------------------------------
def owner_permission_required(fn):
    def wrapper(request,*args,**kwargs):
        id=kwargs.get('pk')  #url ll varunna id edukkan
        todo_obj=Todos.objects.get(id=id) #ee id ll olla todo obj edukkan
        if todo_obj.user != request.user:
            messages.error(request,"Invalid Session")
            return redirect('signin')
        else:
            return fn(request,*args,**kwargs)
    return wrapper  
# -
dec=[signin_required,owner_permission_required]  
#-----------------------register---------------------------------
class SignUpView(View):
    def get(self,request,*args,**kwargs):
        form=UserForm()
        return render(request,'register.html',{'form':form})
    def post(self,request,*args,**kwargs):
        form=UserForm(request.POST)
        if form.is_valid():
            form.save()
            print('account created')
            return redirect('signin')
        else:
            print("failed")
            messages.error(request,"Invalid Session")
            return render(request,'register.html',{'form':form})
# ------------------register-------------------------------------------

class SignInView(View):
    def get(self,request,*args,**kwargs):
        form=LoginForm()
        return render(request,'login.html',{'form':form})
    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            user_name=form.cleaned_data.get('username')
            pwd=form.cleaned_data.get('password')
            user_obj=authenticate(request,username=user_name,password=pwd)
            if user_obj:
                login(request,user_obj)
                print('successfully login')
                return redirect('index')
                
        print('invalid credential')
        return render(request,'login.html',{'form':form})

# ------------------------------------------------------------------------
@method_decorator(signin_required,name='dispatch')
class IndexView(View):
    def get(self,request,*args,**kwargs):
        form=TodoForm()
        qs=Todos.objects.filter(user=request.user).order_by('status')
        return render(request,'index.html',{'form':form,'data':qs})
    def post(self,request,*args,**kwargs):
        form=TodoForm(request.POST)
        form.instance.user=request.user
        if form.is_valid():
            form.save()
            return redirect('index')
        else:
            return render(request,"index.html",{'form':form})

#---------------------todo delete view------------------------------------------------------
@method_decorator(dec,name='dispatch')    
class TodoDeleteView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        Todos.objects.filter(id=id).delete()
        return redirect('index')
# ----------------------todo update view--------------------------------------------------------------
@method_decorator(dec,name='dispatch')
class TodoUpdateView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('pk')
        todo_obj=Todos.objects.get(id=id)
        if todo_obj.status==True:
            todo_obj.status=False
            todo_obj.save()
        else:
            todo_obj.status=True
            todo_obj.save()    
        return redirect('index')
# ----------------------todo logout view--------------------------------------------------------------
@method_decorator(signin_required,name='dispatch')
class TodoSignOutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect('signin')