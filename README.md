# RT-Project
I'll made a blackhole!

### New Class: Ring(Object)
- Used to make the accretion disk and the plant's ring
    - vCenter = ring's center (vector)
    - vNormal = ring's angle to indicate tilt (vector)
    - fRadiusInner = inner radius (float) (0 makes a disk)
    - fRadiusOuter = outer radius (float)
- Beware: ring's actual size is from fRadiusOuter - fRadiusInner. Therefore it doesn't work when fRadiusInner is bigger than fRadiusOuter
### Black Hole
- Only faked though since the engine cast rays in a straight line
- Implemented in the integrator
    - bh_center = black hole's center used to set position  
    - bh_radius = actually doesn't do anything just used to indicate where to use the math (if some distance away from radius = no calculation)                
    - bh_mass = mass of the black hole (determines the strength and actual size of black hole)
- We also check the foreground first. If the ray hit and object in front of the black hole, we don't apply the effect.
- We find closest_point which is the point in each ray closest to the singularity.
- If foreground check is passed we cast a new ray starting from closest_point in a bent direction according to the black hole's pull.
- The black hole strength is determined by its `bh_mass / (dist_to_center * dist_to_center)` from $$g = \frac{G\times{M}}{r^2}$$ so g (which is gravitational field strength) is proportional to (mass/radius\**2) or $$g ∝ \frac{M}{r^2}$$
