#!/usr/bin/env python3
"""Plot article figures
"""

import argparse
import time
import os
from os.path import join as pjoin
import inspect

import sys
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from myutils import info, create_readme
import scipy; from scipy.signal import convolve2d
import imageio

##########################################################
def get_kernel(kerdiam, kerstd, outdir):
    """Get 2d kernel """
    info(inspect.stack()[0][3] + '()')
    ker = (scipy.signal.gaussian(kerdiam, kerstd)).reshape(kerdiam, 1)
    ker2d = np.dot(ker, ker.T)
    ker2d = ker2d / np.sum(ker2d)
    imageio.imwrite(pjoin(outdir, 'kernel.png'), ker2d.astype(np.uint8))
    return ker2d

##########################################################
def diffuse_with_source(imorig, ker2d, refpoints, nsteps, label, outdir):
    """Profile value of @refpoints with diffusion with source"""
    info(inspect.stack()[0][3] + '()')
    im = imorig.copy()
    profile = np.zeros((nsteps, len(refpoints)), dtype=float)
    for i in range(nsteps):
        im = convolve2d(im, ker2d, mode='same')
        im[np.where(imorig == 1)] = 1
        outpath = pjoin(outdir, '{}_{:02d}.png'.format(label, i))
        imageio.imwrite(outpath, im)
        for j, p in enumerate(refpoints):
            x, y = p
            profile[i, j] = im[x, y]
    return profile

##########################################################
def plot_signatures(outdir):
    """Short description """
    info(inspect.stack()[0][3] + '()')

    n = 301
    nquart = int(n / 4)
    m = int(1.5 * nquart)
    nsteps = 10
    l = 8

    refpoints = (np.array([
                [1/4, 1/2],
                [3/8, 1/2],
                [1/2, 1/2],
                ]) * n).astype(int)

    ker2d =  get_kernel(kerdiam=int(n/5), kerstd=int(n/5), outdir=outdir)

    im = np.ones((n, n), dtype=np.uint8); im[nquart:-nquart, nquart:-nquart] = 0
    prof = diffuse_with_source(im, ker2d, refpoints, nsteps, 'A', outdir)
    fig, axs = plt.subplots(1, 1, figsize=(l, l))
    for j in range(prof.shape[1]): axs.plot(range(nsteps), prof[:, j], label=str(j))
    axs.legend(); plt.savefig(pjoin(outdir, 'A.png'))

    im = np.ones((n, n), dtype=np.uint8); im[nquart:-nquart, m:-m] = 0
    prof = diffuse_with_source(im, ker2d, refpoints, nsteps, 'B', outdir)
    fig, axs = plt.subplots(1, 1, figsize=(l, l))
    for j in range(prof.shape[1]): axs.plot(range(nsteps), prof[:, j], label=str(j))
    axs.legend(); plt.savefig(pjoin(outdir, 'B.png'))
      
##########################################################
def main():
    info(inspect.stack()[0][3] + '()')
    t0 = time.time()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir', default='/tmp/out/', help='Output directory')
    args = parser.parse_args()

    if not os.path.isdir(args.outdir): os.mkdir(args.outdir)
    readmepath = create_readme(sys.argv, args.outdir)

    plot_signatures(args.outdir)
    info('For Aiur!')

    info('Elapsed time:{}'.format(time.time()-t0))
    info('Output generated in {}'.format(args.outdir))

##########################################################
if __name__ == "__main__":
    main()
