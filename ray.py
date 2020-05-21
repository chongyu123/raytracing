import pygame
import math

shapes = [
    {
        "location" : [4, -2, 20],
        "radius" : 3,
        "color" : [0,255,100],
        "reflection_level" : .3
    },
    {
        "location" : [-2, 8, 30],
        "radius" : 6,
        "color" : [255,50,50],
        "reflection_level" : .3
    },
    {
        "location" : [-7, 0, 25],
        "radius" : 3,
        "color" : [100,100,255],
        "reflection_level" : .4
    },
    {
        "location" : [6, 5, 35],
        "radius" : 4,
        "color" : [255,255,0],
        "reflection_level" : .5
    },
]

lights = [
    [10, 15, 30],
]

def dot_product(a, b):
    return (a[0]*b[0]+ a[1]*b[1] + a[2]*b[2])

def vector_add(a, b):
    return (a[0]+b[0], a[1]+b[1], a[2]+b[2])

def vector_subtract(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

def vector_scale(scaler, vector):
    return (scaler*vector[0], scaler*vector[1], scaler*vector[2])

def vector_to_unit(vector):
    length =vector_length(vector)
    return (vector[0]/length, vector[1]/length, vector[2]/length)

def vector_length(vector):
    return math.sqrt(dot_product(vector, vector))

def vector_angle(v1, v2):
    return dot_product(v1, v2)/(vector_length(v1) * vector_length(v2))

def overlay_color(original, overlay, trans):
    # trans 1 = replace
    # 0 = no change
    # 0.5 = half/half
    adjusted_overlay = vector_scale(trans, overlay)
    adjusted_original = vector_scale(1-trans, original)
    return vector_add(adjusted_original, adjusted_overlay)


def find_next_object(p_origin, d_ray):
    selected_shape = None
    selected_t = None

    for shape in shapes:
        # circle center at 0,0,80 with radius 10
        location = shape["location"]
        p_center = (location[0], location[1], location[2])
        radius = shape["radius"]

        oc = vector_subtract(p_origin, p_center)
        k1 = dot_product(d_ray, d_ray)
        k2 = 2 * dot_product(oc, d_ray)
        k3 = dot_product(oc, oc) - radius*radius
        discriminant = k2*k2 - 4*k1*k3
        if discriminant >= 0:
            t1 = (-k2 - math.sqrt(discriminant)) / (2*k1)
            t2 = (-k2 + math.sqrt(discriminant)) / (2*k1)

            if t1>0 and t2>0:
                if selected_t == None or t1 < selected_t or t2 < selected_t:
                    selected_t = min(t1, t2)
                    selected_shape = shape

    return (selected_t, selected_shape)


def find_floor(p_origin, d_ray):
    # floor at y=-5
    color = None

    if d_ray[1] + p_origin[1] == 0:
        return (None, color)

    if p_origin[1] + 5 < 0.1 :
        return (None, color)

    t = (-5-p_origin[1])/d_ray[1]

    if t > 0.01:
        p_floor = vector_add(vector_scale(t, d_ray), p_origin)
        tile_size = 3
        x_temp = int(p_floor[0]/tile_size) % 2
        if p_floor[0] < 0:
            x_temp = (int(p_floor[0]/tile_size)+1) % 2
        z_temp = int(p_floor[2]/tile_size)%2
        if (x_temp == 0 and z_temp == 1) or (x_temp == 1 and z_temp == 0):
            color = (200, 200, 200)
        else:
            color = (20,20,20)
    else:
        t = None

    return (t, color)


def light_filter(p_origin, d_normal):
    # returns 0-2
    # 2 should be the brightest - smallest angle
    # 0 darkest - bigest angle
    total_filter = 0

    for light in lights:
        source = tuple(light)
        d_light = vector_subtract(p_origin, source)

        shape = find_next_object(p_origin, vector_to_unit(vector_scale(-1,d_light)))
        if shape[0] != None:
            return None

        angle = vector_angle(d_light, d_normal)
        total_filter = total_filter + angle
    

    return 1-angle


def color_apply_filter(color, filter):
    r = color[0] - filter
    g = color[1] - filter
    b = color[2] - filter
    return (max(r, 0), max(g, 0), max(b, 0))


def get_pixel_color(x,y):
    # translate screen x,y to display to model's unit
    # define ray direction d_ray
    vx = x*(1.0/cw)
    vy = y*(1.0/ch)
    d_ray = (vx, vy, 1.0)
    d_ray = vector_to_unit(d_ray)
    p_origin = (0,0,0)

    #vector = vector_subtract(d_ray, p_origin)
    current_color = (0, 0, 0)
    current_trans = 1

    # loop through number of rays to follow
    for iteration in range(0, ray_depth):

        continue_iterate = False

        # check for spheres
        #-------------------
        intersection = find_next_object(p_origin, d_ray)


        # find the reflection vector from the sphere
        # Reflected vector = D-2(D.N)N
        #--------------------------------------------
        t = intersection[0]

        if t != None:
            sphere_location = tuple(intersection[1]["location"])
            radius = intersection[1]["radius"]
            p_intersection = vector_add(vector_scale(t, d_ray), p_origin)
            d_normal = ((p_intersection[0]-sphere_location[0])/radius, (p_intersection[1]-sphere_location[1])/radius, (p_intersection[2]-sphere_location[2])/radius)
            #d_normal = vector_to_unit(vector_subtract(p_intersection, sphere_location))

            object_color = tuple(intersection[1]["color"])

            # appy lighting to the object
            angle = light_filter(d_ray, d_normal)
            if angle != None:
                filter = (2-angle) * 100
                object_color = color_apply_filter(object_color, filter)
            else:
                object_color = color_apply_filter(object_color, 250)

            # apply the color to the current color
            if iteration == 0:
                current_color = object_color
            else:
                current_color = overlay_color(current_color, object_color, current_trans)

            current_trans = intersection[1]["reflection_level"]


            scaler = dot_product(vector_scale(2, d_ray), d_normal)
            d_ray = vector_subtract(d_ray, vector_scale(scaler, d_normal))
            d_ray = vector_to_unit(d_ray)
            p_origin = p_intersection
            continue_iterate = True
            continue

        # check for floor
        #-----------------
        intersection = find_floor(p_origin, d_ray)
        t = intersection[0]
        if t != None:
            p_intersection = vector_add(vector_scale(t, d_ray), p_origin)
            object_color = tuple(intersection[1])
            d_normal = (0,1,0)

            angle = light_filter(p_intersection, d_normal)
            if angle != None:
                filter = (2-angle) * 200
                object_color = color_apply_filter(object_color, filter)
            else:
                object_color = color_apply_filter(object_color, 150)

            if iteration == 0:
                current_color = object_color
            else:
                current_color = overlay_color(current_color, object_color, current_trans)
            current_trans = .1

            # find reflection ray off the floor
            d_normal = (0,1,0)
            scaler = dot_product(vector_scale(2, d_ray), d_normal)
            d_ray = vector_subtract(d_ray, vector_scale(scaler, d_normal))
            d_ray = vector_to_unit(d_ray)
            p_origin = p_intersection
            #continue_iterate = True
            #continue

        if not continue_iterate:
            return current_color

    return current_color



# initial constants
cw = 800 # display width
ch = 800 # display height
vw = 1 # view width
vh = 1 # view height
ray_depth = 4 # how many depth the ray will trace
camera = (0, 0, 0)
display_z = 0

screen = pygame.display.set_mode((cw, ch))
clock = pygame.time.Clock()
running = True

print("drawing...")
for y in range(-400, 400):
    print(f"{int((y+401)/8)}%")
    for x in range(-400, 400):
        screen.set_at((x+400, 800-(y+400)), get_pixel_color(x,y))

for event in pygame.event.get():
    if event.type == pygame.QUIT:
        running = False

pygame.display.flip()
    #clock.tick(240)

c=input("Complete. Press enter to stop.")


