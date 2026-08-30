# Literature Notes For Candidate Events

These notes are intended as biological context for prioritization, not as validation.

## Stronger Context

PFKP is the most directly relevant candidate for metabolism-oriented downstream work. It is a glycolysis gene and therefore maps naturally to genome-scale metabolic model reasoning. The observed AD-higher skipped-exon inclusion should be followed up by transcript/domain mapping before changing model constraints.

MARK3 is relevant to tau and microtubule biology. Its high read support makes it a good visualization and mechanistic-prioritization candidate, although it is not a direct GEM reaction gene in the same way PFKP is.

RBM3 is relevant to neurodegeneration and synaptic stress-response biology. The large delta PSI makes it interesting, but the key next question is whether the event changes coding sequence, UTR behavior, RNA-binding function, or transcript stability.

AMPH is relevant to synaptic vesicle/endocytosis biology and has a plausible AD/synaptic dysfunction connection. It is a good candidate for mechanism discussion and sashimi visualization.

## More Exploratory

PBRM1 has a strong event-level FDR and large delta PSI in this dataset, but the selected event has lower total count than the other sashimi examples. Treat it as exploratory unless replicated or supported by isoform/protein evidence.

## Recommended Next Checks

- Map each selected exon to transcript IDs.
- Determine whether the skipped exon is coding, UTR, frame-preserving, frameshifting, or NMD-linked.
- Check whether the event affects known protein domains.
- Compare with independent AD/control cohorts if available.
- For GEM/iMAT integration, prioritize PFKP first and use splicing as an isoform-level modifier rather than a direct reaction-bound edit unless there is stronger functional evidence.
