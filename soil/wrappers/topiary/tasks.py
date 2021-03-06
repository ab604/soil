import os
import pandas as pd
import pypeliner.commandline as cli
import shutil
import subprocess
import tempfile

import soil.utils.file_system
import soil.utils.workflow


def filter_hla_alleles(raw_hla_alleles, iedb_dir=None, predictor='nethmhc'):
    valid_alleles = _get_valid_alleles(iedb_dir, predictor)

    raw_hla_alleles = _parse_alleles(raw_hla_alleles, predictor)

    if valid_alleles is None:
        hla_alleles = raw_hla_alleles

    else:
        hla_alleles = []

        for a in raw_hla_alleles:
            if a in valid_alleles:
                hla_alleles.append(a)

    return hla_alleles


def run_topiary(
        hla_alleles,
        in_file,
        out_file,
        copy_pyensembl_cache_dir=False,
        iedb_dir=None,
        genome='GRCh37',
        peptide_length=9,
        predictor='nethmhc',
        pyensembl_cache_dir=None):

    tmp_cache_dir = None

    try:
        if (pyensembl_cache_dir is not None) and copy_pyensembl_cache_dir:
            tmp_cache_dir = tempfile.mkdtemp()

            shutil.rmtree(tmp_cache_dir)

            shutil.copytree(pyensembl_cache_dir, tmp_cache_dir)

            pyensembl_cache_dir = tmp_cache_dir

        _set_path(iedb_dir, predictor)

        if pyensembl_cache_dir is not None:
            os.environ['PYENSEMBL_CACHE_DIR'] = os.path.abspath(pyensembl_cache_dir)

        hla_alleles = ','.join(hla_alleles)

        cmd = [
            'topiary',

            '--mhc-alleles', hla_alleles,
            '--vcf', in_file,
            '--output-csv', out_file,

            '--genome', genome,
            '--mhc-predictor', predictor,
            '--mhc-peptide-lengths', peptide_length
        ]

        cli.execute(*cmd)

    finally:
        if tmp_cache_dir is not None:
            shutil.rmtree(tmp_cache_dir)


def reformat_output(in_files, out_file):
    data = []

    for file_name in soil.utils.workflow.flatten_input(in_files):
        df = pd.read_csv(file_name, sep=',')

        df = df.drop('#', axis=1)

        data.append(df)

    data = pd.concat(data)

    data.to_csv(out_file, index=False, sep='\t')


def _set_path(iedb_dir, predictor):
    if iedb_dir is not None:
        if predictor == 'netmhc':
            exe_dir = os.path.dirname(soil.utils.file_system.find('netMHC-4.0.readme', iedb_dir))

        elif predictor == 'netmhcpan':
            exe_dir = os.path.dirname(soil.utils.file_system.find('netMHCpan-3.0.readme', iedb_dir))

        os.environ['PATH'] = ':'.join([exe_dir, os.environ['PATH']])


def _parse_alleles(hla_alleles, predictor):
    hla_alleles = [x.replace('HLA-', '') for x in hla_alleles]

    if predictor == 'netmhc':
        return ['HLA-{}'.format(x.replace('*', '').replace(':', '')) for x in hla_alleles]

    elif predictor == 'netmhcpan':
        return ['HLA-{}'.format(x.replace('*', '')) for x in hla_alleles]

    else:
        return hla_alleles


def _get_valid_alleles(iedb_dir, predictor):
    _set_path(iedb_dir, predictor)

    if predictor in ['netmhc', 'netmhcpan']:
        if predictor == 'netmhc':
            raw_out = subprocess.check_output(['netMHC', '-listMHC'])

        else:
            raw_out = subprocess.check_output(['netMHCpan', '-listMHC'])

        valid_alleles = []

        for line in raw_out.split('\n'):
            line = line.strip()

            if line.startswith('HLA'):
                valid_alleles.append(line)

    else:
        valid_alleles = None

    return valid_alleles
