import numpy as np

def findMarkers(chunk, labels):
    markers = []
    for label in labels:
        foundMarker = [marker for marker in chunk.markers if marker.label == label]
        if len(foundMarker) == 1: markers.append(foundMarker[0])

    return markers

def setRegion(chunk, scaler):
    # Find midpoint of volume
    markers = findMarkers(chunk, ['target 15', 'target 11', 'target 13', 'target 9'])
    points = np.array([[marker.position.x, marker.position.y, marker.position.z] for marker in markers])
    centroid = Metashape.Vector(np.mean(points, axis=0))

    # Compute distance between the width markers
    widthMarkers = findMarkers(chunk, ['target 11', 'target 15'])
    cageWidth = (widthMarkers[0].position - widthMarkers[1].position).norm()

    # Align region with chunk (presumes chunk has already been cleaned)
    chunk.region.rot = chunk.transform.rotation.t()
    yAxis = Metashape.Matrix.Rotation(chunk.region.rot).mulv(Metashape.Vector((0, 1, 0)))
    if scaler > 0.75:
        chunk.region.center = centroid
    else:
        # Slightly lower than centroid
        adjust = cageWidth * 0.1
        chunk.region.center = Metashape.Vector((
            centroid.x - yAxis.x * adjust,
            centroid.y - yAxis.y * adjust,
            centroid.z - yAxis.z * adjust
        ))

    chunk.addMarker(chunk.region.center).label = 'Rc'

    # Set size according to parameter
    if scaler > 0.75:
        chunk.region.size = Metashape.Vector([cageWidth * scaler, cageWidth * scaler, cageWidth * scaler])
    else:
        chunk.region.size = Metashape.Vector([cageWidth * scaler, cageWidth * 0.75, cageWidth * scaler])

def fitPlaneToMarkers(markers):
    # Pack markers into matrix subtracting centroid
    points = np.array([
        [marker.position.x, marker.position.y, marker.position.z] for marker in markers
    ])

    # Calculate the centroid of the points
    centroid = np.mean(points, axis=0)

    # Calculate the covariance matrix
    centered_points = points - centroid
    covariance_matrix = np.cov(centered_points.T)

    # Calculate the eigenvectors and eigenvalues
    eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)

    # The best-fit normal vector is the eigenvector corresponding to the smallest eigenvalue
    normal = eigenvectors[:, np.argmin(eigenvalues)]

    # Return normal and centroid
    return Metashape.Vector(normal), Metashape.Vector(centroid)

def computeBasisFromCoplanerMarkers(chunk, markerLabels):
    # Find the relevant targets
    targets = findMarkers(chunk, markerLabels)
    print(targets)

    # Compute best-fit plane
    up, centroid = fitPlaneToMarkers(targets)

    # Compute view direction from first two targets
    v = (targets[0].position - targets[1].position).normalized()

    # Return normal, view direction, and center of mass
    return up, v, centroid

def applyBasis(chunk, t, u, v, c):
    chunk.transform.matrix = Metashape.Matrix([
        [ t.x,  t.y,  t.z, -c.x],
        [ u.x,  u.y,  u.z, -c.y],
        [-v.x, -v.y, -v.z, -c.z],
        [0, 0, 0, 1]
    ])

def visualizeBasis(chunk, t, u, v, c):
    chunk.addMarker(c).label = 'C'
    chunk.addMarker(c + 1.5*t).label = ''
    chunk.addMarker(c + 1.5*u).label = ''
    chunk.addMarker(c + 1.5*v).label = ''

    chunk.addScalebar(chunk.markers[-4], chunk.markers[-3]).label = 'T'
    chunk.addScalebar(chunk.markers[-4], chunk.markers[-2]).label = 'U'
    chunk.addScalebar(chunk.markers[-4], chunk.markers[-1]).label = 'V'

def chunkCorrect(chunk):
    # Compute a basis from markers in the scene
    up, view, c = computeBasisFromCoplanerMarkers(chunk,
        ['target 15', 'target 11', 'target 13', 'target 9']
    )

    # Use markers to find a known "upward" vector
    upMarkers = findMarkers(chunk, ['target 11', 'target 18'])
    upward = (upMarkers[1].position - upMarkers[0].position).normalized()

    # If up vector is opposite to the upward vector, flip it
    if up * upward < 0: up = -up

    # Compute rest of basis and apply to chunk
    t = Metashape.Vector.cross(view, up).normalized()
    v = Metashape.Vector.cross(up, t).normalized()
    chunk.addMarker(c).label = 'C'
    applyBasis(chunk, t, up, v, c)

    # Apply a final fudge rotation to correct for non-planer markers
    fudgeMatrix = Metashape.Matrix([
        [0.9993, -0.0373, -0.0025],
        [0.0371,  0.9981, -0.0482],
        [0.0043,  0.0481,  0.9988]
    ])
    chunk.transform.rotation = fudgeMatrix * chunk.transform.rotation

def filterTiePoints(chunk):
    # Compute distance between the width markers
    widthMarkers = findMarkers(chunk, ['target 11', 'target 15'])
    cageWidth = (widthMarkers[0].position - widthMarkers[1].position).norm()

    # Find midpoint of volume
    markers = findMarkers(chunk, ['target 15', 'target 11', 'target 13', 'target 9'])
    points = np.array([[marker.position.x, marker.position.y, marker.position.z] for marker in markers])
    centroid = Metashape.Vector(np.mean(points, axis=0))

    # General size to limit
    horizSize = 2.138 * cageWidth
    vertSize = 1.145 * cageWidth

    # Select tie points outside bounding box
    BBRegion = chunk.region.copy()
    BBRegion.size = Metashape.Vector([horizSize, vertSize, horizSize])
    BBRegion.center = centroid
    selectTiePointsOutsideBoundingBox(chunk, BBRegion)

def selectTiePointsOutsideBoundingBox(chunk, region):
    for tiePoint in chunk.tie_points.points:
        checkPoint(tiePoint, region)

def checkPoint(point, region):
	R = region.rot		# Bounding box rotation matrix
	C = region.center	# Bounding box center vector
	size = region.size

	v = point.coord
	v.size = 3
	v_c = v - C
	v_r = R.t() * v_c

	if abs(v_r.x) > abs(size.x / 2.):
		point.selected = True
	elif abs(v_r.y) > abs(size.y / 2.):
		point.selected = True
	elif abs(v_r.z) > abs(size.z / 2.):
		point.selected = True
	else:
		point.selected = False

T = Metashape.Vector([-0.2584722977580742,  0.8917901019142753, 0.371349586534559])
U = Metashape.Vector([ 0.7983857193443118, -0.0191399011945906, 0.601761719727441])
V = Metashape.Vector([-0.5437837677600905, -0.4520205066991530, 0.707043291067867])
C = Metashape.Vector([0.7620915626907145, -0.048169224042599934, -3.0163309698955088])
