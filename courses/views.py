from django.apps import apps
from django.forms import modelform_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import TemplateResponseMixin, View

from braces.views import CsrfExemptMixin, JSONRequestResponseMixin

from courses.forms import ModuleFormSet
from courses.models import Course, Module, Content


class OwnerMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin:
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)

    def dispatch(self, request, pk=None, *args, **kwargs):
        self.course = get_object_or_404(Course, pk=pk, owner=request.user)
        return super().dispatch(request, pk, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({
            'course': self.course,
            'formset': formset,
        })

    def post(self, request, *args, **kwargs):
        formset = self.get_formset()
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({
            'course': self.course,
            'formset': formset,
        })


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        form = modelform_factory(model, exclude=['owner', 'order', 'created', 'updated'])
        return form(*args, **kwargs)

    def dispatch(self, request, module_pk=None, model_name=None, pk=None, *args, **kwargs):
        self.module = get_object_or_404(Module, pk=module_pk, course__owner=request.user)
        self.model = self.get_model(model_name=model_name)
        if pk:
            self.obj = get_object_or_404(self.model, pk=pk, owner=request.user)
        return super().dispatch(request, module_pk, model_name, pk, *args, **kwargs)

    def get(self, request, module_pk, model_name, pk=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({
            'form': form,
            'object': self.obj,
        })

    def post(self, request, module_pk, model_name, pk=None):
        form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not pk:
                Content.objects.create(module=self.module, item=obj)
            return redirect('module_content_list', self.module.pk)
        return self.render_to_response({
            'form': form,
            'object': self.obj,
        })


class ContentDeleteView(View):
    def post(self, request, pk):
        content = get_object_or_404(Content, pk=pk, module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.pk)


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_pk):
        module = get_object_or_404(Module, pk=module_pk, course__owner=request.user)
        return self.render_to_response({
            'module': module,
        })


class ChangeOrderMixin(CsrfExemptMixin, JSONRequestResponseMixin):

    def get_qs(self, pk, owner):
        return None

    def post(self, request):
        for pk, order in self.request_json.items():
            self.get_qs(pk, request.user).update(order=order)
        return self.render_json_response({'saved': 'ok'})


class ModuleOrderView(ChangeOrderMixin, View):
    def get_qs(self, pk, owner):
        return Module.objects.filter(pk=pk, course__owner=owner)


class ContentOrderView(ChangeOrderMixin, View):
    def get_qs(self, pk, owner):
        return Content.objects.filter(pk=pk, module__course__owner=owner)
