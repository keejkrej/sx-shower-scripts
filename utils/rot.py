import numpy as np

def det2q(point, ai):
    # 1=vertical, 2=horizontal, origin at bottom left, 3=sample-detector
    d1, d2, zrot = point # unit (px, px, deg)
    dn1 = d1 * ai.pixel1 - ai.poni1 # unit (m)
    dn2 = d2 * ai.pixel2 - ai.poni2 # unit (m)
    L = ai.dist # unit (m)

    xp = ai.rotation_matrix() @ np.array((dn1, dn2, L), dtype=object) # unit (m)
    # xp = np.array((dn1, dn2, L), dtype=object) # unit (m)
    alpha = np.arctan(xp[0] / np.linalg.norm(xp))
    phi = np.arctan(xp[1] / np.linalg.norm(xp))
    k = 2 * np.pi / (ai.wavelength * 1e10) # unit (1/A)

    q1 = k * np.sin(alpha) # unit (1/A)
    q2 = k * np.cos(alpha) * np.sin(phi) # unit (1/A)
    q3 = k * (np.cos(alpha) * np.cos(phi) - 1) # unit (1/A)

    zrot = np.deg2rad(zrot) # unit (rad)
    q2p = np.cos(zrot) * q2 - np.sin(zrot) * q3 # unit (1/A)
    q3p = np.sin(zrot) * q2 + np.cos(zrot) * q3 # unit (1/A)

    return q1, q2p, q3p

def qsize(qpoints, ai, dq):
    qx_min, qx_max = np.min(qpoints[0]), np.max(qpoints[0])
    qy_min, qy_max = np.min(qpoints[1]), np.max(qpoints[1])
    qz_min, qz_max = np.min(qpoints[2]), np.max(qpoints[2])
    qrange = ((qx_min, qx_max), (qy_min, qy_max), (qz_min, qz_max))

    nqx = int(np.floor((qx_max - qx_min) / dq + 0.5))
    nqy = int(np.floor((qy_max - qy_min) / dq + 0.5))
    nqz = int(np.floor((qz_max - qz_min) / dq + 0.5))
    nq = (nqx, nqy, nqz)

    return qrange, nq

def qrebin(qpoints, qrange, nq, intensity):
    qpoints_flatten = (qpoints[0].flatten(), qpoints[1].flatten(), qpoints[2].flatten())
    print(qpoints_flatten[0].shape)
    I_hist, _ = np.histogramdd(qpoints_flatten, bins=nq, range=qrange, weights=intensity.flatten())
    n_hist, _ = np.histogramdd(qpoints_flatten, bins=nq, range=qrange)
    I_hist[n_hist > 0] /= n_hist[n_hist > 0]

    return I_hist

def qtransform(img, ai, dq):
    d1_arr = np.arange(img.shape[0])
    d2_arr = np.arange(img.shape[1])
    zrot_arr = 0

    points = np.meshgrid(d1_arr, d2_arr, zrot_arr, indexing='ij') # indexing important, default is 'xy' (swap d1 and d2)

    qpoints = det2q(points, ai)
    qrange, nq = qsize(qpoints, ai, dq)

    return qrebin(qpoints, qrange, nq, img)