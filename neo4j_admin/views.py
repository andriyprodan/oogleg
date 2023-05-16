from django.shortcuts import render
from django.views.generic import TemplateView

from neo4j_admin.driver import driver
from neo4j_admin.utils import get_all_db_labels


class AdminBase(TemplateView):
    template_name = 'neo4j_admin/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        with driver.session() as session:
            context['labels'] = get_all_db_labels(session)
        return context


# Create your views here.
class ListView(AdminBase):
    template_name = 'neo4j_admin/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 0))
        context['page'] = page
        context['model_name'] = self.kwargs['model_name']
        with driver.session() as session:
            context['results'] = session.run(
                f"match (n:{self.kwargs['model_name']}) return ID(n) AS id, n skip {page * 10} limit 10;").data()
            # res = context['results'].data()
            # context['results'] = list(context['results'])
            context['count'] = session.run(
                f"match (n:{self.kwargs['model_name']}) return count(n);").single().value()
            context['fields'] = [x for x in context['results'][0]['n'].keys()]

            return context


class EditView(AdminBase):
    template_name = 'neo4j_admin/edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.kwargs['model_name']
        with driver.session() as session:
            context['object'] = session.run(
                f"match (n:{self.kwargs['model_name']}) where ID(n) = {self.kwargs['id']} return n;").single().value()
            # get values of the fields of the node
            context['fields'] = [x for x in context['object'].items()]
            context['related_objects'] = session.run(
                f"match (n)-[r]-(m) where ID(n) = {self.kwargs['id']} return DISTINCT type(r) AS relationship, ID(m) as id, labels(m) AS labels, m;").data()
            return context

    def post(self, request, *args, **kwargs):
        properties = {key: value for key, value in request.POST.dict().items() if key.startswith('property_')}
        #     todo
        # related_objects = {key, value for key, value in request.POST.dict().items() if key.startswith('related_')}
        with driver.session() as session:
            session.run(
                f"match (n:{self.kwargs['model_name']}) where ID(n) = {self.kwargs['id']} set n = $props;",
                props=request.POST.dict())
        return self.get(request, *args, **kwargs)
