# RT-Project
I'll try making a blackhole, if my work is not a blackhole it means I gave up.

### New Class: Ring(Object)
- vCenter = ring's center (vector)
- vNormal = ring's angle to indicate tilt (vector)
- fRadiusInner = inner radius (float) (0 makes a disk)
- fRadiusOuter = outer radius (float)
### Black Hole
- Only faked though since the engine cast rays in a straight line
- Implemented in the integrator
- bh_center = black hole's center used to set position  
- bh_radius = actually doesn't do anything just used to indicate where to use the math (if some distance away from radius = no calculation)                
- bh_mass = mass of the black hole (determines the strength and actual size of black hole)
