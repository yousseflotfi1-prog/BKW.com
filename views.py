from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from .models import Article
from .forms import CustomUserCreationForm
from django.db.models import Q


# ---------------------------
# Page d'accueil avec recherche
# ---------------------------
def accueil(request):
    query = request.GET.get('q')
    if query:
        articles = Article.objects.filter(
            Q(titre__icontains=query) |
            Q(auteur__icontains=query) |
            Q(genre__icontains=query)
        )
    else:
        articles = Article.objects.all()
    return render(request, 'blog/accueil.html', {"articles": articles, "query": query})



# Signup avec email verification

def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Bloquer jusqu'à confirmation
            user.save()

            # Générer token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Lien d'activation
            activation_link = request.build_absolute_uri(f'/activate/{uid}/{token}/')

            # Envoyer email (ici affiché dans la console pour test)
            user.email_user(
                subject="Activez votre compte",
                message=f"Bonjour {user.username}, cliquez ici pour activer votre compte : {activation_link}"
            )

            return render(request, 'blog/signup_success.html', {"email": user.email})
    else:
        form = CustomUserCreationForm()
    return render(request, 'blog/signup.html', {'form': form})



# Activation du compte

def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'blog/activation_success.html', {"user": user})
    else:
        return render(request, 'blog/activation_invalid.html')


# Login

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('accueil')
    else:
        form = AuthenticationForm()
    return render(request, 'blog/login.html', {'form': form})


# ---------------------------
# Logout
# ---------------------------
def logout_view(request):
    logout(request)
    return redirect('accueil')


# ---------------------------
# Admin dashboard
# ---------------------------
def superuser_required(view_func):
    decorated_view_func = login_required(user_passes_test(lambda u: u.is_superuser)(view_func))
    return decorated_view_func


@superuser_required
def admin_dashboard(request):
    # Ajouter un nouvel article
    if request.method == "POST":
        titre = request.POST.get("titre")
        contenu = request.POST.get("contenu")
        auteur = request.POST.get("auteur")
        genre = request.POST.get("genre")
        fichier = request.FILES.get("fichier")

        Article.objects.create(
            titre=titre,
            contenu=contenu,
            auteur=auteur or "Inconnu",
            genre=genre or "Non spécifié",
            fichier=fichier
        )
        return redirect('admin_dashboard')

    articles = Article.objects.all()
    return render(request, 'blog/admin_dashboard.html', {"articles": articles})
