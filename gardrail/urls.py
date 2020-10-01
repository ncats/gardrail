"""gardrail URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic.base import RedirectView
from rest_framework import routers

from core import views

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'synonyms', views.SynonymViewSet)
router.register(r'inheritances', views.InheritanceViewSet)
router.register(r'genes', views.GeneViewSet)
router.register(r'diseases', views.DiseaseViewSet)
router.register(r'terms', views.TermViewSet)
router.register(r'phenotypes', views.PhenotypeViewSet)
router.register(r'disease_gene_associations', views.DiseaseGeneAssociationViewSet)
router.register(r'disease_phenotype_associations', views.DiseasePhenotypeAssociationViewSet)

v1patterns = [
    path('', include(router.urls)),
]

apipatterns = [
    path('', RedirectView.as_view(url='v1/', permanent=False)),
    path('v1/', include(v1patterns)),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(apipatterns)),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
