from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import login_view, logout_view, register_view, profile_view, AdvisorClientListView, ClientCreateView, ClientDetailView

urlpatterns = [
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path('login/', login_view),  # 👈 expose JWT login at root if needed
    path('clients/', AdvisorClientListView.as_view(), name='advisor-client-list'),
    path('clients/create/', ClientCreateView.as_view(), name='client-create'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)