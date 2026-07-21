from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, User
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.core.forms import CustomUserCreationForm, GroupForm, ConfiguracionForm
from apps.core.models import Configuracion


# ============================================
# Auth
# ============================================

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Cuenta creada exitosamente.")
            return redirect("dashboard")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})


# ============================================
# Usuarios
# ============================================

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "cotizaciones/user_list.html"
    context_object_name = "usuarios"
    paginate_by = 10

    def get_queryset(self):
        qs = User.objects.all().order_by("username")
        search = self.request.GET.get("search")
        if search:
            qs = qs.filter(
                Q(username__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )
        return qs


class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = "cotizaciones/user_form.html"
    success_url = reverse_lazy("user_list")

    def form_valid(self, form):
        messages.success(self.request, "Usuario creado exitosamente.")
        return super().form_valid(form)


# ============================================
# Roles
# ============================================

class GroupListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = "cotizaciones/roles/list.html"
    context_object_name = "roles"
    paginate_by = 10

    def get_queryset(self):
        qs = Group.objects.all()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_roles"] = Group.objects.count()
        page = ctx.get("page_obj")
        if page and page.paginator.count:
            start = (page.number - 1) * page.paginator.per_page + 1
            ctx["page_start"] = start
            ctx["page_end"] = start + len(ctx["roles"]) - 1
            ctx["page_total"] = page.paginator.count
        else:
            ctx["page_start"] = 0
            ctx["page_end"] = 0
            ctx["page_total"] = 0
        return ctx


class GroupCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = "cotizaciones/roles/form.html"
    success_url = reverse_lazy("rol_list")
    success_message = "Rol creado correctamente."


class GroupUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = "cotizaciones/roles/form.html"
    success_url = reverse_lazy("rol_list")
    success_message = "Rol actualizado correctamente."


class GroupDeleteView(LoginRequiredMixin, DeleteView):
    model = Group
    success_url = reverse_lazy("rol_list")
    success_message = "Rol eliminado correctamente."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# ============================================
# Configuración
# ============================================

def configuracion(request):
    if not request.user.is_staff:
        messages.error(request, "No tenés permiso para acceder a esta página.")
        return redirect("dashboard")

    config = Configuracion.get()

    if request.method == "POST":
        form = ConfiguracionForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuración guardada exitosamente.")
            return redirect("configuracion")
    else:
        form = ConfiguracionForm(instance=config)

    return render(request, "cotizaciones/configuracion.html", {"form": form, "config": config})


# ============================================
# Reportes (views propias, no la de analytics)
# ============================================

def reportes_view(request):
    return render(request, "cotizaciones/reportes.html", {})