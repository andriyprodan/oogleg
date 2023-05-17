from django.urls import path, include

urlpatterns = [
    path('admin/', include([
        path('', include('search.urls'), name='admin_base'),
    ])),
]