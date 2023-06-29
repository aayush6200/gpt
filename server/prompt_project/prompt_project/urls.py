from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from teaching_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html')),
    path('verifyToken', views.verify_token),
    path('post', views.generate_response)
    # path('', include(routing.websocket_urlpatterns)),
]
