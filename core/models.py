import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.constraints import Q
from simple_history.models import HistoricalRecords
from model_utils.managers import InheritanceManager

def get_tuple(tuple, key):
    for t in tuple:
        if key == t[0]:
            return t[1]
    return None

# Create your models here.
class Synonym(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Synonym', max_length=256, unique=True, null=False)

    def __str__(self):
        return self.name
    
class Term(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cui = models.CharField('CURIE', max_length=32, unique=True)
    label = models.CharField(max_length=1024, null=False)
    synonyms = models.ManyToManyField(
        Synonym, 
        blank=True)    
    url = models.URLField(max_length=256, blank=True)
    description = models.TextField(null=True, blank=True)
    history = HistoricalRecords()

    objects = InheritanceManager()
    
    def __str__(self):
        return '%s{%s, %s}' % (type(self).__name__, self.cui, self.label)

class Phenotype(Term):
    history = HistoricalRecords()

class Inheritance(Term):
    history = HistoricalRecords()

class Reference(Term):
    history = HistoricalRecords()
    
class Relationship(models.Model):
    STATUS = (
        ('U', 'Unknown'),
        ('V', 'Validated'),
        ('P', 'Pending')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Relationship name', max_length=64, null=False)
    status = models.CharField('Relationship status', max_length=1,
                              default='U', choices=STATUS)
    comments = models.TextField(null=True, blank=True)
    references = models.ManyToManyField(Reference, blank=True)

    class Meta:
        abstract = True

class Gene(Term):
    symbol = models.CharField('Gene symbol', max_length=16, null=False)
    locus = models.CharField('Gene locus (e.g., 2q33)', max_length=12,
                             blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return '%s{%s, %s, %s}' % (type(self).__name__, self.cui,
                                   self.symbol, self.label)

class Prevalence(models.Model):
    PTYPE = (
        ('C', 'Cases/families'),
        ('P', 'Point prevalence'),
        ('A', 'Annual incidence'),
        ('B', 'Prevalence at birth'),
        ('L', 'Lifetime Prevalence')
    )
    PQUAL = (
        ('S', 'Case'),
        ('V', 'Value and class'),
        ('C', 'Class only'),
        ('F', 'Family')
    )
    PCLASS = (
        ('A', '>1 / 1000'),
        ('B', '<1 / 1 000 000'),
        ('C', '1-5 / 10 000'),
        ('D', '1-9 / 1 000 000'),
        ('E', '1-9 / 100 000'),
        ('F', '6-9 / 10 000'),
        ('X', 'Not yet documented'),
        ('U', 'Unknown')
    )
    PSTATUS = (
        ('A', 'Validated'),
        ('B', 'Not yet validated'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ptype = models.CharField('Type', max_length=1, default='P', choices=PTYPE)
    pqual = models.CharField('Qualification', max_length=1, default='V', choices=PQUAL)
    pclass = models.CharField('Class', max_length=1, default='D', choices=PCLASS)
    valmoy = models.FloatField('ValMoy', blank=True, null=True,
                               help_text='Mean value of a given prevalence type')
    geo = models.CharField('Geographic', max_length=64,
                           help_text='e.g., Worldwide, United States')
    status = models.CharField(max_length=1, default='A', choices=PSTATUS)

    def __str__(self):
        return '%s{%s, %s, %s, %s, %s}' % (
            type(self).__name__, self.get_type(), self.get_qualification(),
            self.get_class(), self.geo, self.get_status()
        )

    def get_type(self):
        return get_tuple(Prevalence.PTYPE, self.ptype)
    
    def get_qualification(self):
        return get_tuple(Prevalence.PQUAL, self.pqual)

    def get_class(self):
        return get_tuple(Prevalence.PCLASS, self.pclass)

    def get_status(self):
        return get_tuple(Prevalence.PSTATUS, self.status)

class Disease(Term):
    inheritance = models.ManyToManyField(
        Inheritance, related_name='disease_inheritance', blank=True)
    gene_associations = models.ManyToManyField(
        Gene,
        through='DiseaseGeneAssociation',
        through_fields=('disease', 'gene')
    )
    pheno_associations = models.ManyToManyField(
        Phenotype,
        through='DiseasePhenotypeAssociation',
        through_fields=('disease', 'phenotype')
    )
    epidemiology = models.ManyToManyField(Prevalence, blank=True)
        
    history = HistoricalRecords()

class DiseaseGeneAssociation(Relationship):
    TYPES = (
        ('Orphanet_317343', 'disease-causing germline mutation(s) in'),
        ('Orphanet_317344', 'disease-causing somatic mutation(s) in'),
        ('Orphanet_317345', 'major susceptibility factor in'),
        ('Orphanet_317346', 'modifying germline mutation in'),
        ('Orphanet_317348', 'part of a fusion gene in'),
        ('Orphanet_317349', 'role in the phenotype of'),
        ('Orphanet_327767', 'candidate gene tested in'),
        ('Orphanet_410295', 'disease-causing germline mutation(s) (loss of function) in'),
        ('Orphanet_410296', 'disease-causing germline mutation(s) (gain of function) in'),
        ('Orphanet_465410', 'biomarker tested in'),
    )
    name = models.CharField(max_length=64, null=False,
                            default='DiseaseGeneAssociation')
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE)
    assoc_type = models.CharField(max_length=32, choices=TYPES)
    references = models.ManyToManyField(Reference, blank=True, related_name='gene_assoc_ref')
    modified_by = models.ForeignKey(User, null=True, related_name='disase_gene_modified_user',
                                    on_delete=models.SET_NULL)
    created_by = models.ForeignKey(User, null=True, related_name='disease_gene_created_user',
                                   on_delete=models.SET_NULL)    
    history = HistoricalRecords()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['disease', 'gene'],
                                    name='unique_disease_gene_assoc')
        ]

    def get_type(self):
        return get_tuple(DiseaseGeneAssociation.TYPES, self.assoc_type)

class Frequency(models.Model):
    FREQUENCY = (
        ('HP:0040280', 'Obligate (always present, i.e., in 100% of the cases)'),
        ('HP:0040281', 'Very frequent (present in 80% to 99% of the cases)'),
        ('HP:0040282', 'Frequent (present in 30% to 79% of the cases)'),
        ('HP:0040283', 'Occasional (present in 5% to 29% of the cases)'),
        ('HP:0040284', 'Very rare (present in 1% to 4% of the cases)'),        
        ('HP:0040285', 'Excluded (present in 0% of the cases)'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    value = models.CharField(max_length=12, blank=True, null=True,
                             choices=FREQUENCY)
    other = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['value', 'other'],
                                    name='unique_frequency'),
            models.CheckConstraint(
                check=Q(other__isnull=False) | Q(value__isnull=False),
                name='frequency_not_null'
            )
        ]
        verbose_name_plural = "Frequencies"

    def get_value(self):
        return get_tuple(Frequency.FREQUENCY, self.value)
        
    def __str__(self):
        return '%s{%s, %s}' % (type(self).__name__, self.get_value(), self.other)
        
# consult the annotations here https://hpo.jax.org/app/help/annotations
class DiseasePhenotypeAssociation(Relationship):
    EVIDENCE = (
        ('PCS', 'Published clinical study (PCS)'),
        ('IEA', 'Inferred from electronic annotation (IEA)'),
        ('TAS', 'Traceable author statement (TAS)')
    )
    SEX = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('X', 'Unknown')
    )
    ASPECT = (
        ('P', 'Phenotypic abnormality'),
        ('I', 'Inheritance'),
        ('C', 'Onset and clinical course')
    )
    ONSET = (
        ('HP:0030674', 'Antenatal onset (prior to birth)'),
        ('HP:0003623', 'Neonatal onset (within the first 28 days of life)'),        
        ('HP:0011461', 'Fetal onset (prior to birth but after 8 weeks of gestation)'),
        ('HP:0011460', 'Embryonal onset (up to 8 weeks of gestation)'),
        ('HP:0003577', 'Congenital onset (present at birth)'),        
        ('HP:0410280', 'Pediatric onset (before the age of 16 years, but excluding neonatal or congenital onset)'),
        ('HP:0003593', 'Infantile onset (between 28 days to one year of life)'),
        ('HP:0011463', 'Childhood onset (age of between 1 and 5 years)'),
        ('HP:0003621', 'Juvenile onset (between the age of 5 and 15 years)'),
        ('HP:0003581', 'Adult onset (age of 16 years or later)'),
        ('HP:0011462', 'Young adult onset (age between 16 and 40 years)'),
        ('HP:0003596', 'Middle age onset (age between 40 and 60 years)'),
        ('HP:0003584', 'Late onset (after age of 60 years)'),
    )
    name = models.CharField(max_length=64, null=False,
                            default='DiseasePhenotypeAssociation')
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    phenotype = models.ForeignKey(Phenotype, on_delete=models.CASCADE)
    evidence = models.CharField(max_length=12, default='', choices=EVIDENCE)
    frequency = models.ForeignKey(Frequency, null=True, blank=True,
                                  on_delete=models.CASCADE)
    onset = models.CharField(max_length=12, null=True, blank=True, choices=ONSET)
    sex = models.CharField(max_length=1, null=True, blank=True, choices=SEX)
    modifier = models.ForeignKey(Term, null=True, blank=True,
                                 related_name='modifier_term',
                                 on_delete=models.CASCADE)
    aspect = models.CharField(max_length=1, default='P', choices=ASPECT)
    references = models.ManyToManyField(Reference, blank=True,
                                        related_name='phenotype_assoc_ref')
    modified_by = models.ForeignKey(User, null=True,
                                    related_name='disease_phenotype_modified_user',
                                    on_delete=models.SET_NULL)
    created_by = models.ForeignKey(User, null=True,
                                   related_name='disease_phenotype_created_user',
                                   on_delete=models.SET_NULL)
    history = HistoricalRecords()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['disease', 'phenotype'],
                                    name='unique_disease_pheno_assoc')
        ]
    
    def get_onset(self):
        return get_tuple(DiseasePhenotypeAssociation.ONSET, self.onset)

    def get_evidence(self):
        return get_tuple(DiseasePhenotypeAssociation.EVIDENCE, self.evidence)

    def get_aspect(self):
        return get_tuple(DiseasePhenotypeAssociation.ASPECT, self.aspect)
