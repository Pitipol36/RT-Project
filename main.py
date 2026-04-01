import RT_utility as rtu
import RT_camera as rtc
import RT_renderer as rtren
import RT_material as rtm
import RT_scene as rts
import RT_object as rto
import RT_integrator as rti
import RT_light as rtl
import RT_texture as rtt
import multiprocessing

def renderBH():
    main_camera = rtc.Camera()
    main_camera.aspect_ratio = 16.0/9.0
    main_camera.img_width = 480
    main_camera.center = rtu.Vec3(0,0,0)
    main_camera.samples_per_pixel = 20
    main_camera.max_depth = 5
    main_camera.vertical_fov = 60
    main_camera.look_from = rtu.Vec3(0, 0, -1)
    main_camera.look_at = rtu.Vec3(0, 0, 0)
    main_camera.vec_up = rtu.Vec3(0, 1, 0)

    aperture = 0.3
    focus_distance = 4.0
    main_camera.init_camera(aperture, focus_distance)
    # add objects to the scene
    
    mat_phong1 = rtm.Phong(rtu.Color(0.8, 0.3, 0.3), 0.5, 0.5, 0.8)
    mat_phong2 = rtm.Phong(rtu.Color(0.3, 0.8, 0.3), 0.5, 0.5, 8.0)
    mat_phong3 = rtm.Phong(rtu.Color(0.3, 0.3, 0.8), 0.5, 0.5, 30.0)
    dlight = rtl.Diffuse_light(rtu.Color(10.0, 4.0, 1.0))
    starlight = rtl.Diffuse_light(rtu.Color(0.06, 0.06, 0.02))
    
    
    black_hole_disk = rto.Ring(
        vCenter=rtu.Vec3(0, 0, 5),
        vNormal=rtu.Vec3(0, 1, -0.30),
        fRadiusInner=1.0,
        fRadiusOuter=2.5,
        mMat=dlight
    )
    
    eh_mat = rtm.Lambertian(rtu.Color(0.02, 0.015, 0.04))
    black_hole_eh = rto.Sphere(rtu.Vec3(0, 0, 5), 1, eh_mat)

    mat_earth = rtm.TextureColor(rtt.ImageTexture("textures/earthmap.png"))
    
    phong_gold = rtm.Phong(rtu.Color(0.8, 0.6, 0.1), 0.8, 0.8, 30)

    phong_panel = rtm.Phong(rtu.Color(0.05, 0.1, 0.3), 0.8, 0.8, 30)
    
    planet_ring = rto.Ring(
        vCenter=rtu.Vec3( -5, -2, 5),
        vNormal=rtu.Vec3(0.0, 0.4, -0.10),
        fRadiusInner=0.3,
        fRadiusOuter=0.5,
        mMat=starlight
    )
        
    world = rts.Scene()
    world.add_object(black_hole_disk)
    #world.add_object(black_hole_eh)
    world.add_object(rto.Sphere(rtu.Vec3(   2,   -1, 1.5),  0.8, mat_earth))
    world.add_object(rto.Sphere(rtu.Vec3(   5,   3, 6),  0.2, mat_phong1))
    world.add_object(rto.Sphere(rtu.Vec3(   -3,   -3, 6),  0.1, mat_phong2))
    world.add_object(rto.Sphere(rtu.Vec3(   -4,   3.5, 6),  0.2, mat_phong3))
    world.add_object(rto.Sphere(rtu.Vec3(   -5,   -2, 5),  0.2, mat_phong3))
    
    world.add_object(planet_ring)
    
    probe_body = rto.Sphere(vCenter=rtu.Vec3(-2.5, 1, 3), fRadius=0.2, mMat=phong_gold)
    world.add_object(probe_body)

    left_panel = rto.Quad(
        vQ=rtu.Vec3(-2.24124, 0.968144, 3.10966) ,   
        vU=rtu.Vec3(1.03776, 0.596222, -0.08701),
        vV=rtu.Vec3(-0.1716, 0.26246, -0.248331),
        mMat=phong_panel
    )
    world.add_object(left_panel)

    right_panel = rto.Quad(
        vQ=rtu.Vec3(-3.62492, 0.173181, 3.22568),   
        vU=rtu.Vec3(1.03776, 0.596222, -0.08701),
        vV=rtu.Vec3(-0.1716, 0.26246, -0.248331),
        mMat=phong_panel
    )
    world.add_object(right_panel)
    
    intg = rti.Integrator(bSkyBG=False)

    renderer = rtren.Renderer(main_camera, intg, world)
    renderer.render()
    renderer.write_img2png('bhwithoutlambertianball.png')    

if __name__ == "__main__":
    multiprocessing.freeze_support()
    renderBH()


