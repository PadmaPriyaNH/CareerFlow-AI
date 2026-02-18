from django.urls import path, include
from two_factor.views import (
    BackupTokensView, DisableView, LoginView, ProfileView, QRGeneratorView,
    SetupCompleteView, SetupView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('two_factor/setup/', SetupView.as_view(), name='setup'),
    path('two_factor/qrcode/', QRGeneratorView.as_view(), name='qr'),
    path('two_factor/setup/complete/', SetupCompleteView.as_view(), name='setup_complete'),
    path('two_factor/backup/tokens/', BackupTokensView.as_view(), name='backup_tokens'),
    path('two_factor/', ProfileView.as_view(), name='profile'),
    path('two_factor/disable/', DisableView.as_view(), name='disable'),
]
