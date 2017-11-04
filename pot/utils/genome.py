from collections import OrderedDict

import pysam


def get_regions(chromosome_lengths, split_size):
    if split_size is None:
        return dict(enumerate(chromosome_lengths.keys()))

    regions = {}

    region_index = 0

    for chrom, length in chromosome_lengths.iteritems():
        lside_interval = range(1, length + 1, split_size)

        rside_interval = range(split_size, length + split_size, split_size)

        for beg, end in zip(lside_interval, rside_interval):
            end = min(end, length)

            regions[region_index] = '{}:{}-{}'.format(chrom, beg, end)

            region_index += 1

    return regions


def get_bam_regions(bam_file, split_size, chromosomes=None):
    chromosome_lengths = load_bam_chromosome_lengths(bam_file, chromosomes=chromosomes)

    return get_regions(chromosome_lengths, split_size)


def load_bam_chromosome_lengths(file_name, chromosomes=None):
    chromosome_lengths = OrderedDict()

    bam = pysam.Samfile(file_name, 'rb')

    if chromosomes is None:
        chromosomes = bam.references

    else:
        chromosomes = chromosomes

    for chrom, length in zip(bam.references, bam.lengths):
        if chrom not in chromosomes:
            continue

        chromosome_lengths[str(chrom)] = int(length)

    return chromosome_lengths
