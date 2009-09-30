#!/usr/bin/python
# vim:tabstop=4:shiftwidth=4:syntax=python:expandtab
"""
    This Version: $Id: 3ds2egg.py,v 1.13 2008/06/03 03:48:15 andyp Exp $
    Info: info >at< pfastergames.com

    Extended from: http://panda3d.org/phpbb2/viewtopic.php?t=3378
    .___..__ .___.___.___.__..__ .  .
      |  [__)[__ [__ [__ |  |[__)|\/|
      |  |  \[___[___|   |__||  \|  |
    obj2egg.py [n##][b][t][s] filename1.3ds ...
        -n regenerate normals with # degree smoothing
            exaple -n30  (normals at less 30 degrees will be smoothed)
        -b make binarmals
        -t make tangents
        -s show in pview

    licensed under WTFPL (http://sam.zoy.org/wtfpl/)
"""

from pandac.PandaModules import *
import struct
import math
import string
import getopt
import sys, os


def floats(float_list):
    """coerce a list of strings that represent floats into a list of floats"""
    return [ float(number) for number in float_list ]

def ints(int_list):
    """coerce a list of strings that represent integers into a list of integers"""
    return [ int(number) for number in int_list ]

class TDSChunk:
    CHUNK_ATTRIB = {}
    # if "container" is True, then try to subdivide the chunk.
    # "name" is a printable name for the id.
    # see initChunkmakers() and TDSChunk.chunkmaker() for how the
    # "make" attrib is used.
    # the pieces of the .egg are produced on the return path of
    # a recursive traversal of the "chunk tree....have a look at
    # a few of the eggifygeometry() methods in various chunks...
    # generally, leaf chunks push relevant data up into their
    # parent's attribute dict.
    CHUNK_ATTRIB[0x4d4d] = { "container":  True, "name": "root" }
    CHUNK_ATTRIB[0x0002] = { "container": False, "name": "version" }
    CHUNK_ATTRIB[0x0010] = { "container": False, "name": "colorf" }
    CHUNK_ATTRIB[0x0011] = { "container": False, "name": "color24" }
    CHUNK_ATTRIB[0x0030] = { "container": False, "name": "percentage" }
    CHUNK_ATTRIB[0x0100] = { "container": False, "name": "scale" }
    CHUNK_ATTRIB[0x1200] = { "container":  True, "name": "solidbackground" }
    CHUNK_ATTRIB[0x1201] = { "container":  True, "name": "usesolidbackground" }
    CHUNK_ATTRIB[0x1300] = { "container": False, "name": "vgradient" }
    CHUNK_ATTRIB[0x1400] = { "container": False, "name": "loshadowbias" }
    CHUNK_ATTRIB[0x1410] = { "container": False, "name": "hishadowbias" }
    CHUNK_ATTRIB[0x1420] = { "container": False, "name": "shadowmapsize" }
    CHUNK_ATTRIB[0x1450] = { "container": False, "name": "shadowfilter" }
    CHUNK_ATTRIB[0x1460] = { "container": False, "name": "raybias" }
    CHUNK_ATTRIB[0x2100] = { "container":  True, "name": "ambientlight" }
    CHUNK_ATTRIB[0x2200] = { "container": False, "name": "fog" }
    CHUNK_ATTRIB[0x2300] = { "container": False, "name": "distancecue" }
    CHUNK_ATTRIB[0x2302] = { "container": False, "name": "layerfog" }
    CHUNK_ATTRIB[0x3d3d] = { "container":  True, "name": "edit3ds" }
    CHUNK_ATTRIB[0x3d3e] = { "container": False, "name": "meshversion" }
    CHUNK_ATTRIB[0x4000] = { "container":  True, "name": "namedobject" }
    CHUNK_ATTRIB[0x4100] = { "container":  True, "name": "triobject" }
    CHUNK_ATTRIB[0x4110] = { "container": False, "name": "points" }
    CHUNK_ATTRIB[0x4111] = { "container": False, "name": "vertexoptions" }
    CHUNK_ATTRIB[0x4120] = { "container":  True, "name": "faces" }
    CHUNK_ATTRIB[0x4130] = { "container": False, "name": "meshmatgroup" }
    CHUNK_ATTRIB[0x4140] = { "container": False, "name": "uvs" }
    CHUNK_ATTRIB[0x4150] = { "container": False, "name": "smoothgroup" }
    CHUNK_ATTRIB[0x4160] = { "container": False, "name": "meshmatrix" }
    CHUNK_ATTRIB[0x4165] = { "container": False, "name": "meshcolor" }
    CHUNK_ATTRIB[0x4700] = { "container": False, "name": "camera" }
    CHUNK_ATTRIB[0x8000] = { "container":  True, "name": "xdata" }
    CHUNK_ATTRIB[0x8001] = { "container": False, "name": "xdataentry" }
    CHUNK_ATTRIB[0xa000] = { "container": False, "name": "materialname" }
    CHUNK_ATTRIB[0xa010] = { "container":  True, "name": "ambient" }
    CHUNK_ATTRIB[0xa020] = { "container":  True, "name": "diffuse" }
    CHUNK_ATTRIB[0xa030] = { "container":  True, "name": "specular" }
    CHUNK_ATTRIB[0xa040] = { "container":  True, "name": "shininess" }
    CHUNK_ATTRIB[0xa041] = { "container":  True, "name": "shininess2" }
    CHUNK_ATTRIB[0xa050] = { "container":  True, "name": "transparency" }
    CHUNK_ATTRIB[0xa052] = { "container":  True, "name": "xpfall" }
    CHUNK_ATTRIB[0xa053] = { "container":  True, "name": "refblur" }
    CHUNK_ATTRIB[0xa081] = { "container":  True, "name": "twosided" }
    CHUNK_ATTRIB[0xa084] = { "container":  True, "name": "selfillumpercent" }
    CHUNK_ATTRIB[0xa087] = { "container":  True, "name": "wiresize" }
    CHUNK_ATTRIB[0xa08a] = { "container":  True, "name": "xpfallin" }
    CHUNK_ATTRIB[0xa100] = { "container":  True, "name": "shading" }
    CHUNK_ATTRIB[0xa200] = { "container":  True, "name": "texturemap" }
    CHUNK_ATTRIB[0xa220] = { "container":  True, "name": "reflectionmap" }
    CHUNK_ATTRIB[0xa300] = { "container": False, "name": "mapname" }
    CHUNK_ATTRIB[0xa351] = { "container":  True, "name": "maptiling" }
    CHUNK_ATTRIB[0xa353] = { "container":  True, "name": "maptexblur" }
    CHUNK_ATTRIB[0xafff] = { "container":  True, "name": "material" }
    CHUNK_ATTRIB[0xb000] = { "container":  True, "name": "keyf3ds" }
    CHUNK_ATTRIB[0xb002] = { "container":  True, "name": "objectnodetag" }
    CHUNK_ATTRIB[0xb008] = { "container": False, "name": "kfseg" }
    CHUNK_ATTRIB[0xb009] = { "container": False, "name": "kftime" }
    CHUNK_ATTRIB[0xb00a] = { "container": False, "name": "kfhdr" }
    CHUNK_ATTRIB[0xb010] = { "container": False, "name": "nodeheader" }
    CHUNK_ATTRIB[0xb011] = { "container": False, "name": "instancename" }
    CHUNK_ATTRIB[0xb013] = { "container": False, "name": "pivot" }
    CHUNK_ATTRIB[0xb014] = { "container": False, "name": "boundbox" }
    CHUNK_ATTRIB[0xb020] = { "container": False, "name": "trackpos" }
    CHUNK_ATTRIB[0xb021] = { "container": False, "name": "trackrot" }
    CHUNK_ATTRIB[0xb022] = { "container": False, "name": "trackscl" }
    CHUNK_ATTRIB[0xb030] = { "container": False, "name": "nodeid" }

    def __init__(self, parent=None):
        self.parent = parent
        self.child = []
        self.id = 0
        self.base = 0
        self.limit = 0
        self.data = None
        self.attrib = {}

    def put(self, key, value):
        self.attrib[key] = value
        return self

    def get(self, key):
        if self.attrib.has_key(key):
            return self.attrib[key]
        return None

    def has_key(self, key):
        return self.attrib.has_key(key)

    def isContainer(self, id):
        if TDSChunk.CHUNK_ATTRIB.has_key(id):
            attr = TDSChunk.CHUNK_ATTRIB[id]
            return attr["container"]
        return False

    def getchunknamebyid(self, id):
        if TDSChunk.CHUNK_ATTRIB.has_key(id):
            attr = TDSChunk.CHUNK_ATTRIB[id]
            return attr["name"]
        return "UNKNOWN_%04x" % id

    def addChild(self, child):
        """add a child chunk to this chunk"""
        self.child.append(child)
        child.parent = self
        return self

    def subchunkbase(self, data):
        """skip over variable length data in a chunk"""
        return self.base + 6

    def chunkmaker(self, parentchunk, id):
        """make a chunk, perhaps specialized, by .3ds chunk id"""
        maker = None
        if TDSChunk.CHUNK_ATTRIB.has_key(id) and TDSChunk.CHUNK_ATTRIB[id].has_key("make"):
            maker = TDSChunk.CHUNK_ATTRIB[id]["make"]
        if maker is None:
            maker = TDSChunk
        child = maker(parentchunk)
        child.id = id
        return child

    def subdivide(self, depth, parentchunk, data, verbose=True):
        """subdivide a chunk, provided its marked as a container"""
        if not self.isContainer(self.id):
            return self
        base = self.subchunkbase(data)
        limit = self.limit
        if (limit - base) < 6:
            return self
        while base < limit:
            id, length = struct.unpack("<HI", data[base:base + 6])
            child = self.chunkmaker(self, id)
            child.base = base
            child.limit = child.base + length
            if verbose:
                print "    " * depth, "%6d 0x%04x %6d [%s]" % (base, id, length, self.getchunknamebyid(id))
            self.addChild(child)
            child.subdivide(depth + 1, self, data)
            base = child.limit
        return self

    def isKnownChunkID(self, id=None):
        if id is None: id = self.id
        return TDSChunk.CHUNK_ATTRIB.has_key(id)

    def getchildren(self):
        return self.child

    def eggifyinit(self, rootchunk, egg):
        """initialization pass"""
        for chunk in self.getchildren():
            chunk.eggifyinit(rootchunk, egg)
        return self

    def eggifymaterials(self, rootchunk, egg):
        """traverse and convert materials"""
        for chunk in self.getchildren():
            chunk.eggifymaterials(rootchunk, egg)
        return self

    def eggifygeometry(self, rootchunk, egg):
        """traverse and convert geometry"""
        for chunk in self.getchildren():
            chunk.eggifygeometry(rootchunk, egg)
        return self

# important chunks are specialized
class ChunkRoot(TDSChunk):
    """the root chunk of a .3ds file"""
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)
        self.materialsbyname = {}

    def load(self, fileobj, offset, verbose=True):
        """read in the entire .3ds file (ie, the root chunk)"""
        fileobj.seek(offset)
        header = fileobj.read(6)
        id, length = struct.unpack("<HI", header)
        self.id = id
        self.base = offset
        self.limit = self.base + length
        self.data = header + fileobj.read(length - 6)
        if verbose:
            print "%6d 0x%04x %6d [%s]" % (self.base, id, length, self.getchunknamebyid(id))
        return self

    def addMaterial(self, matchunk):
        """an easy (not the best) place to note a material chunk"""
        name = matchunk.getName()
        # print "ChunkRoot:", name, matchunk
        self.materialsbyname[name] = matchunk
        return self

    def getMaterial(self, name):
        """return a material chunk given a name"""
        if self.materialsbyname.has_key(name):
            return self.materialsbyname[name]
        return None

    def eggifygeometry(self, rootchunk, egg):
        """start making an .egg before recursing"""
        print "ChunkRoot:", "egg:", egg
        eobj = EggGroup(self.get("name"))
        egg.addChild(eobj)
        TDSChunk.eggifygeometry(self, rootchunk, eobj)
        return self


class ChunkNamedObject(TDSChunk):
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)

    def subchunkbase(self, data):
        """return the next potential subchunk offset"""
        # chunk ID 0x4000 ("namedobject") has an asciz up front
        # that must be stepped over.
        base = self.base + 6
        name_start = base
        c = data[base:base+1]
        while ord(c) is not 0:
            base += 1
            c = data[base:base+1]
        name_end = base
        self.put("name", data[name_start:name_end])
        return base + 1

    def eggifygeometry(self, rootchunk, egg):
        self.put("triobjects", [])
        egrp = EggGroup(self.get("name"))
        egg.addChild(egrp)
        TDSChunk.eggifygeometry(self, rootchunk, egrp)
        if False: print "namedobject:", self.get("name")
        return self

class ChunkTriObject(TDSChunk):
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)
        self.matnamebyface = {}
        self.put("faces", [])
        self.put("points", [])
        self.put("uvs", [])

    def setMatNameByFace(self, facenum, matname):
        self.matnamebyface[facenum] = matname
        return self

    def getMatNameByFace(self, facenum):
        if self.matnamebyface.has_key(facenum):
            return self.matnamebyface[facenum]
        return None

    def getMaterialByFace(self, rootchunk, facenum):
        matname = self.getMatNameByFace(facenum)
        if matname is not None:
            return rootchunk.getMaterial(matname)
        return None

    def __eggifypoly(self, egg, eprim, evpool, rootchunk, facenum, vlist, points, uvs, mtl):
        # configure some defaults, then adjust them
        if len(uvs) == 0:
            hasuvs = False
        else:
            hasuvs = True
        eprim2 = None
        if mtl is not None:
            if mtl.isTwoSided():
                eprim2 = EggPolygon()
                egg.addChild(eprim2)
            if mtl.isTextured():
                eprim.setTexture(mtl.getEggTexture())
                eprim.setMaterial(mtl.getEggMaterial())
                if eprim2 is not None:
                    eprim2.setTexture(mtl.getEggTexture())
                    eprim2.setMaterial(mtl.getEggMaterial())
            rgb = mtl.get("diffuse")
            if rgb is not None:
                eprim.setColor(Vec4(rgb[0], rgb[1], rgb[2], 1.0))
                if eprim2 is not None:
                    eprim2.setColor(Vec4(rgb[0], rgb[1], rgb[2], 1.0))
                if False:
                    eprim.setMaterial(mtl.getEggMaterial())
                    if eprim2 is not None:
                        eprim2.setMaterial(mtl.getEggMaterial())
        evobjs = []
        for v in vlist[0:3]:
            xyz = points[v]
            ev = EggVertex()
            ev.setPos(Point3D(xyz[0], xyz[1], xyz[2]))
            if hasuvs:
                uv = uvs[v]
                ev.setUv(Point2D(uv[0], uv[1]))
            evpool.addVertex(ev)
            eprim.addVertex(ev)
            evobjs.insert(0, ev)
        if eprim2 is not None:
            for ev in evobjs:
                eprim2.addVertex(ev)
        return self

    def eggifygeometry(self, rootchunk, egg):
        TDSChunk.eggifygeometry(self, rootchunk, egg)
        self.parent.get("triobjects").append(self)
        # we should now have everything we need to know...
        name = self.parent.get("name")
        points = self.get("points")
        uvs = self.get("uvs")
        faces  = self.get("faces")
        evpool = EggVertexPool(name)
        egg.addChild(evpool)
        facenum = 0
        for face in faces:
            epoly = EggPolygon()
            egg.addChild(epoly)
            mtl = self.getMaterialByFace(rootchunk, facenum)
            self.__eggifypoly(egg, epoly, evpool, rootchunk, facenum, face, points, uvs, mtl)
            facenum += 1
        print "object \"%s\": %d tris, %d vertices, %d uvs" % (name, len(faces), len(points), len(uvs))
        return self


class ChunkPoints(TDSChunk):
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)

    def eggifygeometry(self, rootchunk, egg):
        data = rootchunk.data
        base = self.base + 6
        nverts = struct.unpack("<H", data[base:base+2])[0]
        base += 2;
        verts = []
        for i in xrange(0, nverts):
            verts.append(struct.unpack("<fff", data[base:base+12]))
            base += 12
        self.parent.put("points", verts)
        return self

class ChunkUVs(TDSChunk):
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)

    def eggifygeometry(self, rootchunk, egg):
        data = rootchunk.data
        base = self.base + 6
        nverts = struct.unpack("<H", data[base:base+2])[0]
        base += 2;
        verts = []
        for i in xrange(0, nverts):
            verts.append(struct.unpack("<ff", data[base:base+8]))
            base += 8
        self.parent.put("uvs", verts)
        return self

class ChunkFaces(TDSChunk):
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)
        self.put("faces", [])
        self.put("matgroups", [])
        self.put("smoothgroups", [])

    def subchunkbase(self, data):
        """return the next potential subchunk offset"""
        # chunk ID 0x4120 ("faces") is variable length with an unsigned
        # short at the front of the array.
        base = self.base + 6
        nfaces = struct.unpack("<H", data[base:base+2])[0]
        # 2 for the array length, 4 shorts per element of the array
        base += 2 + (nfaces * 8)
        return base

    def eggifygeometry(self, rootchunk, egg):
        TDSChunk.eggifygeometry(self, rootchunk, egg)
        for mgrp in self.get("matgroups"):
            mname = mgrp.get("name")
            mfaces = mgrp.get("faces")
            for facenum in mfaces:
                self.parent.setMatNameByFace(facenum, mname)
        data = rootchunk.data
        base = self.base + 6
        nfaces = struct.unpack("<H", data[base:base+2])[0]
        base += 2
        faces = []
        for i in xrange(0, nfaces):
            # face: (v1, v2, v3, faceinfobits)
            faces.append(struct.unpack("<HHHH", data[base:base+8]))
            base += 8
        self.put("faces", faces)
        self.parent.put("faces", faces)
        return self

class ChunkMeshMatrix(TDSChunk):
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)

    def eggifygeometry(self, rootchunk, egg):
        data = rootchunk.data
        base = self.base + 6
        nitems = 12
        matrix = []
        for i in xrange(0, 12):
            matrix.append(struct.unpack("<f", data[base:base+4])[0])
            base += 4
        self.parent.put("meshmatrix", matrix)
        return self

class ChunkMeshMatGroup(TDSChunk):
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)

    def eggifygeometry(self, rootchunk, egg):
        data = rootchunk.data
        base = self.base + 6
        name_start = base
        c = data[base:base+1]
        while ord(c) is not 0:
            base += 1
            c = data[base:base+1]
        name = data[name_start:base]
        base = base + 1
        self.put("name", name)
        nfaces = struct.unpack("<H", data[base:base+2])[0]
        base += 2
        faces = []
        for i in xrange(0, nfaces):
            faces.append(struct.unpack("<H", data[base:base+2])[0])
            base += 2
        self.put("faces", faces)
        self.parent.get("matgroups").append(self)
        return self

class ChunkSmoothGroup(TDSChunk):
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)

    def eggifygeometry(self, rootchunk, egg):
        data = rootchunk.data
        base = self.base + 6
        faces = []
        while base < self.limit:
            bits = struct.unpack("<I", data[base:base+4])[0]
            base += 4
            faces.append(bits)
        # self.put("faces", faces)
        self.parent.get("smoothgroups").append(self)
        return self

class ChunkMaterialName(TDSChunk):
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)

    def eggifymaterials(self, rootchunk, egg):
        data = rootchunk.data
        name = data[self.base+6:self.limit-1]
        self.parent.put("name", name)
        return self

class ChunkMaterial(TDSChunk):
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)
        self.eggmaterial = None
        self.eggdiffusetexture = None
        self.put("name", None)
        self.put("twosided", False)

    def eggifymaterials(self, rootchunk, egg):
        TDSChunk.eggifymaterials(self, rootchunk, egg)
        terse = {}
        if self.get("twosided"):
            terse["twosided"] = True
        if self.get("texturemap"):
            terse["texturemap"] = self.get("texturemap")
        print "material:", self.get("name"), terse
        rootchunk.addMaterial(self)
        return self

    def getName(self):
        return self.get("name")

    def getEggMaterial(self):
        if self.eggmaterial:
            return self.eggmaterial
        name = self.get("name")
        if name is not None:
            m = EggMaterial(self.get("name"))
            Kd = self.get("diffuse")
            m.setDiff(Vec4(Kd[0], Kd[1], Kd[2], 1.0))
            Ka = self.get("ambient")
            m.setAmb(Vec4(Ka[0], Ka[1], Ka[2], 1.0))
            Ks = self.get("specular")
            m.setSpec(Vec4(Ks[0], Ks[1], Ks[2], 1.0))
            Ns = self.get("shininess")
            m.setShininess(Ns)
            self.eggmaterial = m
        return self.eggmaterial

    def isTextured(self):
        if self.get("texturemap") is not None:
            return True
        return False

    def isTwoSided(self):
        return self.get("twosided")

    def getEggTexture(self):
        if self.eggdiffusetexture:
            return self.eggdiffusetexture
        if not self.isTextured():
            return None
        # incomplete for now (ignores flags found in the .3ds file)
        m = EggTexture(self.get("name") + "_diffuse", self.get("texturemap"))
        m.setFormat(EggTexture.FRgb)
        m.setMagfilter(EggTexture.FTLinearMipmapLinear)
        m.setMinfilter(EggTexture.FTLinearMipmapLinear)
        m.setWrapU(EggTexture.WMRepeat)
        m.setWrapV(EggTexture.WMRepeat)
        self.eggdiffusetexture = m
        return self.eggdiffusetexture

class ChunkColor24(TDSChunk):
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)

    def eggifymaterials(self, rootchunk, egg):
        # 3 unsigned chars after the header... push up to the parent
        data = rootchunk.data
        base = self.base + 6
        rgb = struct.unpack("BBB", data[base:base+3])
        frgb = [float(rgb[0]) / 255.0, float(rgb[1]) / 255.0, float(rgb[2]) / 255.0]
        self.parent.put("_color", rgb)
        self.parent.put("color", frgb)
        return self

class ChunkPercentage(TDSChunk):
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)

    def eggifymaterials(self, rootchunk, egg):
        # 1 short after the header... no conversion needed here.
        # push value to the parent.
        data = rootchunk.data
        base = self.base + 6
        percentage = struct.unpack("H", data[base:base+2])[0]
        self.parent.put("percentage", percentage)
        return self

class ChunkAmbient(TDSChunk):
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)
        self.put("color", (0, 0, 0))

    def eggifymaterials(self, rootchunk, egg):
        TDSChunk.eggifymaterials(self, rootchunk, egg)
        self.parent.put("ambient", self.get("color"))
        return self

class ChunkDiffuse(TDSChunk):
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)
        self.put("color", (0.5, 0.5, 0.5))

    def eggifymaterials(self, rootchunk, egg):
        TDSChunk.eggifymaterials(self, rootchunk, egg)
        self.parent.put("diffuse", self.get("color"))
        return self

class ChunkSpecular(TDSChunk):
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)
        self.put("color", (0.0, 0.0, 0.0))

    def eggifymaterials(self, rootchunk, egg):
        TDSChunk.eggifymaterials(self, rootchunk, egg)
        self.parent.put("specular", self.get("color"))
        return self

class ChunkShininess(TDSChunk):
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)
        self.put("shininess", 0)

    def eggifymaterials(self, rootchunk, egg):
        TDSChunk.eggifymaterials(self, rootchunk, egg)
        self.parent.put("shininess", self.get("shininess"))
        return self

class ChunkTransparency(TDSChunk):
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)
        self.put("transparency", 0)

    def eggifymaterials(self, rootchunk, egg):
        TDSChunk.eggifymaterials(self, rootchunk, egg)
        self.parent.put("transparency", self.get("transparency"))
        return self

class ChunkMapname(TDSChunk):
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)
        self.put("mapname", None)

    def eggifymaterials(self, rootchunk, egg):
        TDSChunk.eggifymaterials(self, rootchunk, egg)
        data = rootchunk.data
        base = self.base + 6
        name_start = base
        c = data[base:base+1]
        while ord(c) is not 0:
            base += 1
            c = data[base:base+1]
        name_end = base
        mapname = data[name_start:name_end]
        self.put("mapname", mapname)
        self.parent.put("mapname", mapname)
        return self

class ChunkTexturemap(TDSChunk):
    def __init__(self, parent=None):
        TDSChunk.__init__(self, parent)
        self.put("mapname", None)

    def eggifymaterials(self, rootchunk, egg):
        TDSChunk.eggifymaterials(self, rootchunk, egg)
        self.parent.put("texturemap", self.get("mapname"))
        return self

class ChunkTwoSided(TDSChunk):
    def __init__(self, parent=None):
        """if present in the .3ds, this chunk means 2-sided tris"""
        TDSChunk.__init__(self, parent)

    def eggifymaterials(self, rootchunk, egg):
        # given that the in-file size of this chunk is 6, and that
        # is the size of a chunk header, there must be no data bytes
        # in the chunk. it would appear to be that if this chunk is
        # present in the material description, it means two-sided polys.
        # if not present, single-sided polys.
        TDSChunk.eggifymaterials(self, rootchunk, egg)
        self.parent.put("twosided", True)
        return self


# most chunks we care about are instances of specialized classes.
# the route below registers the constructors in the CHUNK_ATTRIB
# table and are used by "TDSChunk.chunkmaker()"
def initChunkMakers():
    chunkmakers = [
        ( 0x4000, ChunkNamedObject ),
        ( 0x4100, ChunkTriObject ),
        ( 0x4110, ChunkPoints ),
        ( 0x4120, ChunkFaces ),
        ( 0x4140, ChunkUVs ),
        ( 0x4d4d, ChunkRoot ),
        ( 0xa000, ChunkMaterialName ),
        ( 0xafff, ChunkMaterial ),
        ( 0x0011, ChunkColor24 ),
        ( 0x0030, ChunkPercentage ),
        ( 0xa010, ChunkAmbient ),
        ( 0xa020, ChunkDiffuse ),
        ( 0xa030, ChunkSpecular ),
        ( 0xa040, ChunkShininess ),
        ( 0xa050, ChunkTransparency ),
        ( 0xa081, ChunkTwoSided ),
        ( 0xa200, ChunkTexturemap ),
        ( 0xa300, ChunkMapname ),
        ( 0x4160, ChunkMeshMatrix ),
        ( 0x4130, ChunkMeshMatGroup ),
        ( 0x4150, ChunkSmoothGroup )
    ]
    for item in chunkmakers:
        id, cls = item
        TDSChunk.CHUNK_ATTRIB[id]["make"] = cls
initChunkMakers()


class TDSFile:
    """a representation of an autodesk .3ds file"""
    def __init__(self, filename=None):
        self.filename = None
        self.rootchunk = None
        if filename is not None:
            self.read(filename)

    def read(self, filename, verbose=False):
        if verbose: print "TDSFile.read:", "filename:", filename
        self.filename = filename
        try:
            file = open(filename)
        except:
            return self
        chunk = ChunkRoot(None)
        chunk.load(file, 0, True)
        file.close()
        if not chunk.isKnownChunkID():
            print "unknown chunk id:", chunk.id
            return self
        chunk.subdivide(1, chunk, chunk.data)
        self.rootchunk = chunk
        return self

    def __eggifymaterials(self, root, egg):
        #print "__eggifymaterials:", "self:", self
        for chunk in root.getchildren():
            chunk.eggifymaterials(root, egg)
        return self

    def __eggifygeometry(self, root, egg):
        #print "__eggifygeometry:", "self:", self
        for chunk in root.getchildren():
            chunk.eggifygeometry(root, egg)
        return self

    def __eggifyinit(self, root, egg):
        #print "__eggifyinit:", "self:", self
        for chunk in root.getchildren():
            chunk.eggifyinit(root, egg)
        return self

    def toEgg(self, verbose=True):
        if verbose: print "converting..."
        # make a new egg
        egg = EggData()
        self.__eggifyinit(self.rootchunk, egg)
        self.__eggifymaterials(self.rootchunk, egg)
        self.__eggifygeometry(self.rootchunk, egg)
        return egg

def pathify(path):
    if os.path.isfile(path):
        return path
    # if it was written on win32, it may have \'s in it, and
    # also a full rather than relative pathname (Hexagon does this... ick)
    orig = path
    path = path.lower()
    path = path.replace("\\", "/")
    h, t = os.path.split(path)
    if os.path.isfile(t):
        return t
    print "warning: can't make sense of this map file name:", orig
    return t
    

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        opts, args = getopt.getopt(argv[1:], "hn:bs", ["help", "normals", "binormals", "show"])
    except getopt.error, msg:
        print msg
        print __doc__
        return 2
    show = False
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            return 0
        elif o in ("-s", "--show"):
            show = True
    for infile in args:
        try:
            if ".3ds" not in infile and ".3DS" not in infile:
                print "WARNING", infile, "does not look like a valid .3ds file"
                continue
            tds = TDSFile(infile)
            egg = tds.toEgg()
            f, e = os.path.splitext(infile)
            outfile = f + ".egg"
            for o, a in opts:
                if o in ("-n", "--normals"):
                    print "recomputing vertex normals..."
                    egg.recomputeVertexNormals(float(a))
                elif o in ("-b", "--binormals"):
                    print "recomputing tangent binormals..."
                    egg.recomputeTangentBinormal(GlobPattern(""))
            print "removing unreferenced vertices..."
            egg.removeUnusedVertices(GlobPattern(""))
            if True:
                print "recomputing polygon normals..."
                egg.recomputePolygonNormals()
            egg.writeEgg(Filename(outfile))
            if show:
                os.system("pview " + outfile)
        except Exception,e:
            print e
    return 0

if __name__ == "__main__":
    sys.exit(main())


