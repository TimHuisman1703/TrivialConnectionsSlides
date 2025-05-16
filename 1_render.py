from manim import *
import numpy as np
import os
import shutil
import time

from utils import *

DEBUG = False

BACKGROUND_COLOR = WHITE

config.background_color = BACKGROUND_COLOR
config.max_files_cached = 1000

def render_slides():
    start_time = time.time()

    width, height = (480, 270) if DEBUG else (1920, 1080)

    filename = os.path.realpath(__file__)
    command = f"manim {filename} MainScene --resolution {width},{height} --frame_rate {FRAMERATE} --format=png"

    print(f"\033[0;32m{command}\033[0m")
    os.system(command)

    if os.path.exists(OUTPUT_DIRECTORY):
        shutil.rmtree(OUTPUT_DIRECTORY)
    os.mkdir(OUTPUT_DIRECTORY)

    print("\033[34;1mCopying frames...\033[0m")

    for filename in os.listdir(RENDER_DIRECTORY):
        nr = int(filename[9:-4])
        shutil.copyfile(f"{RENDER_DIRECTORY}/{filename}", f"{OUTPUT_DIRECTORY}/{nr:06}.png")

    duration = int(time.time() - start_time)
    print(f"\033[32;1mFinished in {duration // 60}m {duration % 60:02}s!\033[0m")

class MainScene(Scene):
    ########################################
    #                                      #
    #            HELPER METHODS            #
    #                                      #
    ########################################

    def all_objects(self):
        return [*filter(lambda x: issubclass(type(x), Mobject), self.mobjects)]

    def pause(self):
        self.hold(0.15)

        pause_marker_rectangle = Rectangle(PAUSE_MARKER_COLOR_HEX, 100, 100).set_fill(PAUSE_MARKER_COLOR_HEX, opacity=1)
        pause_marker_rectangle.z_index = 10 ** 10
        self.add_foreground_mobject(pause_marker_rectangle)
        self.add(pause_marker_rectangle)
        self.wait(1)

        self.remove(pause_marker_rectangle)

    def hold(self, run_time):
        ignore_me = Dot().move_to(UP * 100)
        self.add(ignore_me)
        self.play(
            ignore_me.animate.shift(UP * 100),
            run_time=run_time
        )

    def load_image(self, name):
        image = ImageMobject(f"{DIRECTORY}/assets/{name}.png")
        image.set_resampling_algorithm(RESAMPLING_ALGORITHMS["bilinear"])
        return image

    def next_slide(self):
        self.clear()
        self.update_page_number()

    def clear(self):
        self.remove(*self.all_objects())

    def update_page_number(self):
        self.page_number += 1
        self.page_number_text = Text("#" if DEBUG else str(self.page_number), color=GREY).scale(0.6).to_corner(DOWN + RIGHT)
        self.add_foreground_mobject(self.page_number_text)
        self.add(self.page_number_text)

    def set_title(self, text, **kwargs):
        kwargs["color"] = kwargs.get("color", BLACK)

        self.title = Text(text, **kwargs).scale(0.8).to_corner(UP + LEFT).shift((0.2, -0.3, 0))
        self.add(self.title)

        self.next_bullet_point_pos = self.title.get_corner(UP + LEFT) + DOWN * 0.9

    def add_bullet_point(self, text, **kwargs):
        kwargs["color"] = kwargs.get("color", "#1F1F1F")

        spacing = len(text) - len(text.strip())
        text = text.strip()

        last_bullet_point = Text(text, **kwargs).scale(0.6).move_to(self.next_bullet_point_pos, LEFT + UP).shift(0.3 * spacing * RIGHT)
        self.add(last_bullet_point)

        self.next_bullet_point_pos += DOWN * 0.6

        return last_bullet_point

    def generate_triangle_mesh(self, grid, spacing=1):
        def pos(x, y):
            return np.array([x - 0.5 * y, -y * np.sqrt(3) / 2, 0]) * spacing

        vertex_map = {}
        for iy in range(len(grid)):
            for ix in grid[iy]:
                vertex = Circle(0.08).set_stroke(opacity=0).set_fill(BLACK, opacity=1)
                vertex.shift(pos(ix, iy))
                vertex_map[(ix, iy)] = vertex

        edge_map = {}
        for ix, iy in vertex_map:
            for jx, jy in [(ix + 1, iy), (ix, iy + 1), (ix + 1, iy + 1)]:
                if (jx, jy) in vertex_map:
                    edge = Line(pos(ix, iy), pos(jx, jy), color=LIGHT_GREY)
                    edge_map[frozenset({(ix, iy), (jx, jy)})] = edge

        face_map = {}
        for ix, iy in vertex_map:
            jx, jy = ix + 1, iy
            if (jx, jy) in vertex_map:
                for kx, ky in [(ix, iy - 1), (jx, jy + 1)]:
                    if (kx, ky) in vertex_map:
                        face_pos = (pos(ix, iy) + pos(jx, jy) + pos(kx, ky)) / 3
                        face = Circle(0.08).shift(face_pos).set_stroke(opacity=0).set_fill(opacity=0)
                        face_map[frozenset({(ix, iy), (jx, jy), (kx, ky)})] = face

        return vertex_map, edge_map, face_map

    def create_arrow(self, arrow):
        start, end = arrow.get_start_and_end()
        opacity = arrow.get_stroke_opacity()
        arrow.set_stroke(opacity=0).set_fill(opacity=0).put_start_and_end_on(start, start + 0.00001 * (end - start))
        return arrow.animate.set_stroke(opacity=opacity).set_fill(opacity=opacity).put_start_and_end_on(start, end)

    def construct(self):
        np.random.seed(4136121025)

        self.page_number = 0

        self.title = None
        self.page_number_text = None

        self.animate()

    ################################
    #                              #
    #            SLIDES            #
    #                              #
    ################################

    def animate_slide_intro_outro(self):
        self.next_slide()

        paper_title_text = Text("Trivial Connections in Discrete Geometry", color=BLACK).scale(1.1).move_to(ORIGIN).shift(DOWN * 0.9)
        authors_text = Text("Keenan Crane, Mathieu Desbrun, Peter Schröder", color=DARK_GREY).scale(0.6).next_to(paper_title_text, DOWN)
        presented_by_text = Text("Presented by Tim Huisman", color=GREY).scale(0.6).next_to(authors_text, DOWN).shift(DOWN * 0.4)

        intro_bunny_image = self.load_image("intro_bunny").shift(UP * 1.5)

        self.add(paper_title_text, authors_text, presented_by_text, intro_bunny_image)

        self.pause()

    def animate_slide_problem_description(self):
        self.next_slide()
        self.set_title("Aim")
        self.pause()

        self.add_bullet_point("- Create vector fields on the surface of a 3D shape.", t2w={"vector fields": BOLD, "surface": BOLD, "3D shape": BOLD})
        from_bunny_to_field_image = self.load_image("from_bunny_to_field")
        from_bunny_to_field_image.scale(0.75).to_corner(DOWN + RIGHT)
        self.add(from_bunny_to_field_image)
        self.pause()

        self.add_bullet_point("- Smooth everywhere, except on predefined singularity vertices.", t2w={"Smooth": BOLD, "singularity vertices": BOLD})
        self.pause()

    def animate_slide_relevance(self):
        self.next_slide()
        self.set_title("Applications")
        from_bunny_to_field_image = self.load_image("from_bunny_to_field")
        from_bunny_to_field_image.scale(0.6).to_corner(DOWN + LEFT)
        self.add(from_bunny_to_field_image)
        self.pause()

        hair_rendering_image = self.load_image("fur_rendering").scale(0.95)
        hair_rendering_image.to_corner(UP + RIGHT).shift(LEFT * 3.5)
        self.add_bullet_point("- Fur rendering;")
        self.add(hair_rendering_image)
        self.pause()

        surface_parameterization_image = self.load_image("surface_parameterization").scale(0.75)
        surface_parameterization_image.to_corner(UP + RIGHT)
        self.add_bullet_point("- Surface parameterization;")
        self.add(surface_parameterization_image)
        self.pause()

        art_image = self.load_image("art").scale(1.2)
        art_image.to_corner(DOWN + RIGHT)
        self.add_bullet_point("- Art!")
        self.add(art_image)
        self.pause()

        self.add_bullet_point("- ...").shift(DOWN * 0.1)
        self.pause()

    def animate_slide_definitions(self):
        self.next_slide()

        background_text = Text("BACKGROUND", color=BLACK, weight=BOLD).scale(2)
        self.add(background_text)
        self.pause()

        self.next_slide()
        self.set_title("Definitions")
        self.pause()

        pos_dir_length = [
            ([0.45, -0.2, 0], [0.8, -0.2, 0], 0.7),
            ([1.3, -1.0, 0], [0.5, -0.6, 0], 0.7),
            ([0.8, -1.9, 0], [0.8, -0.2, 0], 0.7),
            ([-0.4, -1.7, 0], [0.8, 0.2, 0], 0.7),
            ([-0.6, -0.5, 0], [0.8, 0.3, 0], 0.7),
            ([-1.3, -0.6, 0], [0.25, 0.4, 0], 0.7),
            ([-1.0, -2.5, 0], [0.6, 0.4, 0], 0.7),
            ([-0.2, -3.1, 0], [0.3, 0.4, 0], 0.5),
            ([0.7, -2.9, 0], [0.6, 0.4, 0], 0.7),
        ]
        tangent_vectors = []
        for p, d, l in pos_dir_length:
            vector_pos = np.array(p)
            vector_dir = np.array(d)
            vector_dir *= l / np.linalg.norm(vector_dir)
            tangent_vector = Arrow(max_tip_length_to_length_ratio=0.12).set_color(RED).put_start_and_end_on(vector_pos, vector_pos + vector_dir)
            tangent_vectors.append(tangent_vector)

        icosahedron_image = self.load_image("icosahedron")
        icosahedron_image.shift(1.5 * DOWN)
        self.add(icosahedron_image)
        self.add_bullet_point("- Discrete surface (mesh of triangles).", t2c={"triangles": ICO_BLUE})
        self.pause()

        self.add(tangent_vectors[0])
        self.add_bullet_point("- One tangent vector per triangle.", t2c={"tangent vector": RED, "triangle": ICO_BLUE})
        self.pause()

        self.add_bullet_point("- All tangent vectors form a vector field.", t2c={"tangent vectors": RED}, t2s={"vector field": ITALIC})
        self.add(*tangent_vectors[1:])
        self.pause()

    def animate_slide_levi_civita_connection(self):
        self.next_slide()
        self.set_title("A first attempt")
        self.pause()

        self.add_bullet_point("- Levi-Civita connections.")
        self.pause()

        icosahedron_image = self.load_image("icosahedron")
        icosahedron_image.shift((-3, -1.5, 0))
        pos_left_1 = np.array([-2.55, -0.2, 0])
        dir_left_1 = np.array([0.8, -0.2, 0])
        dir_left_1 *= 0.7 / np.linalg.norm(dir_left_1)
        tangent_vector_left_1 = Arrow(max_tip_length_to_length_ratio=0.12).set_color(RED).put_start_and_end_on(pos_left_1, pos_left_1 + dir_left_1)

        self.add_bullet_point("  - Start with tangent vector on some triangle.", t2c={"tangent vector": RED}, t2w={"Start": BOLD})
        self.add(icosahedron_image)
        self.add(tangent_vector_left_1)
        self.add_foreground_mobject(tangent_vector_left_1)
        self.pause()

        icosahedron_two_triangles_image = self.load_image("icosahedron_two_triangles")
        icosahedron_two_triangles_image.move_to(icosahedron_image)
        transition_arrow = Arrow(max_tip_length_to_length_ratio=0.12).set_color(BLACK).put_start_and_end_on((-0.5, -1.5, 0), (0.5, -1.5, 0))
        v, e, f = self.generate_triangle_mesh([
            [0],
            [0, 1],
            [1],
        ], spacing=2.5)
        for edge in e.values():
            edge.set_stroke(ORANGE)
        mesh_group = Group(*f.values(), *e.values(), *v.values())
        mesh_group.rotate(0.5 * np.pi).move_to((3, -1.5, 0))

        self.remove(icosahedron_image)
        self.add(icosahedron_two_triangles_image)
        self.add_bullet_point("  - Propogate vector to neighbors.", t2c={"vector": RED, "neighbors": ORANGE}, t2w={"Propogate": BOLD})
        self.pause()

        pos_right_1 = f[frozenset({(0, 0), (0, 1), (1, 1)})].get_center()
        pos_right_2 = f[frozenset({(0, 1), (1, 1), (1, 2)})].get_center()
        dir_right = np.array([np.sqrt(3), 1, 0])
        dir_right *= 0.7 / np.linalg.norm(dir_right)
        tangent_vector_right_1 = Arrow(max_tip_length_to_length_ratio=0.12).set_color(RED).put_start_and_end_on(pos_right_1, pos_right_1 + dir_right)

        self.add(transition_arrow)
        self.add(mesh_group)
        self.add(tangent_vector_right_1)
        self.pause()

        tangent_vector_right_2 = tangent_vector_right_1.copy()
        self.play(
            tangent_vector_right_2.animate.shift(pos_right_2 - pos_right_1),
            run_time=0.8
        )
        self.pause()

        pos_left_2 = np.array([-1.7, -1, 0])
        dir_left_2 = np.array([0.5, -0.6, 0])
        dir_left_2 *= 0.7 / np.linalg.norm(dir_left_2)
        tangent_vector_left_2 = Arrow(max_tip_length_to_length_ratio=0.12).set_color(RED).put_start_and_end_on(pos_left_2, pos_left_2 + dir_left_2)
        tangent_vector_left_2.generate_target()
        tangent_vector_left_2.put_start_and_end_on(*tangent_vector_left_1.get_start_and_end())
        self.play(
            MoveToTarget(tangent_vector_left_2),
            run_time=0.8
        )
        self.pause()

    def animate_slide_problem_with_curved_surface(self):
        self.next_slide()
        self.set_title("A slight problem...")

        pos_left_1 = np.array([-3.05, 0.25, 0])
        dir_left_1 = np.array([-1.1, 0.7, 0])
        dir_left_1 *= 1.2 / np.linalg.norm(dir_left_1)
        curved_surface_problem_left_image = self.load_image("curved_surface_problem_left").scale(1.5)
        curved_surface_problem_left_image.shift((-3, -1, 0))
        tangent_vector_left_1 = Arrow(max_tip_length_to_length_ratio=0.12).set_color(RED)
        tangent_vector_left_1.put_start_and_end_on(pos_left_1, pos_left_1 + dir_left_1)
        self.add(curved_surface_problem_left_image)
        self.add(tangent_vector_left_1)
        self.pause()

        transition_arrow = Arrow(max_tip_length_to_length_ratio=0.12).set_color(BLACK).put_start_and_end_on((-0.5, -1, 0), (0.5, -1, 0))
        curved_surface_problem_right_image = self.load_image("curved_surface_problem_right").scale(1.5)
        curved_surface_problem_right_image.shift((3, -1, 0))

        tangent_vector_right_start_pos = curved_surface_problem_right_image.get_center() + UP * 1.25
        tangent_vector_right_pos = Dot(tangent_vector_right_start_pos).set_opacity(0)
        tangent_vector_right_dir = Dot(UP * 1.25).set_opacity(0)
        tangent_vector_right = always_redraw(
            lambda: Arrow(max_tip_length_to_length_ratio=0.12).set_color(RED)
                .put_start_and_end_on(tangent_vector_right_pos.get_center(), tangent_vector_right_pos.get_center() + tangent_vector_right_dir.get_center())
        )
        self.add(transition_arrow)
        self.add(curved_surface_problem_right_image)
        self.add(tangent_vector_right)
        self.pause()

        middle_point = curved_surface_problem_right_image.get_center() + DOWN * 0.2
        tangent_vector_right_ghost_1 = tangent_vector_right.copy()
        self.add(tangent_vector_right_ghost_1)
        self.play(
            Rotate(tangent_vector_right_pos, 0.855 * np.pi, about_point=middle_point),
            run_time=1.2
        )
        self.pause()

        tangent_vector_right_ghost_1.set_opacity(0.4)
        tangent_vector_right_ghost_2 = tangent_vector_right.copy()
        self.add(tangent_vector_right_ghost_2)
        tangent_vector_right_pos.move_to(tangent_vector_right_start_pos)
        self.play(
            Rotate(tangent_vector_right_pos, -0.855 * np.pi, about_point=middle_point),
            run_time=1.2
        )
        self.pause()

        pos_left_2_3 = np.array([-1.62, -1.45, 0])
        dir_left_2 = np.array([-1.1, 0.6, 0])
        dir_left_2 *= 1.2 / np.linalg.norm(dir_left_2)
        dir_left_3 = np.array([-0.02, 0.8, 0])
        dir_left_3 *= 1.2 / np.linalg.norm(dir_left_3)
        tangent_vector_left_2 = Arrow(max_tip_length_to_length_ratio=0.12).set_color(RED)
        tangent_vector_left_2.put_start_and_end_on(pos_left_2_3, pos_left_2_3 + dir_left_2)
        tangent_vector_left_3 = Arrow(max_tip_length_to_length_ratio=0.12).set_color(RED)
        tangent_vector_left_3.put_start_and_end_on(pos_left_2_3, pos_left_2_3 + dir_left_3)
        self.play(
            tangent_vector_left_1.animate.set_opacity(0.4),
            self.create_arrow(tangent_vector_left_2),
            self.create_arrow(tangent_vector_left_3),
            run_time=0.6
        )
        self.pause()

        self.add_bullet_point("- Path-dependent...", t2c={"defect": RED, "δ": RED}, t2s={"path dependence": ITALIC})
        self.hold(0.2)

        tangent_vector_right_fade_out = tangent_vector_right.copy()
        self.remove(tangent_vector_right)
        self.play(
            FadeOut(curved_surface_problem_left_image),
            FadeOut(transition_arrow),
            FadeOut(curved_surface_problem_right_image),
            FadeOut(tangent_vector_left_1),
            FadeOut(tangent_vector_left_2),
            FadeOut(tangent_vector_left_3),
            FadeOut(tangent_vector_right_fade_out),
            FadeOut(tangent_vector_right_ghost_1),
            FadeOut(tangent_vector_right_ghost_2),
            run_time=0.6
        )

        defect_angle = 0.3 * np.pi
        pos_a = np.array([-2.5, -1.5, 0])
        pos_b = np.array([2.5, -1.5, 0])
        point_a = Triangle(color=BLACK)
        point_a.shift(DOWN * 0.25).rotate(-np.pi / 2).scale(0.25).shift(pos_a)
        point_b = Triangle(color=BLACK)
        point_b.shift(DOWN * 0.25).rotate(np.pi / 2).scale(0.25).shift(pos_b)
        path_arrow_1 = CurvedArrow(pos_b + np.array([-0.1, 0.1, 0]), pos_a + np.array([0.1, 0.1, 0])).set_color(LIGHT_GREY).scale((-1, 1, 1))
        path_arrow_2 = CurvedArrow(pos_a + np.array([0.1, -0.1, 0]), pos_b + np.array([-0.1, -0.1, 0])).set_color(LIGHT_GREY)
        self.play(
            GrowFromCenter(point_a),
            GrowFromCenter(point_b),
            Create(path_arrow_1),
            Create(path_arrow_2),
            run_time=0.4
        )
        self.hold(0.2)

        tangent_vector_pos_1 = Dot(pos_a).set_opacity(0)
        tangent_vector_dir_1 = Dot(UP * 1.5).set_opacity(0)
        tangent_vector_1 = always_redraw(
            lambda: Arrow(max_tip_length_to_length_ratio=0.12).set_color(RED)
                .put_start_and_end_on(tangent_vector_pos_1.get_center(), tangent_vector_pos_1.get_center() + tangent_vector_dir_1.get_center())
        )
        tangent_vector_pos_2 = Dot(pos_a).set_opacity(0)
        tangent_vector_dir_2 = Dot(UP * 1.5).set_opacity(0)
        tangent_vector_2 = always_redraw(
            lambda: Arrow(max_tip_length_to_length_ratio=0.12).set_color(RED)
                .put_start_and_end_on(tangent_vector_pos_2.get_center(), tangent_vector_pos_2.get_center() + tangent_vector_dir_2.get_center())
        )
        self.play(
            self.create_arrow(tangent_vector_1),
            self.create_arrow(tangent_vector_2),
            run_time=0.6
        )
        self.pause()

        defect_arc_right = Arc(1.6, 0.5 * np.pi + defect_angle / 2, -defect_angle).set_color(RED)
        defect_arc_right.shift(pos_b)
        defect_arc_text_right = Tex("$\\delta$", color=RED)
        defect_arc_text_right.scale(0.8).move_to(defect_arc_right).shift((0, 0.4, 0))
        self.play(
            Rotate(tangent_vector_pos_1, np.pi / 2, about_point=(0, 1, 0)),
            Rotate(tangent_vector_pos_2, -np.pi / 2, about_point=(0, -4, 0)),
            Rotate(tangent_vector_dir_1, defect_angle / 2, about_point=ORIGIN),
            Rotate(tangent_vector_dir_2, -defect_angle / 2, about_point=ORIGIN),
            run_time=0.8
        )
        self.hold(0.2)
        self.play(
            Create(defect_arc_right),
            FadeIn(defect_arc_text_right),
            run_time=0.6
        )
        self.pause()

        tangent_vector_1_static = tangent_vector_1.copy()
        tangent_vector_2_static = tangent_vector_2.copy()
        self.add(tangent_vector_1_static)
        self.add(tangent_vector_2_static)
        self.remove(tangent_vector_1)
        self.remove(tangent_vector_2)
        self.play(
            tangent_vector_1_static.animate.set_opacity(0.4),
            tangent_vector_2_static.animate.set_opacity(0.4),
            defect_arc_right.animate.set_stroke(opacity=0.4),
            defect_arc_text_right.animate.set_opacity(0.4),
            path_arrow_2.animate.scale((-1, 1, 1)),
            run_time=0.8
        )
        self.pause()

        tangent_vector_pos_3 = Dot(pos_a).set_opacity(0)
        tangent_vector_dir_3 = Dot(UP * 1.5).set_opacity(0)
        tangent_vector_3 = always_redraw(
            lambda: Arrow(max_tip_length_to_length_ratio=0.12).set_color(RED)
                .put_start_and_end_on(tangent_vector_pos_3.get_center(), tangent_vector_pos_3.get_center() + tangent_vector_dir_3.get_center())
        )
        tangent_vector_3_ghost = tangent_vector_3.copy().set_opacity(0.4)
        self.play(
            self.create_arrow(tangent_vector_3),
            run_time=0.4
        )
        self.hold(0.4)

        self.add(tangent_vector_3_ghost)
        self.play(
            Rotate(tangent_vector_pos_3, -np.pi / 2, about_point=(0, -4, 0)),
            Rotate(tangent_vector_dir_3, -defect_angle / 2, about_point=ORIGIN),
            run_time=0.6
        )
        self.play(
            Rotate(tangent_vector_pos_3, -np.pi / 2, about_point=(0, 1, 0)),
            Rotate(tangent_vector_dir_3, -defect_angle / 2, about_point=ORIGIN),
            run_time=0.6
        )
        self.pause()

        defect_arc_left = Arc(1.6, 0.5 * np.pi, -defect_angle).set_color(RED)
        defect_arc_left.shift(pos_a)
        defect_arc_text_left = Tex("$\\delta$", color=RED)
        defect_arc_text_left.scale(0.8).move_to(defect_arc_left).shift((0.2, 0.4, 0))
        self.play(
            tangent_vector_1_static.animate.set_opacity(1),
            tangent_vector_2_static.animate.set_opacity(1),
            tangent_vector_3_ghost.animate.set_opacity(1),
            defect_arc_right.animate.set_stroke(opacity=1),
            defect_arc_text_right.animate.set_opacity(1),
            Create(defect_arc_left),
            FadeIn(defect_arc_text_left),
            run_time=0.6
        )
        self.pause()

        self.add_bullet_point("- Goal: No defect (δ) on any cycle.", t2c={"δ": RED}, t2w={"No defect": BOLD, "any cycle": BOLD})
        self.pause()

    def animate_slide_paper_contribution(self):
        self.next_slide()
        self.set_title("Contribution")

        intro_bunny_image = self.load_image("intro_bunny")
        intro_bunny_image.shift(3.6 * RIGHT + DOWN)
        self.add(intro_bunny_image)
        self.add_bullet_point("- Algorithm for enforcing zero-defect cycles (\"trivial connections\").", t2w={"trivial connections": BOLD})
        self.pause()

        self.add_bullet_point("  - Efficient;")
        self.pause()

        self.add_bullet_point("  - Allows full control over singularities;")
        self.pause()

        self.add_bullet_point("  - Elegant.")
        self.pause()

    def animate_slide_adjustment_angles(self):
        self.next_slide()
        how_text = Text("HOW?", color=BLACK, weight=BOLD).scale(2)
        self.add(how_text)
        self.pause()

        self.next_slide()
        self.set_title("How to control?")
        self.pause()

        icosahedron_image = self.load_image("icosahedron_two_triangles")
        icosahedron_image.shift(LEFT * 3)
        transition_arrow = Arrow(max_tip_length_to_length_ratio=0.12).set_color(BLACK).put_start_and_end_on(LEFT * 0.5, RIGHT * 0.5)
        v, e, f = self.generate_triangle_mesh([
            [0],
            [0, 1],
            [1],
        ], spacing=2)
        for edge in e.values():
            edge.set_stroke(ORANGE)
        mesh_group = Group(*f.values(), *e.values(), *v.values())
        mesh_group.rotate(0.5 * np.pi).move_to(3 * RIGHT)

        self.add(icosahedron_image)
        self.add(transition_arrow)
        self.add(mesh_group)
        self.pause()

        self.play(
            FadeOut(self.title, shift=UP),
            FadeOut(icosahedron_image, shift=LEFT * 5),
            FadeOut(transition_arrow, shift=LEFT * 5),
            Group(*e.values()).animate.scale(2).move_to(ORIGIN).set_color(LIGHT_GREY),
            Group(*v.values(), *f.values()).animate.scale(2).move_to(ORIGIN),
            run_time=1.2
        )
        self.hold(0.2)

        displacement = np.array([1.0, 0.75, 0])
        pos_i = f[frozenset({(0, 0), (0, 1), (1, 1)})].get_center()
        pos_j = f[frozenset({(1, 2), (0, 1), (1, 1)})].get_center()
        tangent_vector_i = Arrow(max_tip_length_to_length_ratio=0.12).set_color(RED).put_start_and_end_on(pos_i, pos_i + displacement)
        self.play(
            self.create_arrow(tangent_vector_i),
            run_time=0.6
        )
        self.pause()

        middle_edge = e[frozenset({(0, 1), (1, 1)})]
        self.play(
            middle_edge.animate.set_color(BLUE),
            run_time=0.8
        )
        self.pause()

        face_i_text = Tex("$i$", color=GREY).scale(0.8).next_to(e[frozenset({(0, 0), (0, 1)})], UP).shift(DOWN)
        face_j_text = Tex("$j$", color=GREY).scale(0.8).next_to(e[frozenset({(0, 1), (1, 2)})], UP).shift(DOWN)
        edge_circle = Circle(0.5).set_stroke(BLUE, opacity=1).set_fill(WHITE, opacity=1)
        edge_circle_text = Tex("$x_{i \\to j}$").set_color(BLUE).scale(0.8)
        edge_circle_group = Group(edge_circle, edge_circle_text)
        edge_circle_group.move_to(middle_edge)
        self.play(
            FadeIn(face_i_text),
            FadeIn(face_j_text),
            GrowFromCenter(edge_circle_group, scale=0.5),
            run_time=0.8
        )
        self.pause()

        self.add_foreground_mobject(tangent_vector_i)
        self.play(
            tangent_vector_i.animate.shift(pos_j - pos_i),
            run_time=1.2
        )
        self.pause()

        tangent_vector_i_ghost = tangent_vector_i.copy()
        tangent_vector_i_ghost.set_opacity(0.35)
        self.add(tangent_vector_i_ghost)

        displacement_angle = np.arctan(displacement[1] / displacement[0])
        adjustment_angle_value = 0.35 * np.pi
        adjustment_angle_arc = Arc(1.35, displacement_angle, adjustment_angle_value).set_color(BLUE)
        adjustment_angle_arc.shift(pos_j)
        self.play(
            Create(adjustment_angle_arc),
            Rotate(tangent_vector_i, adjustment_angle_value, about_point=pos_j),
            run_time=0.8
        )
        self.hold(0.3)

        adjustment_angle_indicator = edge_circle_text.copy().set_background_stroke(color=WHITE, width=5)
        self.add(adjustment_angle_indicator)
        self.play(
            adjustment_angle_indicator.animate.scale(0.6).move_to(adjustment_angle_arc).shift((0.25, 0.3, 0)),
            run_time=0.8
        )
        self.pause()

        adjustment_angle_text = Text("\"Adjustment Angle\"", color=BLUE).to_edge(UP).shift(DOWN * 0.2)
        self.add(adjustment_angle_text)
        self.pause()

        opposite_adjustment_angle_formula_text = Tex("$x_{j \\to i}$", "$~= -$", "$x_{i \\to j}$", color=BLACK)
        opposite_adjustment_angle_formula_text.set_color_by_tex("x", BLUE)
        opposite_adjustment_angle_formula_text.scale(1.5).to_edge(DOWN).shift(UP * 0.2)
        self.add(opposite_adjustment_angle_formula_text)
        self.pause()

        tangent_vector_j = tangent_vector_i.copy()
        self.add(tangent_vector_j)
        self.play(
            tangent_vector_j.animate.shift(pos_i - pos_j),
            run_time=0.8
        )
        self.hold(0.2)

        tangent_vector_j_ghost = tangent_vector_j.copy().set_background_stroke(color=WHITE, width=5)
        tangent_vector_j_ghost.set_opacity(0.35)
        self.add(tangent_vector_j_ghost)
        adjustment_angle_arc_negative = Arc(1.35, displacement_angle + adjustment_angle_value, -adjustment_angle_value).set_color(BLUE)
        adjustment_angle_arc_negative.shift(pos_i)
        adjustment_angle_indicator_negative = Tex("$-x_{i \\to j}$").set_color(BLUE).scale(0.8 * 0.6)
        adjustment_angle_indicator_negative.move_to(adjustment_angle_arc_negative).shift((0.25, 0.3, 0))
        self.play(
            Create(adjustment_angle_arc_negative),
            Rotate(tangent_vector_j, -adjustment_angle_value, about_point=pos_i),
            FadeIn(adjustment_angle_indicator_negative),
            run_time=0.8
        )
        self.pause()

    def animate_slide_equation_for_basis_cycle(self):
        self.next_slide()
        self.set_title("Our first equation")
        self.add_bullet_point("- Goal: No defect on one cycle.", t2w={"one": BOLD})
        self.pause()

        v, e, f = self.generate_triangle_mesh([
            [0, 1],
            [0, 1, 2],
            [1, 2],
        ], spacing=2)
        mesh_group = Group(*f.values(), *e.values(), *v.values())
        mesh_group.move_to(3 * RIGHT)

        path_face_keys = [
            frozenset({(1, 1), (1, 2), (2, 2)}),
            frozenset({(1, 1), (2, 1), (2, 2)}),
            frozenset({(1, 0), (1, 1), (2, 1)}),
            frozenset({(0, 0), (1, 0), (1, 1)}),
            frozenset({(0, 0), (0, 1), (1, 1)}),
            frozenset({(0, 1), (1, 1), (1, 2)}),
        ]

        edge_circles = []
        edge_circle_texts = []
        for i in range(len(path_face_keys)):
            key_i, key_j = path_face_keys[i], path_face_keys[(i + 1) % len(path_face_keys)]
            edge_key = frozenset(key_i & key_j)
            edge = e[edge_key]

            edge_circle = Circle(0.1).set_stroke(BLUE, opacity=1, width=3).set_fill(WHITE, opacity=1)
            edge_circle_text = Tex(f"$x_{i + 1}$").set_color(BLUE).scale(0.6)
            edge_circle_group = Group(edge_circle, edge_circle_text)
            edge_circle_group.move_to(edge)

            edge_circles.append(edge_circle)
            edge_circle_texts.append(edge_circle_text)

        self.add(mesh_group)
        self.hold(0.4)

        path_arrows = []
        for i in range(len(path_face_keys)):
            fa, fb = f[path_face_keys[i]], f[path_face_keys[(i + 1) % len(path_face_keys)]]
            arrow = Arrow(max_tip_length_to_length_ratio=0.12).set_color(BLUE).set_opacity(0.4).put_start_and_end_on(fa.get_center(), fb.get_center())
            path_arrows.append(arrow)
            self.play(
                self.create_arrow(arrow),
                run_time=0.2
            )
        self.pause()

        tangent_vectors = []
        angle = -np.pi / 2
        angle_delta = 0.04 * np.pi
        for i in range(len(path_face_keys) + 1):
            i = i % len(path_face_keys)
            pos = f[path_face_keys[i]].get_center()

            displacement = 0.75 * np.array([np.cos(angle), np.sin(angle), 0])
            tangent_vector = Arrow(max_tip_length_to_length_ratio=0.12).set_color(RED).put_start_and_end_on(pos, pos + displacement)
            tangent_vectors.append(tangent_vector)

            angle += angle_delta

        self.play(
            self.create_arrow(tangent_vectors[0]),
            run_time=0.6
        )
        self.add_foreground_mobject(tangent_vectors[0])
        self.pause()

        for i in range(1, len(tangent_vectors)):
            pos_i = f[path_face_keys[i - 1]].get_center()
            pos_j = f[path_face_keys[i % len(path_face_keys)]].get_center()
            tangent_vectors[i].generate_target()
            tangent_vectors[i].shift(pos_i - pos_j).rotate(-angle_delta, about_point=pos_i)
            self.play(
                MoveToTarget(tangent_vectors[i]),
                run_time=0.2
            )
            self.add_foreground_mobject(tangent_vectors[i])
        self.hold(0.3)

        animations = []
        for i in range(len(tangent_vectors)):
            vector = tangent_vectors[i]
            start, end = vector.get_start_and_end()
            if i == 0:
                animations.append(vector.animate.put_start_and_end_on(start, start + (end - start) * 2).set_opacity(0.4))
            elif i == 6:
                animations.append(vector.animate.put_start_and_end_on(start, start + (end - start) * 2))
            else:
                animations.append(vector.animate.put_start_and_end_on(start, start + (end - start) * 0.5).set_opacity(0.4))
        self.play(
            *animations,
            run_time=0.8
        )
        self.hold(0.2)

        defect_angle = len(path_face_keys) * angle_delta
        defect_arc = Arc(1.6, -0.5 * np.pi, defect_angle).set_stroke(RED, width=5)
        defect_arc.shift(f[path_face_keys[0]].get_center())
        defect_arc_text = Tex("$\\delta$", color=RED).move_to(defect_arc).shift((0.15, -0.4, 0))
        self.play(
            Create(defect_arc),
            FadeIn(defect_arc_text),
            run_time=0.8
        )
        self.pause()

        self.play(
            *[FadeIn(j, scale=3) for j in edge_circles],
            run_time=0.6
        )
        self.pause()

        self.add_bullet_point("- Idea: cancel out defect", t2c={"defect": RED}, t2w={"cancel out": BOLD})
        self.add_bullet_point("  using adjustment angles.", t2c={"adjustment angles": BLUE}).shift(UP * 0.12)
        self.pause()

        linear_formula_tex = Tex("$x_1$", "$ + $", "$x_2$", "$ + $", "$x_3$", "$ + $", "$x_4$", "$ + $", "$x_5$", "$ + $", "$x_6$", "$~=~$", "$-\\delta$", color=BLACK)
        linear_formula_tex.set_color_by_tex("x", BLUE)
        linear_formula_tex.set_color_by_tex("\\delta", RED)
        linear_formula_tex.move_to(self.next_bullet_point_pos, LEFT + UP).shift((0.3, -0.8, 0))
        self.play(
            Write(linear_formula_tex),
            run_time=0.8
        )
        self.pause()

        x = [
            -0.08 * np.pi,
            -0.05 * np.pi,
             0.09 * np.pi,
            -0.10 * np.pi,
            -0.13 * np.pi,
             0.03 * np.pi
        ]
        for i in range(len(x)):
            rotation_animations = []
            for j in range(i + 1, len(tangent_vectors)):
                pos = f[path_face_keys[j % len(path_face_keys)]].get_center()
                rotation_animations.append(Rotate(tangent_vectors[j], x[i], about_point=pos))
            self.play(
                *rotation_animations,
                GrowFromCenter(edge_circle_texts[i]),
                ScaleInPlace(edge_circles[i], 2),
                run_time=0.6
            )
        self.pause()

    def animate_slide_basis_cycle_with_singularities(self):
        self.next_slide()
        self.set_title("Supporting singularities")

        intro_bunny_image = self.load_image("intro_bunny")
        intro_bunny_image.scale(1.4).shift(3 * RIGHT)

        self.add(intro_bunny_image)
        self.pause()

        self.add_bullet_point("- Why not remove singularities?", t2s={"remove": ITALIC})
        self.pause()

        self.add_bullet_point("  - We can't!")
        self.pause()

        self.next_slide()
        hairy_ball_theorem_text = Text("Hairy Ball Theorem", color=BLACK).scale(1.5).shift(2.5 * UP)
        hairy_ball_image = self.load_image("hairy_ball").scale(2)
        coconut_text = Text("\"You can't comb the hair on a coconut.\"", color=DARK_GREY, slant=ITALIC).shift(2.5 * DOWN)
        self.add(hairy_ball_theorem_text)
        self.add(hairy_ball_image)
        self.add(coconut_text)
        self.pause()

        self.next_slide()
        self.set_title("Supporting singularities")

        intro_bunny_image.scale(0.5).to_corner(DOWN + LEFT)
        hairy_ball_image.scale(0.75).next_to(intro_bunny_image, RIGHT).align_to(intro_bunny_image, DOWN)
        self.add(intro_bunny_image)
        self.add(hairy_ball_image)
        self.pause()

        middle_vertex = Circle(0.24).set_stroke(opacity=0).set_fill(GREEN, opacity=1)
        middle_vertex.move_to(3 * RIGHT)
        k_text = Tex("$k_v$", color=WHITE).scale(0.8).move_to(middle_vertex)
        outline_rectangle = Rectangle(WHITE, 4, 4).set_stroke(LIGHT_GREY, width=3).set_fill(opacity=0)
        outline_rectangle.move_to(middle_vertex)
        k_value_text_1 = Tex("$k_v =~$", "$0$", color=GREEN).next_to(outline_rectangle, UP)
        k_value_text_2 = Tex("$k_v =~$", "$1$", color=GREEN).next_to(outline_rectangle, UP)
        k_value_text_3 = Tex("$k_v =~$", "$-1$", color=GREEN).next_to(outline_rectangle, UP)
        k_value_text_4 = Tex("$k_v =~$", "$3$", color=GREEN).next_to(outline_rectangle, UP)

        tangent_vectors = []
        interpolation_steps = 48
        angle_delta = 2 * np.pi / interpolation_steps
        for i in range(interpolation_steps):
            pos_angle = -0.25 * np.pi + 2 * np.pi * (i / interpolation_steps)
            pos = middle_vertex.get_center() + 1.2 * np.array([np.cos(pos_angle), np.sin(pos_angle), 0])
            tangent_vector = Arrow(max_tip_length_to_length_ratio=0.06).set_color(RED).put_start_and_end_on(pos, pos + 0.35 * (DOWN + RIGHT))
            tangent_vector.rotate((np.random.random() - 0.5) * 0.2, about_point = tangent_vector.get_start())
            tangent_vectors.append(tangent_vector)

        self.add_bullet_point("- User defines singular index", t2c={"singular index": GREEN}, t2s={"singular index": ITALIC})
        self.add_bullet_point("  for each vertex.").shift(UP * 0.12)
        self.add(outline_rectangle)
        self.add(middle_vertex)
        self.add(k_text)
        self.pause()

        self.add(k_value_text_1)
        self.pause()

        self.play(
            AnimationGroup(
                *[self.create_arrow(j) for j in tangent_vectors],
                run_time=1.2,
                lag_ratio=0.1
            ),
        )
        self.add_foreground_mobjects(*tangent_vectors)
        self.add_foreground_mobjects(middle_vertex, k_text)
        self.pause()

        singularity_plus_one_image = self.load_image("singularity_plus_one")
        singularity_plus_one_image.scale(2).move_to(middle_vertex)
        self.play(
            *[Rotate(tangent_vectors[j], angle_delta * j, about_point=tangent_vectors[j].get_start()) for j in range(len(tangent_vectors))],
            Transform(k_value_text_1, k_value_text_2, replace_mobject_with_target_in_scene=True),
            run_time=1.6
        )
        self.pause()

        self.play(
            FadeIn(singularity_plus_one_image, scale=0.2),
            *[j.animate.set_opacity(0.4) for j in tangent_vectors],
            run_time=0.6
        )
        self.pause()

        singularity_minus_one_image = self.load_image("singularity_minus_one")
        singularity_minus_one_image.scale(2).move_to(middle_vertex)
        self.play(
            FadeOut(singularity_plus_one_image),
            *[j.animate.set_opacity(1) for j in tangent_vectors],
            run_time=0.4
        )
        self.play(
            *[Rotate(tangent_vectors[j], -2 * angle_delta * j, about_point=tangent_vectors[j].get_start()) for j in range(len(tangent_vectors))],
            Transform(k_value_text_2, k_value_text_3, replace_mobject_with_target_in_scene=True),
            run_time=1.6
        )
        self.play(
            FadeIn(singularity_minus_one_image, scale=0.2),
            *[j.animate.set_opacity(0.4) for j in tangent_vectors],
            run_time=0.6
        )
        self.pause()

        self.play(
            FadeOut(singularity_minus_one_image),
            *[j.animate.set_opacity(1) for j in tangent_vectors],
            run_time=0.4
        )
        self.play(
            *[Rotate(tangent_vectors[j], 4 * angle_delta * j, about_point=tangent_vectors[j].get_start()) for j in range(len(tangent_vectors))],
            Transform(k_value_text_3, k_value_text_4, replace_mobject_with_target_in_scene=True),
            run_time=1.6
        )
        self.pause()

        linear_formula_tex = Tex("$\\sum\\,$", "$x$", "$~=~$", "$-\\delta$", "$~+~2\\pi \\cdot k$", color=BLACK)
        linear_formula_tex.set_color_by_tex("x", BLUE)
        linear_formula_tex.set_color_by_tex("\\delta", RED)
        linear_formula_tex.set_color_by_tex("k", GREEN)
        linear_formula_tex.move_to(self.next_bullet_point_pos, LEFT + UP).shift((0.3, -0.4, 0))
        self.add(linear_formula_tex[:-1])
        self.pause()

        self.play(
            Write(linear_formula_tex[-1]),
            run_time=0.8
        )
        self.pause()

        self.remove_foreground_mobjects(middle_vertex, k_text)

    def animate_slide_adding_basis_cycles(self):
        self.next_slide()
        self.set_title("What about bigger cycles?")
        self.add_bullet_point("- Goal: No defect on any cycle.", t2w={"any": BOLD})
        self.pause()

        v, e, f = self.generate_triangle_mesh([
            [0, 1, 2],
            [0, 1, 2, 3],
            [1, 2, 3],
        ], spacing=2)
        mesh_group = Group(*f.values(), *e.values(), *v.values())
        mesh_group.move_to(DOWN * 0.5)
        self.add(mesh_group)
        self.hold(0.5)

        path_1 = [
            f[frozenset({(0, 0), (0, 1), (1, 1)})],
            f[frozenset({(0, 1), (1, 1), (1, 2)})],
            f[frozenset({(1, 1), (1, 2), (2, 2)})],
            f[frozenset({(1, 1), (2, 1), (2, 2)})],
            f[frozenset({(1, 0), (1, 1), (2, 1)})],
            f[frozenset({(0, 0), (1, 0), (1, 1)})],
        ]
        path_1_arrows = []
        for i in range(len(path_1)):
            pos_i, pos_j = path_1[i - 1].get_center(), path_1[i].get_center()
            pos_i, pos_j = pos_i + 0.05 * (pos_j - pos_i), pos_j + 0.05 * (pos_i - pos_j)
            arrow = Arrow(max_tip_length_to_length_ratio=0.12).set_color(BLUE).put_start_and_end_on(pos_i, pos_j)
            path_1_arrows.append(arrow)

        path_2 = [
            f[frozenset({(1, 0), (1, 1), (2, 1)})],
            f[frozenset({(1, 1), (2, 1), (2, 2)})],
            f[frozenset({(2, 1), (2, 2), (3, 2)})],
            f[frozenset({(2, 1), (3, 1), (3, 2)})],
            f[frozenset({(2, 0), (2, 1), (3, 1)})],
            f[frozenset({(1, 0), (2, 0), (2, 1)})],
        ]
        path_2_arrows = []
        for i in range(len(path_2)):
            pos_i, pos_j = path_2[i - 1].get_center(), path_2[i].get_center()
            pos_i, pos_j = pos_i + 0.05 * (pos_j - pos_i), pos_j + 0.05 * (pos_i - pos_j)
            arrow = Arrow(max_tip_length_to_length_ratio=0.12).set_color(GREEN).put_start_and_end_on(pos_i, pos_j)
            path_2_arrows.append(arrow)

        left_arrow, right_arrow = path_1_arrows[4], path_2_arrows[1]
        right_arrow.shift(RIGHT * 0.1)
        left_arrow.shift(LEFT * 0.1)
        self.play(
            FadeIn(Group(*path_1_arrows), scale=0.5),
            FadeIn(Group(*path_2_arrows), scale=0.5),
            run_time=0.6
        )
        self.pause()

        linear_formula_tex_1 = Tex("$\\sum_{x \\in C_1} x = -\\delta_1$", color=BLUE)
        linear_formula_tex_1.shift((-3, -3, 0))
        linear_formula_tex_2 = Tex("$\\sum_{x \\in C_2} x = -\\delta_2$", color=GREEN)
        linear_formula_tex_2.shift((3, -3, 0))
        self.add(linear_formula_tex_1)
        self.add(linear_formula_tex_2)
        self.pause()

        tangent_vector_pos = Dot(f[frozenset({(1, 0), (1, 1), (2, 1)})].get_center()).set_opacity(0)
        tangent_vector_dir = Dot(UP * 1.6).set_opacity(0)
        tangent_vector = always_redraw(
            lambda: Arrow(max_tip_length_to_length_ratio=0.12).set_color(RED)
                .put_start_and_end_on(tangent_vector_pos.get_center(), tangent_vector_pos.get_center() + tangent_vector_dir.get_center())
        )
        self.play(
            self.create_arrow(tangent_vector),
            run_time=0.6
        )
        self.pause()

        tangent_vector_ghost_1 = tangent_vector.copy().set_opacity(0.4)
        self.add(tangent_vector_ghost_1)
        self.play(
            Rotate(tangent_vector_pos, 2 * np.pi, about_point=v[(1, 1)].get_center()),
            run_time=1.2
        )
        self.pause()

        tangent_vector_ghost_2 = tangent_vector.copy().set_opacity(0.4)
        self.add(tangent_vector_ghost_2)
        self.play(
            Rotate(tangent_vector_pos, 2 * np.pi, about_point=v[(2, 1)].get_center()),
            run_time=1.2
        )
        self.pause()

        partial_defect_angle = 0.15 * np.pi
        self.play(
            Rotate(tangent_vector_pos, (5 / 3) * np.pi, about_point=v[(1, 1)].get_center()),
            Rotate(tangent_vector_dir, partial_defect_angle, about_point=ORIGIN),
            run_time=1.2
        )
        self.pause()

        self.play(
            tangent_vector_pos.animate.shift(UP * 2 / np.sqrt(3)),
            Rotate(tangent_vector_dir, -partial_defect_angle, about_point=ORIGIN),
            run_time=0.4
        )
        self.hold(0.5)
        self.play(
            tangent_vector_pos.animate.shift(DOWN * 2 / np.sqrt(3)),
            Rotate(tangent_vector_dir, partial_defect_angle, about_point=ORIGIN),
            run_time=0.4
        )
        self.pause()

        plus_text = Tex("$+$", color=ORANGE).set_background_stroke(color=WHITE, opacity=1, width=3).next_to(left_arrow, LEFT).shift((0.25, 0.3, 0))
        minus_text = Tex("$-$", color=ORANGE).set_background_stroke(color=WHITE, opacity=1, width=3).next_to(right_arrow, RIGHT).shift((-0.25, -0.3, 0))
        self.play(
            left_arrow.animate.set_color(ORANGE),
            right_arrow.animate.set_color(ORANGE),
            FadeIn(plus_text, shift=LEFT * 0.2),
            FadeIn(minus_text, shift=RIGHT * 0.2),
            run_time=0.6
        )
        self.pause()

        self.play(
            FadeOut(left_arrow, scale=0.5, shift=DOWN * 0.3),
            FadeOut(right_arrow, scale=0.5, shift=DOWN * 0.3),
            FadeOut(plus_text),
            FadeOut(minus_text),
            run_time=1.2
        )
        self.hold(0.2)
        self.play(
            Rotate(tangent_vector_pos, (5 / 3) * np.pi, about_point=v[(2, 1)].get_center()),
            Rotate(tangent_vector_dir, -partial_defect_angle, about_point=ORIGIN),
            run_time=1.2
        )
        self.pause()

        self.play(
            *[arrow.animate.set_color(ORANGE) for arrow in path_1_arrows if arrow != left_arrow],
            *[arrow.animate.set_color(ORANGE) for arrow in path_2_arrows if arrow != right_arrow],
            run_time=0.4
        )
        self.pause()

        self.play(
            Rotate(tangent_vector_pos, (5 / 3) * np.pi, about_point=v[(1, 1)].get_center()),
            rate_func=rush_into,
            run_time=1.2
        )
        self.play(
            Rotate(tangent_vector_pos, (5 / 3) * np.pi, about_point=v[(2, 1)].get_center()),
            rate_func=rush_from,
            run_time=1.2
        )
        self.pause()

    def animate_slide_cycle_construction_demonstration(self):
        self.next_slide()

        v, e, f = self.generate_triangle_mesh([
            [*range(10)] for _ in range(6)
        ], spacing=2)
        mesh_group = Group(*f.values(), *e.values(), *v.values())
        mesh_group.move_to(ORIGIN)

        singularity_vertices = {
            (1, 1): 1,
            (6, 3): -2,
            (4, 4): -1,
        }
        for key, value in singularity_vertices.items():
            vertex = v[key]
            vertex.scale(3).set_fill_color(GREEN)
            k_text = Tex(f"${value}$", color=WHITE).scale(0.6).move_to(vertex)
            mesh_group.add(k_text)

        self.add(mesh_group)
        self.pause()

        def demonstrate_cycle(vertices, old_outer_arrows={}):
            arrow_keys = []
            for v_key in vertices:
                x, y = v_key
                boundary_vertex_keys = [
                    (x - 1, y - 1),
                    (x + 0, y - 1),
                    (x + 1, y + 0),
                    (x + 1, y + 1),
                    (x + 0, y + 1),
                    (x - 1, y + 0),
                ]
                face_keys = [frozenset([v_key, boundary_vertex_keys[j - 1], boundary_vertex_keys[j]]) for j in range(6)]
                arrow_keys.extend([(v_key, face_keys[j - 1], face_keys[j]) for j in range(6)])

            outer_arrows = {}
            inner_arrows = set()
            for arrow_key in arrow_keys:
                pos_v, pos_fa, pos_fb = v[arrow_key[0]].get_center(), f[arrow_key[1]].get_center(), f[arrow_key[2]].get_center()
                pos_fa = pos_fa + 0.05 * (pos_v - pos_fa)
                pos_fb = pos_fb + 0.05 * (pos_v - pos_fb)
                arrow = Arrow(max_tip_length_to_length_ratio=0.12).set_color(BLUE).put_start_and_end_on(pos_fa, pos_fb)

                key = frozenset(arrow_key[1:])
                if key in outer_arrows:
                    inner_arrows.add(outer_arrows.pop(key))
                    inner_arrows.add(arrow)
                else:
                    outer_arrows[key] = arrow
            outer_arrows = set(outer_arrows.values())

            self.play(
                *[FadeOut(j) for j in old_outer_arrows],
                *[self.create_arrow(j) for j in inner_arrows | outer_arrows],
                run_time=0.4
            )
            self.hold(0.6)

            self.play(
                *[j.animate.set_color(ORANGE) for j in inner_arrows],
                run_time=0.4
            )
            self.hold(0.6)

            self.play(
                *[FadeOut(j) for j in inner_arrows],
                run_time=0.4
            )
            self.hold(0.8)

            return outer_arrows

        outer_arrows = demonstrate_cycle(
            [(4, 3), (4, 2), (5, 2)]
        )
        outer_arrows = demonstrate_cycle(
            [(3, 4), (3, 3), (3, 2), (3, 1), (4, 2), (5, 3), (6, 4), (6, 3), (6, 2), (6, 1)],
            outer_arrows
        )
        outer_arrows = demonstrate_cycle(
            [(j, 1) for j in range(3, 6)] +
            [(j, 2) for j in range(2, 6)] + [(7, 2)] +
            [(j, 3) for j in range(3, 8)] +
            [(j, 4) for j in range(4, 6)],
            outer_arrows
        )
        self.pause()

    def animate_slide_explain_noncontractible_cycles(self):
        self.next_slide()
        self.set_title("A few more cycles")
        self.add_bullet_point("- Did we cover all cycles?", t2s={"all": ITALIC})
        self.pause()

        cycle_types_image_1 = self.load_image("cycle_types_1").scale(0.9)
        cycle_types_image_1.to_corner(UP + RIGHT)
        self.add(cycle_types_image_1)
        self.add_bullet_point("  - No, only contractible cycles!", t2c={"contractible": BLUE})
        self.pause()

        cycle_types_image_2 = self.load_image("cycle_types_2").scale(0.9)
        cycle_types_image_2.to_corner(UP + RIGHT)
        self.remove(cycle_types_image_1)
        self.add(cycle_types_image_2)
        self.add_bullet_point("- Noncontractible cycles not covered yet.", t2c={"Noncontractible": PURPLE}, t2s={"yet": ITALIC})
        self.pause()

        self.add_bullet_point("- How to find noncontractible cycles?", t2c={"noncontractible": PURPLE})
        self.pause()

        tree_cotree_decomposition_image = self.load_image("tree_cotree_decomposition")
        tree_cotree_decomposition_image.scale(0.8).to_corner(DOWN + RIGHT)
        self.add_bullet_point("  - Tree-cotree decomposition!", t2s={"Tree-cotree decomposition": ITALIC})
        self.add_bullet_point("    (Eppstein 2003)", color=GREY).shift(UP * 0.12)
        self.next_bullet_point_pos += UP * 0.12
        self.add(tree_cotree_decomposition_image)
        self.pause()

        self.add_bullet_point("  - Obtains 2g cycles.", t2c={"2g": PURPLE})
        self.pause()

    def animate_slide_matrix_equation(self):
        self.next_slide()

        linear_equations = []
        for iy in range(12):
            linear_equation = []
            random_indices = set()
            while len(random_indices) < 6:
                random_indices.add(np.random.randint(1, 100))
            random_indices = [*random_indices]
            for ix in range(17):
                if ix == 13 or ix == 15:
                    continue

                if ix == 6:
                    tex = Tex("$\\ldots$")
                elif ix == 14:
                    tex = Tex("$=$")
                elif ix == 16:
                    tex = Tex(f"$-\\delta_{{{iy + 1}}}$")
                elif ix % 2:
                    tex = Tex("$+$" if np.random.random() < 0.6 else "$-$")
                else:
                    idx = random_indices.pop()
                    tex = Tex(f"$x_{{e_{{{idx}}}}}$")
                tex.set_color(BLACK)
                tex.scale(0.8).shift((-5.6 + 0.7 * ix, 3.5 - 0.73 * iy, 0))
                self.add(tex)

                linear_equation.append(tex)
            linear_equations.append(linear_equation)
        self.pause()

        for iy in range(2):
            for tex in linear_equations[iy]:
                tex.set_color(PURPLE).scale(1.25)
        self.pause()

        for iy in range(2, len(linear_equations)):
            for tex in linear_equations[iy]:
                tex.set_color(BLUE).scale(1.25)
        self.pause()

        mask_rectangle = Square(100).set_fill(WHITE, opacity=0.7)
        matrix_formula_tex = Tex("$A$", "$\\textbf{x}$", "$~=~$", "$\\textbf{b}$", color=BLACK).set_background_stroke(color=WHITE, opacity=1, width=12).scale(1.6)

        self.add(mask_rectangle)
        self.add(matrix_formula_tex)
        self.pause()

        minimiziation_formula_tex = Tex("$\\textbf{min} \\, ||\\textbf{x}||_2$", color=BLACK).set_background_stroke(color=WHITE, opacity=1, width=12).scale(1.6)
        minimiziation_formula_tex.shift(UP * 0.75)
        self.play(
            matrix_formula_tex.animate.shift(DOWN * 0.75),
            FadeIn(minimiziation_formula_tex, shift=DOWN * 0.75),
            run_time=0.4,
        )
        self.pause()

    def animate_slide_constructing_field(self):
        self.next_slide()
        self.set_title("Almost there...")
        bullet_point_1 = self.add_bullet_point("- We have all adjustment angles!", t2c={"adjustment angles": BLUE})
        self.pause()

        bullet_point_2 = self.add_bullet_point("- Now construct the vector field...", t2c={"vector field": RED})
        self.pause()

        v, e, f = self.generate_triangle_mesh([
            [*range(10)] for _ in range(6)
        ], spacing=2)
        mesh_group = Group(*f.values(), *e.values(), *v.values())
        mesh_group.move_to(ORIGIN)

        self.play(
            FadeIn(mesh_group, scale=1.2),
            FadeOut(bullet_point_1, shift=UP),
            FadeOut(bullet_point_2, shift=UP),
            FadeOut(self.title, shift=UP),
            run_time=0.8
        )
        self.pause()

        edge_circles = []
        for edge in e.values():
            edge_circle = Circle(0.1).set_stroke(BLUE, opacity=1, width=3).set_fill(WHITE, opacity=1)
            edge_circle.move_to(edge)
            edge_circles.append(edge_circle)

        start_face_key = frozenset([(2, 3), (3, 3), (3, 4)])
        end_face_key = frozenset([(6, 1), (6, 2), (7, 2)])

        triangle_animations = []
        new_edges = []
        for face_key in [start_face_key, end_face_key]:
            keys = [*face_key]
            curr_new_edges = []
            for i in range(3):
                edge_key = frozenset(keys[:i] + keys[i+1:])
                new_edge = e[edge_key].copy()
                new_edge = new_edge.set_color(ORANGE)
                curr_new_edges.append(new_edge)

            new_edges.extend(curr_new_edges)
            triangle_animations.append(
                FadeIn(Group(*curr_new_edges), scale=10)
            )

        def get_direction(pos):
            x, y, _ = pos
            dir = np.array([np.exp(0.15 * x), -0.4 * y + 1.5, 0])
            dir *= 0.9 / np.linalg.norm(dir)
            return dir

        def func(t):
            return 0.5 * linear(t) + 0.5 * smooth(t)

        tangent_vectors = {}
        for f_key, face in f.items():
            pos = face.get_center()
            dir = get_direction(pos)

            tangent_vector = Arrow(max_tip_length_to_length_ratio=0.12).set_color(RED).put_start_and_end_on(pos, pos + dir)
            tangent_vectors[f_key] = tangent_vector

        self.add_foreground_mobjects(*v.values())
        tangent_vectors[start_face_key].z_index = 100
        self.play(
            triangle_animations[0],
            self.create_arrow(tangent_vectors[start_face_key]),
            run_time=0.6
        )
        self.pause()

        self.play(
            triangle_animations[1],
            run_time=0.6
        )
        self.pause()

        self.remove_foreground_mobjects(*v.values())

        self.play(
            *[FadeIn(j, scale=3) for j in edge_circles],
            run_time=0.6
        )
        self.pause()

        paths = [
            [1, 2, 3, 2, 3, 2, 1, 2, 3, 2, 3, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 2, 3, 4, 3, 2, 3, 2, 1, 6, 1, 2, 3, 2, 3],
            [0, 0, 0, 3, 2, 3, 2, 1, 2, 3, 2, 3, 2, 1, 0, 0, 0],
        ]
        travelling_vectors = [tangent_vectors[start_face_key].copy().set_opacity(0.6) for _ in paths]
        for t in range(len(paths[0])):
            move_animations = []
            if t == 0:
                move_animations = [j.animate.set_stroke(LIGHT_GREY, opacity=1, width=3) for j in edge_circles]

            for i in range(len(paths)):
                v = paths[i][t]
                if v > 0:
                    angle = (v - 1) * np.pi / 3
                    vector = travelling_vectors[i]
                    pos = vector.get_start()
                    new_pos = pos + (2 / np.sqrt(3)) * np.array([np.sin(angle), np.cos(angle), 0])
                    new_dir = get_direction(new_pos)
                    move_animations.append(
                        vector.animate.put_start_and_end_on(new_pos, new_pos + new_dir)
                    )

            self.play(
                *move_animations,
                run_time=0.2,
                rate_func=func
            )
        self.pause()

        self.play(
            *[FadeOut(j) for j in new_edges],
            *[FadeOut(j) for j in travelling_vectors],
            run_time=0.4
        )
        self.hold(0.4)

        neighbors = {face_key: [] for face_key in f}
        for face_key_i in f:
            for face_key_j in f:
                if len(face_key_i & face_key_j) == 2:
                    neighbors[face_key_i].append(face_key_j)

        q = [start_face_key]
        seen = set(q)
        while True:
            come_from = {}
            for face_key_i in q:
                for face_key_j in neighbors[face_key_i]:
                    if face_key_j not in seen and face_key_j not in come_from:
                        come_from[face_key_j] = face_key_i

            if not come_from:
                break

            animations = []
            for face_key_j, face_key_i in come_from.items():
                vector_i = tangent_vectors[face_key_i]
                vector_j = tangent_vectors[face_key_j]

                vector_j.generate_target()
                vector_j.put_start_and_end_on(*vector_i.get_start_and_end())
                animations.append(
                    MoveToTarget(vector_j)
                )
            self.play(
                *animations,
                run_time=0.2,
                rate_func=func
            )

            seen |= set(come_from.keys())
            q = [*come_from.keys()]
            np.random.shuffle(q)
        self.pause()

        tangent_vectors[start_face_key].z_index = 0
        mask_rectangle = Square(100).set_fill(WHITE, opacity=0.7)
        intro_bunny_transparent_image = self.load_image("intro_bunny_transparent").scale(1.6)
        self.play(
            FadeIn(mask_rectangle),
            FadeIn(intro_bunny_transparent_image, shift=UP),
            run_time=0.8,
            rate_func=rush_from
        )
        self.pause()

    def animate_slide_extensions(self):
        self.next_slide()

        width = 8.0 * 1920 / 1080
        line_1 = Line((-width / 6, -5, 0), (-width / 6, 5, 0)).set_stroke(color=GREY, width=6)
        line_2 = Line((width / 6, 5, 0), (width / 6, -5, 0)).set_stroke(color=GREY, width=6)
        self.add(line_1)
        self.add(line_2)
        self.pause()

        header_text_1 = Text("Edge weights", color=BLACK).shift((-width / 3, 3, 0))
        header_text_2 = Text("Directional\nconstraints", color=BLACK).shift((0, 3, 0))
        header_text_3 = Text("Fractional\nsingular\nindices", color=BLACK, t2s={"Fractional": ITALIC}).shift((width / 3, 3, 0)).align_to(header_text_2, UP)

        self.add(header_text_1)
        edge_weight_visual_image = self.load_image("edge_weight_visual").scale(1.2)
        edge_weight_visual_image.shift((-width / 3, 1.2, 0))
        dkk_definition_tex = Tex("$D_{kk}$", "$~= \\sqrt{2 (\\cot \\phi_i + \\cot \\phi_j)^{-1}}$", color=BLACK).scale(0.65)
        dkk_definition_tex.set_color_by_tex("D", GREEN)
        dkk_definition_tex.shift((-width / 3, -1.2, 0))
        minimiziation_formula_tex = Tex("$\\textbf{min} \\, ||$", "$D$", "$\\textbf{x}||_2$", color=BLACK).scale(0.8)
        minimiziation_formula_tex.set_color_by_tex("D", GREEN)
        minimiziation_formula_tex.shift((-width / 3, -2.1, 0))
        matrix_formula_tex = Tex("$A$", "$\\textbf{x}$", "$~=~$", "$\\textbf{b}$", color=BLACK).scale(0.8)
        matrix_formula_tex.shift((-width / 3, -2.7, 0))
        self.add(edge_weight_visual_image)
        self.add(dkk_definition_tex)
        self.add(matrix_formula_tex)
        self.add(minimiziation_formula_tex)
        self.pause()

        self.add(header_text_2)
        directional_constraints_example_image = self.load_image("directional_constraints_example").scale(0.65)
        directional_constraints_example_image.shift((0, 0.9, 0))
        directional_constraints_zoom_image = self.load_image("directional_constraints_zoom").scale(1.35)
        directional_constraints_zoom_image.shift((1.35, 0.3, 0))
        directional_constraints_zoom_stroke = Rectangle(DARK_GREY, directional_constraints_zoom_image.height, directional_constraints_zoom_image.width)
        directional_constraints_zoom_stroke.move_to(directional_constraints_zoom_image)
        directional_constraints_tree_image = self.load_image("directional_constraints_tree").scale(0.8)
        directional_constraints_tree_image.shift((0, -2.1, 0))
        self.add(directional_constraints_example_image)
        self.add(directional_constraints_zoom_image)
        self.add(directional_constraints_zoom_stroke)
        self.add(directional_constraints_tree_image)
        self.pause()

        self.add(header_text_3)
        intro_bunny_image = self.load_image("intro_bunny").scale(0.8)
        intro_bunny_image.shift((width / 3, -1.6, 0))
        bunny_singularity_1_image = self.load_image("bunny_singularity_1").scale(1.2)
        bunny_singularity_1_image.shift((width / 3 - 1.2, 0.8, 0))
        bunny_singularity_1_stroke = Rectangle(DARK_GREY, bunny_singularity_1_image.height, bunny_singularity_1_image.width)
        bunny_singularity_1_stroke.move_to(bunny_singularity_1_image)
        bunny_singularity_2_image = self.load_image("bunny_singularity_2").scale(1.2)
        bunny_singularity_2_image.shift((width / 3, 0.8, 0))
        bunny_singularity_2_stroke = Rectangle(DARK_GREY, bunny_singularity_2_image.height, bunny_singularity_2_image.width)
        bunny_singularity_2_stroke.move_to(bunny_singularity_2_image)
        bunny_singularity_3_image = self.load_image("bunny_singularity_3").scale(1.2)
        bunny_singularity_3_image.shift((width / 3 + 1.2, 0.8, 0))
        bunny_singularity_3_stroke = Rectangle(DARK_GREY, bunny_singularity_3_image.height, bunny_singularity_3_image.width)
        bunny_singularity_3_stroke.move_to(bunny_singularity_3_image)
        self.add(intro_bunny_image)
        self.add(bunny_singularity_1_image)
        self.add(bunny_singularity_1_stroke)
        self.add(bunny_singularity_2_image)
        self.add(bunny_singularity_2_stroke)
        self.add(bunny_singularity_3_image)
        self.add(bunny_singularity_3_stroke)
        self.pause()

    def animate_slide_conclusion(self):
        self.next_slide()
        self.set_title("Conclusion")
        self.pause()

        effective_examples_image = self.load_image("effective_examples").scale(0.6)
        effective_examples_image.to_corner(UP + RIGHT)
        self.add_bullet_point("- Effective;")
        self.add(effective_examples_image)
        self.pause()

        self.add_bullet_point("- Efficient, O(|E|);", t2c={"O(|E|)": BLUE}, t2s={"O(|E|)": ITALIC})
        self.pause()

        self.add_bullet_point("- Controllable;")
        self.pause()

        robust_examples_image = self.load_image("robust_examples").scale(0.65)
        robust_examples_image.to_corner(DOWN + RIGHT)
        self.add_bullet_point("- Robust;")
        self.add(robust_examples_image)
        self.pause()

        self.add_bullet_point("- Solved!", t2c={"Solved!": GREEN})
        self.pause()

        self.add_bullet_point("")
        self.add_bullet_point("- Best Paper Award (Symposium")
        self.add_bullet_point("  on Geometry Processing 2010).").shift(UP * 0.12)
        self.pause()

    def animate_slide_implementation_plan(self):
        self.next_slide()
        how_text = Text("WHAT NOW?", color=BLACK, weight=BOLD).scale(2)
        self.add(how_text)
        self.pause()

        self.next_slide()
        self.set_title("Implementation Plan")
        self.pause()

        link_text = Tex("$\\texttt{https://www.cs.cmu.edu/\\~{}kmcrane/Projects/TrivialConnections/code.zip}$", color=GREY).scale(0.5)
        link_text.to_corner(DOWN + LEFT)
        comb_image = self.load_image("comb").scale(0.4)
        comb_image.to_corner(UP + RIGHT)
        self.add_bullet_point("- Source code publicly available!")
        self.add(link_text)
        self.add(comb_image)
        self.pause()

        self.add_bullet_point("  - Only shows output...")
        self.pause()

        opengl_image = self.load_image("opengl").scale(0.2)
        opengl_image.next_to(comb_image, DOWN).align_to(comb_image, RIGHT)
        self.add_bullet_point("- Interactive media.", t2w={"Interactive media": BOLD})
        self.add_bullet_point("  - Step-by-step visuals, source code + OpenGL.")
        self.add(opengl_image)
        self.pause()

        manim_image = self.load_image("manim").scale(0.7)
        manim_image.next_to(opengl_image, DOWN).align_to(opengl_image, RIGHT)
        self.add_bullet_point("- Noninteractive media.", t2w={"Noninteractive media": BOLD})
        self.add_bullet_point("  - Demonstrative animations, Manim.", t2s={"Manim": ITALIC})
        self.add(manim_image)
        self.pause()

    ###################################
    #                                 #
    #            STRUCTURE            #
    #                                 #
    ###################################

    def animate(self):
        self.animate_slide_intro_outro()
        self.animate_slide_problem_description()
        self.animate_slide_relevance()

        self.animate_slide_definitions()
        self.animate_slide_levi_civita_connection()
        self.animate_slide_problem_with_curved_surface()

        self.animate_slide_paper_contribution()

        self.animate_slide_adjustment_angles()
        self.animate_slide_equation_for_basis_cycle()
        self.animate_slide_basis_cycle_with_singularities()
        self.animate_slide_adding_basis_cycles()
        self.animate_slide_cycle_construction_demonstration()
        self.animate_slide_explain_noncontractible_cycles()

        self.animate_slide_matrix_equation()
        self.animate_slide_constructing_field()
        self.animate_slide_extensions()

        self.animate_slide_conclusion()
        self.animate_slide_implementation_plan()

        self.animate_slide_intro_outro()

if __name__ == "__main__":
    render_slides()
