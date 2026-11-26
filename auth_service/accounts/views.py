from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, RegisterSerializer, MyTokenObtainPairSerializer

# --- New Imports for Frontend ---
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
# --------------------------------

User = get_user_model()


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Création d'un utilisateur.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        print(f"DEBUG REGISTER DATA: {request.data}", flush=True)
        return super().create(request, *args, **kwargs)


class UserMeView(generics.RetrieveAPIView):
    """
    GET /api/users/me/
    Retourne l'utilisateur connecté.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # l'utilisateur courant
        return self.request.user


class UserListView(generics.ListAPIView):
    """
    GET /api/users/?ids=1,2,3
    Retourne les utilisateurs correspondant aux IDs fournis.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        ids_param = self.request.query_params.get('ids', '')
        if not ids_param:
            return User.objects.none()
        
        try:
            user_ids = [int(id_str.strip()) for id_str in ids_param.split(',') if id_str.strip()]
            return User.objects.filter(id__in=user_ids)
        except ValueError:
            return User.objects.none()

# --- Frontend Views ---

def frontend_login(request):
    if request.user.is_authenticated:
        if request.user.role == 'ADMIN':
            return redirect('http://localhost:8001/gym-admin/dashboard/')
        return redirect('http://localhost:8002/')

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user)
            
            # Generate JWT for cross-service auth
            refresh = MyTokenObtainPairSerializer.get_token(user)
            access_token = str(refresh.access_token)
            
            # Redirect to Home (Courses Service)
            response = redirect('http://localhost:8002/')
            
            # Set cookies
            response.set_cookie('access_token', access_token, httponly=True, samesite='Lax')
            response.set_cookie('user_role', user.role, samesite='Lax')
            return response
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
    return render(request, 'accounts/login.html')

def frontend_register(request):
    if request.user.is_authenticated:
        if request.user.role == 'ADMIN':
            return redirect('http://localhost:8001/gym-admin/dashboard/')
        return redirect('http://localhost:8002/')

    if request.method == 'POST':
        u = request.POST.get('username')
        e = request.POST.get('email')
        p = request.POST.get('password')
        r = request.POST.get('role', 'MEMBER')
        
        # Simple validation
        if User.objects.filter(username=u).exists():
            return render(request, 'accounts/register.html', {'error': 'Username already exists'})
            
        try:
            # Create user with specified role
            print(f"DEBUG FRONTEND REGISTER: username={u} role={r}", flush=True)
            user = User.objects.create_user(username=u, email=e, password=p)
            user.role = r
            user.save()
            
            # Auto login
            login(request, user)
            refresh = MyTokenObtainPairSerializer.get_token(user)
            access_token = str(refresh.access_token)
            
            response = redirect('http://localhost:8002/')
            response.set_cookie('access_token', access_token, httponly=True, samesite='Lax')
            response.set_cookie('user_role', r, samesite='Lax')
            return response
        except Exception as ex:
            return render(request, 'accounts/register.html', {'error': str(ex)})
    return render(request, 'accounts/register.html')

def frontend_logout(request):
    """
    Logs out the user, clears cookies, and redirects to login.
    """
    logout(request)
    response = redirect('http://localhost:8001/auth/login')
    response.delete_cookie('access_token')
    response.delete_cookie('user_role')
    return response

# --- Admin Views ---

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'ADMIN'

class AdminUserListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = User
    template_name = 'accounts/admin_user_list.html'
    context_object_name = 'users'
    ordering = ['username']

class AdminUserUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = User
    template_name = 'accounts/admin_user_form.html'
    fields = ['username', 'email', 'role', 'is_active']
    success_url = reverse_lazy('admin-user-list')

class AdminUserDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'accounts/admin_user_confirm_delete.html'
    success_url = reverse_lazy('admin-user-list')


class AdminDashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'accounts/admin_dashboard.html'

