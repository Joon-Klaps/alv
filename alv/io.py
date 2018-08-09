from Bio import AlignIO
from math import log
from .alignment import aaAlignment, dnaAlignment, codonAlignment
from .colorize import aaPainter, dnaPainter, codonPainter, aaHydrophobicity, aaTaylorPainter


def read_alignment(filename, args):
    '''
    Factory function. Read the alignment with BioPython's support, and 
    return an appropriate alv alignment, by looking at input options.
    '''
    seqtype = args.type
    input_format = args.format

    alignment = AlignIO.read(args.infile, input_format)
    if seqtype == 'guess':
        seqtype = guess_seq_type(alignment)
        
    if args.color_scheme == 'taylor':
        painter = aaTaylorPainter(args)
    elif args.color_scheme == 'hydrophobicity':
        painter = aaHydrophobicity(args)
    else:
        painter = aaPainter(args)
        
    if seqtype == 'aa':
        return aaAlignment(alignment), painter
    if seqtype == 'dna':
        return dnaAlignment(alignment), dnaPainter(args)
    elif seqtype == 'codon':
        al = codonAlignment(alignment)
        al.set_genetic_code(args.code)
        return codonAlignment(alignment), codonPainter(args, painter)
    else:
        raise Exception('Unknown option')

    return alignment, painter




            
def guess_seq_type(al):
    '''
    Guess whether alignment al is AA, DNA, coding DNA, or RNA and
    return an appropriate string. RNA is treated as DNA.
    The probabilities are very rough estimates/guesses (and computed in
    log-space).
    '''
    p_aa = _likelihood_of_seq(al, _aa_distr)
    p_dna = _likelihood_of_seq(al, _dna_distr)
    if p_dna < p_aa:
        return 'aa'
    else:
        p_coding = _likelihood_of_codons(al)
        if p_dna > p_coding:
            return 'dna'
        else:
            return 'codon'
        
def _likelihood_of_seq(al, distr):
    log_p = 0.0
    for rec in al:
        for c in rec.seq:
            if c in distr:
                log_p += distr[c]
    return log_p

def _likelihood_of_codons(al):
    log_p = 0.0
    l = len(str(al[0]))
    for rec in al:
        for pos in range(0,l,3):
            codon = str(rec.seq[pos:pos+3])
            if codon in _codon_distr:
                log_p += _codon_distr[codon]
    return log_p

# Overkill: using amino acid frequencies given for vertebrates, found somewhere on the internet.
_aa_distr = {
    'A': log(0.074),
    'R': log(0.042),
    'N': log(0.044),
    'D': log(0.059),
    'C': log(0.033),
    'E': log(0.058),
    'Q': log(0.037),
    'G': log(0.074),
    'H': log(0.029),
    'I': log(0.038),
    'L': log(0.076),
    'K': log(0.072),
    'M': log(0.018),
    'F': log(0.04),
    'P': log(0.05),
    'S': log(0.081),
    'T': log(0.062),
    'W': log(0.013),
    'Y': log(0.033),
    'V': log(0.066),            # Should be 0.068, but I am giving away 0.1+0.1 to X and *
    'X': log(0.01),
    '*': log(0.01)
    }
_dna_distr = {
    # Nucleotide frequncies are rounded down somewhat, leaving 2% for the other letters. 2/18=0.11111111.
    'A': log(0.30),
    'C': log(0.21),
    'G': log(0.26),
    'T': log(0.22),
    'U': log(0.22),             # It is either DNA or RNA and at this point I don't care.

    # Remaining (?) letters
    'B': log(0.0011),
    'R': log(0.0011),
    'N': log(0.0011),
    'D': log(0.0011),
    'E': log(0.0011),
    'Q': log(0.0011),
    'H': log(0.0011),
    'I': log(0.0011),
    'L': log(0.0011),
    'K': log(0.0011),
    'M': log(0.0011),
    'F': log(0.0011),
    'P': log(0.0011),
    'S': log(0.0011),
    'W': log(0.0011),
    'Y': log(0.0011),
    'V': log(0.0011),
    'X': log(0.0011),
    }

_codon_distr = {
    'TTT': log(0.0169),
    'TTC': log(0.0204),
    'TTA': log(0.0072),
    'TTG': log(0.0126),

    'TCT': log(0.0146),
    'TCC': log(0.0174),
    'TCA': log(0.0117),
    'TCG': log(0.0045),

    'TAT': log(0.012),
    'TAC': log(0.0156),
    'TAA': log(0.0007),         # STOP
    'TAG': log(0.0005),         # STOP

    'TGT': log(0.0099),
    'TGC': log(0.0122),
    'TGA': log(0.0013),         # STOP
    'TGG': log(0.0128),

    'CTT': log(0.0128),
    'CTC': log(0.0194),
    'CTA': log(0.0069),
    'CTG': log(0.0403),

    'CCT': log(0.0173),
    'CCC': log(0.020),
    'CCA': log(0.0167),
    'CCG': log(0.007),

    'CAT': log(0.0104),
    'CAC': log(0.0149),
    'CAA': log(0.0118),
    'CAG': log(0.0346),

    'CGT': log(0.0047),
    'CGC': log(0.0109),
    'CGA': log(0.0063),
    'CGG': log(0.0119),
    
    'ATT': log(0.0157),
    'ATC': log(0.0214),
    'ATA': log(0.0071),
    'ATG': log(0.0223),

    'ACT': log(0.0128),
    'ACC': log(0.0192),
    'ACA': log(0.0148),
    'ACG': log(0.0062),

    'AAT': log(0.0167),
    'AAC': log(0.0195),
    'AAA': log(0.024),
    'AAG': log(0.0329),

    'AGT': log(0.0119),
    'AGC': log(0.0194),
    'AGA': log(0.0115),
    'AGG': log(0.0114),

    'GTT': log(0.0109),
    'GTC': log(0.0146),
    'GTA': log(0.007),
    'GTG': log(0.0289),

    'GCT': log(0.0186),
    'GCC': log(0.0285),
    'GCA': log(0.016),
    'GCG': log(0.0076),

    'GAT': log(0.0223),
    'GAC': log(0.026),
    'GAA': log(0.029),
    'GAG': log(0.0408),

    'GGT': log(0.0108),
    'GGC': log(0.0228),
    'GGA': log(0.0163),
    'GGG': log(0.0164),
    }
