#!/usr/bin/env python

import numpy as np
from numpy.linalg import norm, inv
from bvec_rotation import read_bvecs, read_bvals
import argparse
import os, warnings, sys
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import nibabel as nib

PRECISION= 17
np.set_printoptions(precision= PRECISION)

def bvec_scaling(bval, bvec, b_max):
    
    if bval:
        factor= np.sqrt(b_max/bval)
        if norm(bvec)!=factor:
            bvec= np.array(bvec)*factor

    # bvec= [str(np.round(x, precision)) for x in bvec]
    bvec= [str(x) for x in bvec]

    return ('   ').join(bvec)


def matrix_string(A):
    # A= np.array(A)
    
    A= str(A.tolist())
    A= A.replace(', ',',')
    A= A.replace('],[',') (')
    return '('+A[2:-2]+')'
    
    
def main():

    parser = argparse.ArgumentParser(description='Given path prefix, writes a prefix.nhdr file')
    parser.add_argument('-p', '--prefix', type=str, required=True,
                        help='prefix for prefix.nii.gz, prefix.bval, and prefix.bvec files')

    args = parser.parse_args()
    prefix= args.prefix

    nifti_file= prefix.split('/')[-1]+'.nii.gz'
    encoding= 'gzip'
    if not os.path.exists(nifti_file):
        nifti_file= prefix+'.nii'
        encoding= 'raw'

    img= nib.load(nifti_file)
    hdr= img.header

    bval_file= prefix+'.bval'
    bvec_file= prefix+'.bvec'

    bvecs= read_bvecs(bvec_file)
    bvals= read_bvals(bval_file)
    
    nhdr_file=prefix+'.nhdr'
    f= open(nhdr_file,'w')
    console= sys.stdout
    sys.stdout= f
    

    dim= hdr['dim'][0]
    print(f'NRRD0005\n# This nhdr file was generated by pnl.bwh.harvard.edu pipeline\n\
# See https://github.com/pnlbwh for more info\n\
# Complete NRRD file format specification at:\n\
# http://teem.sourceforge.net/nrrd/format.html\n\
type: short\ndimension: {dim}\nspace: right-anterior-superior')

    sizes= hdr['dim'][1:dim+1]
    print('sizes: {}'.format((' ').join(str(x) for x in sizes)))

    spc_dir= hdr.get_sform()[0:3,0:3].T
    print(f'space directions: {matrix_string(spc_dir)}')


    # most important key
    print('byteskip: -1')

    print(f'endian: little\nencoding: {encoding}')
    print('space units: "mm" "mm" "mm"')


    spc_orig= hdr.get_sform()[0:3,3]
    print('space origin: ({})'.format((',').join(str(x) for x in spc_orig)))

    print('data file: ',nifti_file)



    if dim==4:
        print('centerings: cell cell cell ???')
        print('kinds: space space space list')
        res = hdr['pixdim'][1:4]
        mf = inv(np.diag(res)) @ spc_dir
        print(f'measurement frame: {matrix_string(mf)}')
    else:
        print('centerings: cell cell cell')
        print('kinds: space space space')

    print('modality:=DWMRI')
    

    b_max= max(bvals)
    print(f'DWMRI_b-value:={b_max}')
    for ind in range(len(bvals)):
        scaled_bvec= bvec_scaling(bvals[ind], bvecs[ind], b_max)
        print(f'DWMRI_gradient_{ind:04}:={scaled_bvec}')
        
    f.close()
    sys.stdout= console


if __name__ == '__main__':
    main()