# object class
import RT_utility as rtu
import math

class Object:
    def __init__(self) -> None:
        pass

    def intersect(self, rRay, cInterval):
        pass

class Sphere(Object):
    def __init__(self, vCenter, fRadius, mMat=None) -> None:
        super().__init__()
        self.center = vCenter
        self.radius = fRadius
        self.material = mMat
        # additional parameters for motion blur
        self.moving_center = None       # where to the sphere moves to
        self.is_moving = False          # is it moving ?
        self.moving_dir = None          # moving direction

    def add_material(self, mMat):
        self.material = mMat

    def add_moving(self, vCenter):      # set an ability to move to the sphere
        self.moving_center = vCenter
        self.is_moving = True
        self.moving_dir = self.moving_center - self.center

    def move_sphere(self, fTime):       # move the sphere by time parameter
        return self.center + self.moving_dir*fTime

    def printInfo(self):
        self.center.printout()        
    
    def intersect(self, rRay, cInterval):        

        # check if the sphere is moving then move center of the sphere.
        sphere_center = self.center
        if self.is_moving:
            sphere_center = self.move_sphere(rRay.getTime())

        oc = rRay.getOrigin() - sphere_center
        a = rRay.getDirection().len_squared()
        half_b = rtu.Vec3.dot_product(oc, rRay.getDirection())
        c = oc.len_squared() - self.radius*self.radius
        discriminant = half_b*half_b - a*c 

        if discriminant < 0:
            return None
        sqrt_disc = math.sqrt(discriminant)

        root = (-half_b - sqrt_disc) / a 
        if not cInterval.surrounds(root):
            root = (-half_b + sqrt_disc) / a 
            if not cInterval.surrounds(root):
                return None
            
        hit_t = root
        hit_point = rRay.at(root)
        hit_normal = (hit_point - sphere_center) / self.radius
        hinfo = rtu.Hitinfo(hit_point, hit_normal, hit_t, self.material)
        hinfo.set_face_normal(rRay, hit_normal)

        # set uv coordinates for texture mapping
        fuv = self.get_uv(hit_normal)
        hinfo.set_uv(fuv[0], fuv[1])

        return hinfo

    # return uv coordinates of the sphere at the hit point.
    def get_uv(self, vNormal):
        theta = math.acos(-vNormal.y())
        phi = math.atan2(-vNormal.z(), vNormal.x()) + math.pi

        u = phi / (2*math.pi)
        v = theta / math.pi
        return (u,v)

# Ax + By + Cz = D
class Quad(Object):
    def __init__(self, vQ, vU, vV, mMat=None) -> None:
        super().__init__()
        self.Qpoint = vQ
        self.Uvec = vU
        self.Vvec = vV
        self.material = mMat
        self.uxv = rtu.Vec3.cross_product(self.Uvec, self.Vvec)
        self.normal = rtu.Vec3.unit_vector(self.uxv)
        self.D = rtu.Vec3.dot_product(self.normal, self.Qpoint)
        self.Wvec = self.uxv / rtu.Vec3.dot_product(self.uxv, self.uxv)

    def add_material(self, mMat):
        self.material = mMat

    def intersect(self, rRay, cInterval):
        denom = rtu.Vec3.dot_product(self.normal, rRay.getDirection())
        # if parallel
        if rtu.Interval.near_zero(denom):
            return None

        # if it is hit.
        t = (self.D - rtu.Vec3.dot_product(self.normal, rRay.getOrigin())) / denom
        if not cInterval.contains(t):
            return None
        
        hit_t = t
        hit_point = rRay.at(t)
        hit_normal = self.normal

        # determine if the intersection point lies on the quad's plane.
        planar_hit = hit_point - self.Qpoint
        alpha = rtu.Vec3.dot_product(self.Wvec, rtu.Vec3.cross_product(planar_hit, self.Vvec))
        beta = rtu.Vec3.dot_product(self.Wvec, rtu.Vec3.cross_product(self.Uvec, planar_hit))
        if self.is_interior(alpha, beta) is None:
            return None

        hinfo = rtu.Hitinfo(hit_point, hit_normal, hit_t, self.material)
        hinfo.set_face_normal(rRay, hit_normal)

        # set uv coordinates for texture mapping
        hinfo.set_uv(alpha, beta)

        return hinfo
    
    def is_interior(self, fa, fb):
        delta = 0   
        if (fa<delta) or (1.0<fa) or (fb<delta) or (1.0<fb):
            return None

        return True

class Ring(Object):
    def __init__(self, vCenter, vNormal, fRadiusInner, fRadiusOuter, mMat=None) -> None:
        super().__init__()
        self.center = vCenter
        self.normal = rtu.Vec3.unit_vector(vNormal)
        self.radius_inner = fRadiusInner
        self.radius_outer = fRadiusOuter
        self.radius_inner_sq = fRadiusInner * fRadiusInner
        self.radius_outer_sq = fRadiusOuter * fRadiusOuter
        self.material = mMat
        
        # Create an Orthonormal Basis (ONB) for UV calculation later
        self.uvw = rtu.ONB()
        self.uvw.build_from_w(self.normal)

    def add_material(self, mMat):
        self.material = mMat

    def intersect(self, rRay, cInterval):
        denom = rtu.Vec3.dot_product(self.normal, rRay.getDirection())
        
        # If the ray is perfectly parallel to the ring's plane, it misses
        if rtu.Interval.near_zero(denom):
            return None

        # 1. Calculate the intersection t on the infinite plane
        oc = self.center - rRay.getOrigin()
        t = rtu.Vec3.dot_product(oc, self.normal) / denom

        # Check if t is within the acceptable interval
        if not cInterval.contains(t):
            return None

        # 2. Get the hit point and check if it's within the ring's radii
        hit_point = rRay.at(t)
        center_to_hit = hit_point - self.center
        dist_sq = center_to_hit.len_squared()

        if dist_sq < self.radius_inner_sq or dist_sq > self.radius_outer_sq:
            return None

        # 3. Calculate UV coordinates (Polar mapping)
        u_proj = rtu.Vec3.dot_product(center_to_hit, self.uvw.u())
        v_proj = rtu.Vec3.dot_product(center_to_hit, self.uvw.v())
        
        theta = math.atan2(v_proj, u_proj)
        if theta < 0:
            theta += 2 * math.pi
        
        # u maps the angle around the circle (0 to 1)
        u = theta / (2 * math.pi)
        
        # v maps the radial distance from inner radius to outer radius (0 to 1)
        dist = math.sqrt(dist_sq)
        v = (dist - self.radius_inner) / (self.radius_outer - self.radius_inner)

        hit_normal = self.normal
        hinfo = rtu.Hitinfo(hit_point, hit_normal, t, self.material)
        hinfo.set_face_normal(rRay, hit_normal)
        hinfo.set_uv(u, v)

        return hinfo

class Triangle(Object):
    def __init__(self) -> None:
        super().__init__()

    def intersect(self, rRay, cInterval):
        return super().intersect(rRay, cInterval)
    

    