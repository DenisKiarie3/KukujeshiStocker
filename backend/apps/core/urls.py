from rest_framework.routers import DefaultRouter

from .views import StoreViewSet, StoreStaffViewSet

router = DefaultRouter()
router.register("stores", StoreViewSet, basename="store")
router.register("store-staff", StoreStaffViewSet, basename="storestaff")

urlpatterns = router.urls