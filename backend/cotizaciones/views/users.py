from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from ..forms import CustomUserCreationForm


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

