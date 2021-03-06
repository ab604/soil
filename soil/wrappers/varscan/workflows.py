'''
Created on 8 Apr 2017

@author: Andrew Roth
'''
import pypeliner
import pypeliner.managed as mgd

import soil.utils.genome
import soil.utils.workflow
import soil.wrappers.samtools.tasks

import tasks

low_mem_ctx = {'mem': 2, 'mem_retry_factor': 2, 'num_retry': 3}
med_mem_ctx = {'mem': 4, 'mem_retry_factor': 2, 'num_retry': 3}


def create_pileup2snp_workflow(bam_file, ref_genome_fasta_file, out_file, chromosomes=None, split_size=int(1e7)):

    sandbox = soil.utils.workflow.get_sandbox(['bcftools', 'samtools', 'varscan'])

    workflow = pypeliner.workflow.Workflow(default_ctx=low_mem_ctx, default_sandbox=sandbox)

    workflow.setobj(
        obj=pypeliner.managed.TempOutputObj('config', 'regions'),
        value=soil.utils.genome.get_bam_regions(bam_file, split_size, chromosomes=chromosomes)
    )

    workflow.commandline(
        name='run_mpileup',
        axes=('regions',),
        args=(
            'samtools',
            'mpileup',
            '-f', mgd.InputFile(ref_genome_fasta_file),
            '-o', mgd.TempOutputFile('region.mpileup', 'regions'),
            '-r', mgd.TempInputObj('config', 'regions'),
            mgd.InputFile(bam_file),
        )
    )

    workflow.transform(
        name='run_mpileup2snp',
        axes=('regions',),
        ctx=med_mem_ctx,
        func=tasks.mpileup2snp,
        args=(
            mgd.TempInputFile('region.mpileup', 'regions'),
            mgd.TempOutputFile('region.vcf', 'regions'),
        )
    )

    workflow.transform(
        name='compress',
        axes=('regions',),
        func=soil.wrappers.samtools.tasks.compress_vcf,
        args=(
            mgd.TempInputFile('region.vcf', 'regions'),
            mgd.TempOutputFile('region.vcf.gz', 'regions'),
        ),
    )

    workflow.transform(
        name='concatenate_vcfs',
        func=soil.wrappers.samtools.tasks.concatenate_vcf,
        args=(
            mgd.TempInputFile('region.vcf.gz', 'regions'),
            mgd.OutputFile(out_file),
        ),
    )

    return workflow
