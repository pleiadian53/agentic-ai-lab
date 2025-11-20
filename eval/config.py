"""
Configuration for domain evaluation.

Provides predefined sets of preferred domains organized by category.
"""

# Academic and research institutions
ACADEMIC_DOMAINS = {
    "arxiv.org",
    "acm.org",
    "ieee.org",
    "springer.com",
    "sciencedirect.com",
    "nature.com",
    "science.org",
    "sciencemag.org",
    "cell.com",
    "pnas.org",
    "elifesciences.org",
    "jmlr.org",
    "neurips.cc",
    "icml.cc",
    "openreview.net",
}

# Educational institutions
EDUCATIONAL_DOMAINS = {
    "mit.edu",
    "stanford.edu",
    "harvard.edu",
    "berkeley.edu",
    "cmu.edu",
    "ox.ac.uk",
    "cam.ac.uk",
}

# Government and official sources
GOVERNMENT_DOMAINS = {
    "nasa.gov",
    "noaa.gov",
    "nih.gov",
    "nsf.gov",
    "cdc.gov",
    "usgs.gov",
    "europa.eu",
    "gov.uk",
}

# Reputable news and media
NEWS_DOMAINS = {
    "bbc.com",
    "reuters.com",
    "apnews.com",
    "npr.org",
    "pbs.org",
    "scientificamerican.com",
    "newscientist.com",
}

# Reference and encyclopedic sources
REFERENCE_DOMAINS = {
    "wikipedia.org",
    "britannica.com",
}

# Computational Biology and Bioinformatics
COMPUTATIONAL_BIOLOGY_DOMAINS = {
    # Journals
    "plos.org",  # PLOS Computational Biology, PLOS Biology
    "plosbiology.org",
    "ploscompbiol.org",
    "gigascience.org",
    "gigasciencejournal.com",
    "liebertpub.com",  # Journal of Computational Biology
    "biomedcentral.com",  # BMC Bioinformatics, etc.
    "academic.oup.com",  # Oxford journals (Bioinformatics, NAR, etc.)
    "oup.com",
    "bioinformatics.oxfordjournals.org",
    "nar.oxfordjournals.org",  # Nucleic Acids Research
    "jbc.org",  # Journal of Biological Chemistry
    "jcb.org",  # Journal of Cell Biology
    "mcb.asm.org",  # Molecular and Cellular Biology
    "genesdev.cshlp.org",  # Genes & Development
    "rnajournal.cshlp.org",  # RNA journal
    "cshlp.org",  # Cold Spring Harbor Laboratory Press
    "frontiersin.org",  # Frontiers journals
    "mdpi.com",  # MDPI journals (Genes, Biology, etc.)
    "wiley.com",  # Wiley journals
    "onlinelibrary.wiley.com",
    "embopress.org",  # EMBO journals
    "embojournal.org",
    "elifesciences.org",  # Already in ACADEMIC_DOMAINS but relevant here
    "dev.biologists.org",  # Development journal
    "jneurosci.org",  # Journal of Neuroscience
    
    # Databases and resources
    "ncbi.nlm.nih.gov",  # NCBI (GenBank, PubMed, etc.)
    "nih.gov",  # Already in GOVERNMENT_DOMAINS but critical for bio
    "ebi.ac.uk",  # European Bioinformatics Institute
    "ensembl.org",  # Ensembl genome browser
    "uniprot.org",  # UniProt protein database
    "rcsb.org",  # Protein Data Bank
    "pdb.org",
    "genome.ucsc.edu",  # UCSC Genome Browser
    "ucsc.edu",
    "bioconductor.org",  # Bioconductor (R packages for bioinformatics)
    "biocyc.org",  # BioCyc database collection
    "string-db.org",  # STRING protein interaction database
    "genecards.org",  # GeneCards human gene database
    "omim.org",  # Online Mendelian Inheritance in Man
    "kegg.jp",  # KEGG pathway database
    "reactome.org",  # Reactome pathway database
    "pfam.xfam.org",  # Pfam protein families
    "interpro.ebi.ac.uk",  # InterPro protein classification
}

# RNA Therapeutics and RNA Biology
RNA_THERAPEUTICS_DOMAINS = {
    # Specialized RNA journals
    "rnajournal.cshlp.org",  # RNA journal (also in comp bio)
    "liebertpub.com",  # Nucleic Acid Therapeutics
    "landesbioscience.com",  # RNA Biology
    "silencejournal.com",  # Silence (RNAi journal)
    
    # Major journals with RNA focus
    "cell.com",  # Cell, Molecular Cell, etc.
    "nature.com",  # Nature, Nature Medicine, Nature Methods, etc.
    "science.org",  # Science, Science Translational Medicine
    "sciencemag.org",
    "stm.sciencemag.org",  # Science Translational Medicine
    "nejm.org",  # New England Journal of Medicine
    "pnas.org",  # PNAS (already in ACADEMIC_DOMAINS)
    
    # RNA-specific resources
    "rnacentral.org",  # RNAcentral database
    "mirbase.org",  # miRBase microRNA database
    "gtrnadb.ucsc.edu",  # tRNA database
    "rnamod.org",  # RNA modification database
    "modomics.genesilico.pl",  # RNA modification pathways
    
    # Therapeutic and clinical
    "clinicaltrials.gov",  # Clinical trials database
    "fda.gov",  # FDA resources
    "ema.europa.eu",  # European Medicines Agency
    
    # Research institutions
    "umassmed.edu",  # UMass RNA Therapeutics Institute
    "broadinstitute.org",  # Broad Institute
    "sanger.ac.uk",  # Wellcome Sanger Institute
    "jax.org",  # Jackson Laboratory
}

# Genomics and Genetics
GENOMICS_DOMAINS = {
    "genome.gov",  # NHGRI
    "genomebiology.com",  # Genome Biology journal
    "genome.cshlp.org",  # Genome Research
    "genetics.org",  # Genetics journal
    "ashg.org",  # American Society of Human Genetics
    "nature.com/ng",  # Nature Genetics
    "cell.com/ajhg",  # American Journal of Human Genetics
    "gnomad.broadinstitute.org",  # gnomAD database
    "1000genomes.org",  # 1000 Genomes Project
    "hapmap.ncbi.nlm.nih.gov",  # HapMap
    "gtexportal.org",  # GTEx (gene expression)
    "encode-project.org",  # ENCODE project
    "roadmapepigenomics.org",  # Roadmap Epigenomics
}

# Programming and technical resources
TECHNICAL_DOMAINS = {
    "github.com",
    "stackoverflow.com",
    "python.org",
    "docs.python.org",
    "readthedocs.io",
    "codecademy.com",
    "datacamp.com",
}

# Default comprehensive list (union of all categories)
DEFAULT_PREFERRED_DOMAINS = (
    ACADEMIC_DOMAINS
    | EDUCATIONAL_DOMAINS
    | GOVERNMENT_DOMAINS
    | NEWS_DOMAINS
    | REFERENCE_DOMAINS
    | TECHNICAL_DOMAINS
)

# Biology-focused domain set (for life sciences research)
BIOLOGY_FOCUSED_DOMAINS = (
    ACADEMIC_DOMAINS
    | EDUCATIONAL_DOMAINS
    | GOVERNMENT_DOMAINS
    | COMPUTATIONAL_BIOLOGY_DOMAINS
    | RNA_THERAPEUTICS_DOMAINS
    | GENOMICS_DOMAINS
)

# Minimum ratio thresholds for different evaluation levels
THRESHOLD_STRICT = 0.8  # 80% preferred sources
THRESHOLD_MODERATE = 0.6  # 60% preferred sources
THRESHOLD_LENIENT = 0.4  # 40% preferred sources

# Default threshold
DEFAULT_MIN_RATIO = THRESHOLD_LENIENT


def get_domain_set(category: str = "default") -> set[str]:
    """
    Get a predefined set of preferred domains by category.
    
    Args:
        category: One of 'default', 'academic', 'educational', 'government',
                  'news', 'reference', 'technical', 'computational_biology',
                  'rna_therapeutics', 'genomics', 'biology', or 'all'
    
    Returns:
        Set of domain strings
    
    Examples:
        >>> domains = get_domain_set('academic')
        >>> 'arxiv.org' in domains
        True
        
        >>> bio_domains = get_domain_set('computational_biology')
        >>> 'ncbi.nlm.nih.gov' in bio_domains
        True
    """
    category = category.lower()
    
    if category == "academic":
        return ACADEMIC_DOMAINS.copy()
    elif category == "educational":
        return EDUCATIONAL_DOMAINS.copy()
    elif category == "government":
        return GOVERNMENT_DOMAINS.copy()
    elif category == "news":
        return NEWS_DOMAINS.copy()
    elif category == "reference":
        return REFERENCE_DOMAINS.copy()
    elif category == "technical":
        return TECHNICAL_DOMAINS.copy()
    elif category == "computational_biology":
        return COMPUTATIONAL_BIOLOGY_DOMAINS.copy()
    elif category == "rna_therapeutics":
        return RNA_THERAPEUTICS_DOMAINS.copy()
    elif category == "genomics":
        return GENOMICS_DOMAINS.copy()
    elif category == "biology":
        return BIOLOGY_FOCUSED_DOMAINS.copy()
    elif category in ("default", "all"):
        return DEFAULT_PREFERRED_DOMAINS.copy()
    else:
        raise ValueError(
            f"Unknown category '{category}'. "
            f"Choose from: default, academic, educational, government, "
            f"news, reference, technical, computational_biology, "
            f"rna_therapeutics, genomics, biology, all"
        )


def create_custom_domain_set(*categories: str, extra_domains: set[str] | None = None) -> set[str]:
    """
    Create a custom domain set by combining multiple categories.
    
    Args:
        *categories: Category names to combine
        extra_domains: Additional domains to include
    
    Returns:
        Combined set of domains
    
    Examples:
        >>> domains = create_custom_domain_set('academic', 'government')
        >>> len(domains) > 0
        True
        
        >>> domains = create_custom_domain_set('academic', extra_domains={'myjournal.org'})
        >>> 'myjournal.org' in domains
        True
    """
    result = set()
    
    for category in categories:
        result |= get_domain_set(category)
    
    if extra_domains:
        result |= extra_domains
    
    return result
