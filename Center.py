import Metashape
import numpy as np

def findCenter(chunk):
    # Get references to the four floor markers
    m4 = chunk.markers[4].position
    m5 = chunk.markers[5].position
    m6 = chunk.markers[6].position
    m7 = chunk.markers[7].position

    # Compute centroid of four markers
    cent = Metashape.Vector((
        (m4.x + m5.x + m6.x + m7.x) / 4,
        (m4.y + m5.y + m6.y + m7.y) / 4,
        (m4.z + m5.z + m6.z + m7.z) / 4
    ))

    # Pack floor markers into matrix subtracting centroid
    planeMatrix = np.array([
        [m4.x - cent.x, m4.y - cent.y, m4.z - cent.z],
        [m5.x - cent.x, m5.y - cent.y, m5.z - cent.z],
        [m6.x - cent.x, m6.y - cent.y, m6.z - cent.z],
        [m7.x - cent.x, m7.y - cent.y, m7.z - cent.z]
    ])

    # Compute SVD of plane matrix to get best fitting plane
    u, s, vh = np.linalg.svd(planeMatrix)

    # Find least significant value
    minVal = 100000
    minIdx = 0
    i = 0
    for sv in s:
        if sv < minVal:
            minIdx = i
            minVal = sv
        i += 1

    # Construct best-fit plane normal from left singular vector of
    # least sig value
    up = Metashape.Vector((u[0, minIdx], u[1, minIdx], u[2, minIdx]))
    up.normalize()
    print(up)

    # Construct view vector to be z
    v = chunk.markers[3].position - chunk.markers[2].position
    v.normalize()

    # Construct orthogonal u axis
    u = Metashape.Vector.cross(v, up)
    u.normalize()

    # Construct orthogonal n axis (points upward)
    n = Metashape.Vector.cross(u, v)
    n.normalize()

    # SFB Change of basis matrix
    Metashape.app.document.chunk.transform.rotation = np.array([
        [u.x, u.y, u.z],
        [v.x, v.y, v.z],
        [n.x, n.y, n.z],
    ])

    print(basis)
    return basis
