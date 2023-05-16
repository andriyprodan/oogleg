from django.urls import path, include

from neo4j_admin.views import ListView, AdminBase, EditView

app_name = 'neo4j_admin'
urlpatterns = [
    path('admin/', include([
        path('', AdminBase.as_view(), name='base'),
        path('<str:model_name>/', include([
            path('list/', ListView.as_view(), name='list'),
            path('<int:id>/edit/', EditView.as_view(), name='edit'),
        ]))
    ])),
]