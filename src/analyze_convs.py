#!/usr/bin/env python3
"""Analyze convolutions
"""

import argparse
import time
import os, sys
from os.path import join as pjoin
import inspect

import numpy as np
from itertools import product
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import h5py
from scipy import ndimage
from myutils import info, create_readme
import imageio

##########################################################
def hdf2numpy(hdfpath):
    """Convert hdf5 file to numpy """
    with h5py.File(hdfpath, 'r') as f:
        data = np.array(f['data'])
    return data

##########################################################
def plot_disttransform(figsize, mask0, outpath):
    """Short description """
    info(inspect.stack()[0][3] + '()')

    plt.figure(figsize=figsize)
    distransf = ndimage.distance_transform_edt(mask0.astype(int))
    plt.imshow(distransf)
    plt.colorbar()
    plt.savefig(outpath)

##########################################################
def list_hdffiles_and_stds(hdfdir):
    """Get list of standard deviations from filenames in the directory"""
    info(inspect.stack()[0][3] + '()')

    hdfpaths = []
    stds = []

    for f in sorted(os.listdir(hdfdir)):
        if not f.endswith('.hdf5'): continue
        hdfpaths.append(pjoin(hdfdir, f))
        stds.append(int(f.replace('.hdf5', '')))

    return hdfpaths, stds

##########################################################
def parse_urban_mask(maskpath, maskshape):
    """Short description """
    info(inspect.stack()[0][3] + '()')

    if maskpath:
        mask = imageio.imread(maskpath)
        mask = (mask > 128)[0]
    else:
        mask = np.ones(maskshape, dtype=bool)

    import cv2

    borderpts, _ = cv2.findContours(mask.astype(np.uint8),
            cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return borderpts, mask

##########################################################
def plot_contour(maskpath):
    """Plot the contour"""
    info(inspect.stack()[0][3] + '()')

    import cv2
    im = cv2.imread(maskpath)
    breakpoint()

    imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(imgray,127,255,0)
    image, contours, hierarchy = cv2.findContours(thresh,
            cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
##########################################################
def plot_threshold(minpixarg, hdfdir, mask0, urbanmaskarg, figsize, outpath):
    """Plot the required time of the pixels of a map to achieve a minimum value"""
    info(inspect.stack()[0][3] + '()')

    hdfpaths, stds = list_hdffiles_and_stds(hdfdir)

    if minpixarg < 0:
        # By setting this value, I guarantee *all* pixels will achieve the
        # minimum desired values
        largeststdpath = pjoin(hdfdir, '{:02d}.hdf5'.format(sorted(stds)[-1]))
        minpix = np.min(hdf2numpy(largeststdpath))
    else:
        minpix = minpixarg

    info('minpix:{}'.format(minpix))

    urbanborder, urbanmask = parse_urban_mask(urbanmaskarg, mask0.shape)

    steps = -10*np.ones(mask0.shape, dtype=float) # Num steps to achieve minpix
    
    info('Traversing backwards...')
    nstds = len(stds)
    for i, std in enumerate(sorted(stds, reverse=True)): # Traverse backwards
        k = nstds - i
        info('diff step:{}'.format(std))
        mask = hdf2numpy(pjoin(hdfdir, '{:02d}.hdf5'.format(std)))
        inds = np.where(mask >= minpix)
        steps[inds] = k # Keep the minimum time to achieve minpix
        # if i > 10: break #TODO: REMOVE THIS

    # from matplotlib import cm
    # from matplotlib.colors import ListedColormap, LinearSegmentedColormap
    # mycmap = cm.get_cmap('jet', 12)

    fig, ax = plt.subplots(figsize=figsize, dpi=100)
    im = ax.imshow(steps,
            # cmap=mycmap,
            # norm=matplotlib.colors.LogNorm(vmin=steps.min(), vmax=steps.max()),
            )
    ax.set_title('Initial mean:{:.02f}, threshold:{:.02f}'. \
            format(np.mean(mask0), minpix))
    fig.colorbar(im)
    plt.savefig(outpath)

##########################################################
def main():
    info(inspect.stack()[0][3] + '()')
    t0 = time.time()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hdfdir', default='/tmp/out/', help='Hdf5 directory')
    parser.add_argument('--urbanmask', help='Hdf5 directory')
    parser.add_argument('--minpix', type=float, default=-1, help='Min pixel value')
    parser.add_argument('--outdir', default='/tmp/out/', help='Output directory')
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    readmepath = create_readme(sys.argv, args.outdir)

    W = 640; H = 480; figsize=(W*.01, H*.01)

    mask0 = hdf2numpy(pjoin(args.hdfdir, '00.hdf5'))

    distpath = pjoin(args.outdir, 'distransform.png')
    # plot_disttransform(figsize, mask0, distpath)

    threshpath = pjoin(args.outdir, 'diffusion_{:03d}'.format(int(args.minpix*100)))
    plot_threshold(args.minpix, args.hdfdir, mask0, args.urbanmask,
            figsize, threshpath)

    info('Elapsed time:{}'.format(time.time()-t0))

##########################################################
if __name__ == "__main__":
    main()
