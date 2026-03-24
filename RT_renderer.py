# renderer class

import RT_utility as rtu
import numpy as np
from PIL import Image as im
import math
import RT_pbar
import multiprocessing

# 1. STANDALONE WORKER FUNCTION
# This must sit outside the class so Python can safely send it to other CPU cores.
def render_row_task(args):
    j, width, spp, max_depth, camera, integrator, scene = args
    row_colors = []
    
    # Calculate all pixels in this specific row
    for i in range(width):
        pixel_color = rtu.Color(0,0,0)
        for _ in range(spp):
            generated_ray = camera.get_ray(i, j)
            pixel_color = pixel_color + integrator.compute_scattering(generated_ray, scene, max_depth)
        
        # Store the coordinate and the final color
        row_colors.append((i, j, pixel_color))
        
    return row_colors


class Renderer():
    def __init__(self, cCamera, iIntegrator, sScene) -> None:
        self.camera = cCamera
        self.integrator = iIntegrator
        self.scene = sScene

    def render(self):
        # gather lights to the light list
        self.scene.find_lights()

        # Detect how many CPU cores you have available
        num_cores = multiprocessing.cpu_count()
        print(f"Starting parallel render using {num_cores} CPU cores...")

        # Prepare the arguments for each row
        tasks = []
        for j in range(self.camera.img_height):
            tasks.append((j, self.camera.img_width, self.camera.samples_per_pixel,
                          self.camera.max_depth, self.camera, self.integrator, self.scene))

        # Initialize the progress bar for rows instead of individual pixels
        renderbar = RT_pbar.start_animated_marker(self.camera.img_height)
        completed_rows = 0

        with multiprocessing.Pool(processes=num_cores) as pool:
            # imap_unordered yields results as soon as any row finishes processing
            for row_results in pool.imap_unordered(render_row_task, tasks):
                
                for i, j, pixel_color in row_results:
                    self.camera.write_to_film(i, j, pixel_color)

                # Update progress bar
                completed_rows += 1
                renderbar.update(completed_rows)

        print("\nRender complete!")

    def render_jittered(self):
        # gather lights to the light list
        self.scene.find_lights()
        renderbar = RT_pbar.start_animated_marker(self.camera.img_height*self.camera.img_width)
        k = 0
        sqrt_spp = int(math.sqrt(self.camera.samples_per_pixel))
                
        for j in range(self.camera.img_height):
            for i in range(self.camera.img_width):

                pixel_color = rtu.Color(0,0,0)
                # shoot multiple rays at random locations inside the pixel
                for s_j in range(sqrt_spp):
                    for s_i in range(sqrt_spp):

                        generated_ray = self.camera.get_jittered_ray(i, j, s_i, s_j)
                        pixel_color = pixel_color + self.integrator.compute_scattering(generated_ray, self.scene, self.camera.max_depth)

                self.camera.write_to_film(i, j, pixel_color)
                renderbar.update(k)
                k = k+1

    def write_img2png(self, strPng_filename):
        png_film = self.camera.film * 255
        data = im.fromarray(png_film.astype(np.uint8))
        data.save(strPng_filename)