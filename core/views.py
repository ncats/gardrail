from django.shortcuts import render
from rest_framework_json_api.views import ModelViewSet, RelationshipView

from core.models import *
from core.serializers import *

# Create your views here.
class SynonymViewSet(ModelViewSet):
    queryset = Synonym.objects.all()
    serializer_class = SynonymSerializer

class InheritanceViewSet(ModelViewSet):
    queryset = Inheritance.objects.all()
    serializer_class = InheritanceSerializer
    
class TermViewSet(ModelViewSet):
    queryset = Term.objects.all()
    serializer_class = TermSerializer

class ReferenceViewSet(ModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer

class PhenotypeViewSet(ModelViewSet):
    queryset = Phenotype.objects.all()
    serializer_class = PhenotypeSerializer

class GeneViewSet(ModelViewSet):
    queryset = Gene.objects.all()
    serializer_class = GeneSerializer

class DiseaseViewSet(ModelViewSet):
    queryset = Disease.objects.all()
    serializer_class = DiseaseSerializer

class DiseaseGeneAssociationViewSet(ModelViewSet):
    queryset = DiseaseGeneAssociation.objects.all()
    serializer_class = DiseaseGeneAssociationSerializer
    
class DiseasePhenotypeAssociationViewSet(ModelViewSet):
    queryset = DiseasePhenotypeAssociation.objects.all()
    serializer_class = DiseasePhenotypeAssociationSerializer
