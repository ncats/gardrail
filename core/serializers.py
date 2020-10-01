from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework_json_api.serializers import HyperlinkedModelSerializer
from rest_framework import serializers

from core.models import *

class SynonymSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Synonym
        fields = '__all__'

    terms = ResourceRelatedField(
        model=Term,
        many=True,
        read_only=True
    )

    included_serializers = {
        'terms': 'core.serializers.TermSerializer',
    }
    class JSONAPIMeta:
        included_resources = ['terms']
    

class TermSerializer(HyperlinkedModelSerializer):
    """
    (de-)serialize Term
    """
    class Meta:
        model = Term
        fields = '__all__'

    synonyms = ResourceRelatedField(
        model=Synonym,
        many=True,
        read_only=True
    )
       
    # {json:api} 'included' support
    included_serializers = {
        'synonyms': 'core.serializers.SynonymSerializer',
    }
    
    # if not specified, then '?include=synonyms' must be added to the URL
    class JSONAPIMeta:
        included_resources = ['synonyms']

class ReferenceSerializer(TermSerializer):
    class Meta:
        model = Reference
        fields = '__all__'

class PhenotypeSerializer(TermSerializer):
    class Meta:
        model = Phenotype
        fields = '__all__'

class InheritanceSerializer(TermSerializer):
    class Meta:
        model = Inheritance
        fields = '__all__'

    diseases = ResourceRelatedField(
        model=Disease,
        many=True,
        read_only=True
    )

    included_serializers = {
        'synonyms': 'core.serializers.SynonymSerializer',        
        'diseases': 'core.serializers.DiseaseSerializer',
    }
    class JSONAPIMeta:
        included_resources = ['synonyms', 'diseases']

class RelationshipSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Relationship
        fields = '__all__'
        
    status = serializers.SerializerMethodField()
    references = ResourceRelatedField(
        model = Relationship,
        many = True,
        read_only = True
    )

    def get_status(self, obj):
        return obj.get_status()

    included_serializers = {
        'references': 'core.serializers.ReferenceSerializer'
    }

    class JSONAPIMeta:
        included_resources = ['references']

        
class DiseaseGeneAssociationSerializer(RelationshipSerializer):
    class Meta:
        model = DiseaseGeneAssociation
        fields = ('disease', 'gene', 'assoc_type', 'references', 'status')
        
    assoc_type = serializers.SerializerMethodField()
    disease = ResourceRelatedField(
        model=Disease,
        many=False,
        read_only=True
    )

    gene = ResourceRelatedField(
        model=Gene,
        many=False,
        read_only=True
    )

    def get_assoc_type(self, obj):
        return obj.get_type()
    
    included_serializers = {
        'disease': 'core.serializers.DiseaseSerializer',
        'gene': 'core.serializers.GeneSerializer',
        'references': 'core.serializers.ReferenceSerializer'
    }

    class JSONAPIMeta:
        included_resources = ['disease', 'gene', 'references']


class DiseasePhenotypeAssociationSerializer(RelationshipSerializer):
    class Meta:
        model = DiseasePhenotypeAssociation
        exclude = ['modified_by', 'created_by', 'name']

    frequency = serializers.SerializerMethodField()
    disease = ResourceRelatedField(
        model=Disease,
        many=False,
        read_only=True
    )
    phenotype = ResourceRelatedField(
        model=Phenotype,
        many=False,
        read_only=True
    )

    def get_frequency(self, assoc):
        return {
            'value': assoc.frequency.get_value(),
            'other': assoc.frequency.other
        }

    included_serializers = {
        'disease': 'core.serializers.DiseaseSerializer',
        'phenotype': 'core.serializers.PhenotypeSerializer',
        'references': 'core.serializers.ReferenceSerializer'        
    }

class GeneAssociationSerializer(serializers.ModelSerializer):
    symbol = serializers.ReadOnlyField(source='gene.symbol')
    label = serializers.ReadOnlyField(source='gene.label')
    assoc_type = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    def get_assoc_type(self, inst):
        return inst.get_type()

    def get_status(self, inst):
        return inst.get_status()

    class Meta:
        model = DiseaseGeneAssociation
        exclude = ['name', 'created_by', 'modified_by']

class GeneSerializer(TermSerializer):
    diseases = ResourceRelatedField(
        model=DiseaseGeneAssociation,
        many=True,
        read_only=True
    )
    class Meta:
        model = Gene
        fields = '__all__'

    included_serializers = {
        'diseases': 'core.serializers.DiseaseGeneAssociationSerializer'
    }

    class JSONAPIMeta:
        included_resources = ['diseases']


class DiseaseSerializer(TermSerializer):
    class Meta:
        model = Disease
        exclude = ['gene_associations', 'pheno_associations']

    inheritance = ResourceRelatedField(
        model=Inheritance,
        many=True,
        read_only=True
    )

    genes = ResourceRelatedField(
        model=DiseaseGeneAssociation,
        many=True,
        read_only=True
    )
#    gene_associations = GeneAssociationSerializer(
#        source='diseasegeneassociation_set',
#        many=True
#    )
    
    phenotypes = ResourceRelatedField(
        model=DiseasePhenotypeAssociation,
        many=True,
        read_only=True
    )
    
    epidemiology = ResourceRelatedField(
        model=Prevalence,
        many=True,
        read_only=True
    )

    included_serializers = {
        'synonyms': 'core.serializers.SynonymSerializer',        
        'inheritance': 'core.serializers.InheritanceSerializer',
        'genes': 'core.serializers.DiseaseGeneAssociationSerializer',
        'phenotypes': 'core.serializers.DiseasePhenotypeAssociationSerializer'
    }
    
    class JSONAPIMeta:
        included_resources = ['synonyms', 'inheritance', 'genes', 'phenotypes']

