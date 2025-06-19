from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'rides', RideViewSet, basename='ride')
router.register(r'accept-ride', RideAcceptanceViewSet, basename='accept-ride')
router.register(r'view-ride', RideViewSetUser, basename='view-ride')

urlpatterns = [
    path('', include(router.urls)),
    path('register',RegistrationApiView.as_view(),name="register"),
    path('login',LoginApiView.as_view(),name="login"),
    path('logout', LogoutView.as_view(), name='logout'),
]