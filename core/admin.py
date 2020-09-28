from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode

# Register your models here.
from .models import *

def link(type, field, id):
    return reverse('admin:core_'+type+'_changelist')+'?'+urlencode({field: f'{id}'})

@admin.register(Synonym)
class SynonymAdmin(admin.ModelAdmin):
    list_display = ('name', 'show_terms')
    search_fields = ('name',)

    def show_terms(self, obj):
        terms = Term.objects.filter(synonyms = obj)
        html = '<ul>'
        for t in terms:
            url = link('term', 'cui', t.cui)
            html = html +'<li><a href="%s">%s (%s)</a></li>' % (url, t.label, t.cui)
        html = html + '</ul>'
        return format_html(html)
    show_terms.short_description = 'Terms'

@admin.register(Prevalence)
class PrevalenceAdmin(admin.ModelAdmin):
    list_display = ('show_type', 'show_qualification',
                    'show_class', 'geo', 'show_status',
                    'show_diseases'
    )

    def show_type(self, obj):
        return obj.get_type()
    show_type.short_description = 'Type'

    def show_qualification(self, obj):
        return obj.get_qualification()
    show_qualification.short_description = 'Qualification'

    def show_class(self, obj):
        return obj.get_class()
    show_class.short_description = 'Class'

    def show_status(self, obj):
        return obj.get_status()
    show_status.short_description = 'Status'

    def show_diseases(self, obj):
        diseases = Disease.objects.filter(epidemiology=obj)
        html = '<ul>'
        for d in diseases:
            url = link('disease', 'cui', d.cui)
            html = html + '<li><a href="%s">'% url + d.label+' ('+d.cui+')</a></li>'
        html = html + '</ul>'
        return format_html(html)
    show_diseases.short_description = 'Diseases'

@admin.register(DiseaseGeneAssociation)
class DiseaseGeneAssociationAdmin(SimpleHistoryAdmin):
    list_display = ('status', 'show_disease', 'show_gene', 'show_assoc_type')
    search_fields = ('disease__label__startswith', 'gene__label__startswith',)
    readonly_fields = ('name',)
    
    def show_gene(self, obj):
        url = link('gene', 'cui', obj.gene.cui)
        return format_html('<a href="%s">%s (%s)</a>'% (
            url, obj.gene.symbol, obj.gene.cui))
    show_gene.short_description = 'Gene'

    def show_disease(self, obj):
        url = link('disease', 'cui', obj.disease.cui)
        return format_html('<a href="%s">%s (%s)</a>'% (
            url, obj.disease.label, obj.disease.cui))
    show_disease.short_description = 'Disease'

    def show_assoc_type(self, obj):
        return obj.get_type()
    show_assoc_type.short_description = 'Type'

@admin.register(DiseasePhenotypeAssociation)
class DiseasePhenotypeAssociationAdmin(SimpleHistoryAdmin):
    list_display = ('status', 'show_disease', 'show_phenotype',
                    'show_evidence', 'show_frequency', 'show_aspect')
    search_fields = ('disease__label__startswith', 'phenotype__label__startswith',)
    readonly_fields = ('name',)
    
    def show_phenotype(self, obj):
        url = link('phenotype', 'cui', obj.phenotype.cui)
        return format_html('<a href="%s">%s (%s)</a>'% (
            url, obj.phenotype.label, obj.phenotype.cui))
    show_phenotype.short_description = 'Phenotype'

    def show_disease(self, obj):
        url = link('disease', 'cui', obj.disease.cui)
        return format_html('<a href="%s">%s (%s)</a>'% (
            url, obj.disease.label, obj.disease.cui))
    show_disease.short_description = 'Disease'

    def show_evidence(self, obj):
        return obj.get_evidence()
    show_evidence.short_description = 'Evidence'

    def show_frequency(self, obj):
        if obj.frequency:
            if obj.frequency.value is not None:
                return obj.frequency.get_value()
            return obj.frequency.other
        return None
    show_frequency.short_description = 'Frequency'

    def show_aspect(self, obj):
        return obj.get_aspect()
    show_aspect.short_description = 'Aspect'

@admin.register(Term)
class TermAdmin(SimpleHistoryAdmin):
    list_display = ('cui', 'show_type', 'label_display', 'description')
    search_fields = ('label__startswith', 'synonyms__name__startswith', )

    def label_display(self, obj):
        if obj.url is not None:
            return format_html('<a href="{}" target="gardrail">{}</a>', obj.url, obj.label)
        return obj.label
    label_display.short_description = 'Label'

    def show_type(self, obj):
        t = type(Term.objects.get_subclass(id=obj.id)).__name__
        url = reverse('admin:core_'+t.lower()+'_changelist')
        return format_html('<a href="%s">'%url+t+'</a>')
    show_type.short_description = 'Type'
    
@admin.register(Disease)
class DiseaseAdmin(TermAdmin):
    list_display = ('cui', 'label_display', 'show_genes', 'show_inheritance',
                    'show_phenotypes', 'show_epidemiology')

    def show_inheritance(self, obj):
        inher = Inheritance.objects.filter(disease_inheritance=obj)
        html = '<ul>'
        for inh in inher:
            url = link('inheritance', 'cui', inh.cui)
            html = html + '<li><a href="%s">'%url + '%s (%s)</a></li>' % (inh.label, inh.cui)
        html = html + '</ul>'
        return format_html(html)
    show_inheritance.short_description = 'Inheritance'
        
    def show_genes(self, obj):
        assocs = DiseaseGeneAssociation.objects.filter(disease=obj)
        genes = '<ul>'
        for ass in assocs:
            url = link('gene', 'cui', ass.gene.cui)
            genes = genes + '<li><a href="%s">'%url +ass.gene.symbol+'</a></li>'
        genes = genes + '</ul>'
        return format_html(genes)
    show_genes.short_description = 'Genes'

    def show_phenotypes(self, obj):
        assocs = DiseasePhenotypeAssociation.objects.filter(disease=obj)
        ph = '<ul>'
        for ass in assocs:
            url = link('phenotype', 'cui', ass.phenotype.cui)
            ph = ph + '<li><a href="%s">'%url +ass.phenotype.label+'</a></li>'
        ph = ph + '</ul>'
        return format_html(ph)
    show_phenotypes.short_description = 'Phenotypes'

    def show_epidemiology(self, obj):
        prevalence = Prevalence.objects.filter(disease=obj)
        html = ''
        for p in prevalence:
            url = link('prevalence', 'id', p.pk)
            html = (html + '<li><a href="%s">'%url +p.get_type()+', '
                    +p.get_class()+'</a></li>')
        html = html + '</ul>'        
        return format_html(html)
    show_epidemiology.short_description = 'Epidemiology'
        
@admin.register(Frequency)
class FrequencyAdmin(admin.ModelAdmin):
    list_display = ('value', 'other')
    
class DiseaseRelationshipAdmin(TermAdmin):
    list_display = ('cui', 'label_display', 'show_diseases')

    def show_diseases(self, assocs):
        diseases = '%d disease(s)<ul>' % len(assocs)
        for ass in assocs[:min(len(assocs), 5)]:
            url = link('disease', 'cui', ass.disease.cui)
            diseases = (diseases + '<li><a href="%s">'%url
                        +'%s (%s)</a></li>' % (ass.disease.label, ass.disease.cui))
        diseases = diseases + '</ul>'
        return format_html(diseases)
    
@admin.register(Gene)
class GeneAdmin(DiseaseRelationshipAdmin):
    def show_diseases(self, obj):
        assocs = DiseaseGeneAssociation.objects.filter(gene=obj)
        return super().show_diseases(assocs)
    show_diseases.short_description = 'Diseases'
    
@admin.register(Phenotype)
class PhenotypeAdmin(DiseaseRelationshipAdmin):
    def show_diseases(self, obj):
        assocs = DiseasePhenotypeAssociation.objects.filter(phenotype=obj)
        return super().show_diseases(assocs)
    show_diseases.short_description = 'Diseases'

@admin.register(Inheritance)
class InheritanceAdmin(TermAdmin):
    pass

@admin.register(Reference)
class ReferenceAdmin(TermAdmin):
    pass
