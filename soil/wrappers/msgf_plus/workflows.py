'''
Created on 24 Apr 2017

@author: Andrew Roth
'''
import pypeliner
import pypeliner.managed as mgd

import soil.utils.workflow
import soil.wrappers.proteowizard.tasks

import tasks


def create_search_workflow(in_fasta_file, in_mzml_file, out_file, split_size=1000):

    sandbox = soil.utils.workflow.get_sandbox(['msgf_plus', 'proteowizard'])

    workflow = pypeliner.workflow.Workflow(default_sandbox=sandbox)

    workflow.transform(
        name='split_mzml_file',
        axes=(),
        func=soil.wrappers.proteowizard.tasks.split_mzml_file,
        args=(
            mgd.InputFile(in_mzml_file),
            mgd.TempOutputFile('spec_data.mzml', 'split'),
            mgd.TempSpace('split_tmp'),
        ),
        kwargs={
            'split_size': split_size,
        }
    )

    workflow.commandline(
        name='copy_db',
        args=(
            'cp',
            mgd.InputFile(in_fasta_file),
            mgd.TempOutputFile('db.fasta', 'split', axes_origin=[]),
        )
    )

    workflow.transform(
        name='run_msgf_plus',
        axes=('split',),
        ctx={'mem': 8, 'mem_retry_increment': 4, 'num_retry': 3},
        func=tasks.run_search,
        args=(
            mgd.TempInputFile('db.fasta', 'split'),
            mgd.TempInputFile('spec_data.mzml', 'split'),
            mgd.TempOutputFile('search.mzid', 'split'),
            mgd.TempSpace('msgf_tmp', 'split'),
        ),
        kwargs={
            'add_decoys': True,
        }
    )

    workflow.commandline(
        name='convert_to_tsv',
        axes=('split',),
        ctx={'mem': 8, 'mem_retry_increment': 4, 'num_retry': 3},
        args=(
            'msgf_plus',
            'MSGFPlus.jar edu.ucsd.msjava.ui.MzIDToTsv',
            '-i', mgd.TempInputFile('search.mzid', 'split'),
            '-o', mgd.TempOutputFile('search.tsv', 'split'),
        )
    )

    workflow.transform(
        name='merge_results',
        func=tasks.merge_results,
        args=(
            mgd.TempInputFile('search.tsv', 'split'),
            mgd.OutputFile(out_file)
        )
    )

    return workflow
