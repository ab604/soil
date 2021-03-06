import click

import soil.utils.cli
import workflows


@soil.utils.cli.runner
@click.option(
    '-a', '--hla-alleles', required=True, multiple=True,
    help='''HLA allele of donor. Can be set multiple times to allow for multiple allele predictions. Example A*02:01.'''
)
@click.option(
    '-i', '--in-file', required=True, type=click.Path(exists=True, resolve_path=True),
    help='''Path of VCF file with variants to identify neoantigens from.'''
)
@click.option(
    '-o', '--out-file', required=True, type=click.Path(resolve_path=True),
    help='''Path where output will be written in TSV format.'''
)
@click.option(
    '--genome', default='GRCh37', type=click.Choice(['GRCh37', 'GRCh38']),
    help='''Genome build of variant coordinates in VCF file.'''
)
@click.option(
    '--predictor', default='netmhc', type=click.Choice(['netmhc', 'netmhcpan']),
    help='''Prediction tool to use.'''
)
@click.option(
    '--iedb-dir', default=None, type=click.Path(exists=True, resolve_path=True),
    help='''Path to data files for MHC-I from http://tools.iedb.org. If this is not set netMHC must be on the PATH.'''
)
@click.option(
    '--pyensembl-cache-dir', default=None, type=click.Path(exists=True, resolve_path=True),
    help='''Path where pyensembl cache files have been downloaded.'''
)
def topiary(hla_alleles, in_file, out_file, genome, iedb_dir, predictor, pyensembl_cache_dir):

    return workflows.create_topiary_workflow(
        hla_alleles,
        in_file,
        out_file,
        iedb_dir=iedb_dir,
        genome=genome,
        predictor=predictor,
        pyensembl_cache_dir=pyensembl_cache_dir
    )
