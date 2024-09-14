from manim import *
import numpy as np
import os
import shutil

HIGH_QUALITY = True

BLACK = "#000000"
DARK_GREY = "#3F3F3F"
GREY = "#7F7F7F"
LIGHT_GREY = "#BFBFBF"
WHITE = "#FFFFFF"
RED = "#C3312F"
ORANGE = "#EB7246"
GREEN = "#00A390"
CYAN = "00A6D6"
BLUE = "#0065A1"

DIRECTORY = os.path.realpath(os.path.dirname(__file__))
DST_DIRECTORY = f"{DIRECTORY}/output"

BACKGROUND_COLOR = WHITE

config.background_color = BACKGROUND_COLOR

def render_slides(high_quality=True):
    framerate = 24
    width, height = 480, 270
    if high_quality:
        framerate = 60
        width, height = 1920, 1080

    filename = os.path.realpath(__file__)
    src_directory = f"{DIRECTORY}/media/videos/generate/{height}p{framerate}/partial_movie_files/MainScene"

    if os.path.exists(DST_DIRECTORY):
        shutil.rmtree(DST_DIRECTORY)
    os.mkdir(DST_DIRECTORY)

    command = f"manim {filename} MainScene --resolution {width},{height} --frame_rate {framerate}"

    print(f"\033[0;32m{command}\033[0m")
    os.system(command)

    f = open(f"{src_directory}/partial_movie_file_list.txt")
    video_list_data = [x[11:-1] for x in f.read().strip().split("\n")[1:]]
    f.close()

    for idx, src_filename in enumerate(video_list_data):
        dst_filename = f"{DST_DIRECTORY}/output_{idx:04}.mp4"
        shutil.copyfile(src_filename, dst_filename)

class MainScene(Scene):
    ########################################
    #                                      #
    #            HELPER METHODS            #
    #                                      #
    ########################################

    def all_objects(self):
        return [*filter(lambda x: issubclass(type(x), Mobject), self.mobjects)]

    def pause(self):
        self.wait(0.05)
        self.halt_frames.append(self.renderer.num_plays - 1)

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
        self.page_number_text = Text(str(self.page_number), color=GREY).scale(0.6).to_corner(DOWN + RIGHT)
        self.add_foreground_mobject(self.page_number_text)
        self.add(self.page_number_text)

    def set_title(self, text, **kwargs):
        kwargs["color"] = kwargs.get("color", BLACK)

        self.title = Text(text, **kwargs).scale(0.8).to_corner(UP + LEFT).shift((0.2, -0.3, 0))
        self.add(self.title)

        self.next_bullet_point_pos = self.title.get_corner(DOWN + LEFT) + DOWN * 0.4

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
            return np.array([x - 0.5 * y, y * np.sqrt(3) / 2, 0]) * spacing

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

        self.halt_frames = []
        self.page_number = 0

        self.title = None
        self.page_number_text = None

        self.animate()

        f = open(f"{DST_DIRECTORY}/halt_frames.txt", "w")
        f.write(" ".join(str(j) for j in self.halt_frames))
        f.close()

    ################################
    #                              #
    #            SLIDES            #
    #                              #
    ################################

    def animate_slide_intro_outro(self):
        self.next_slide()

        paper_title_text = Text("Trivial Connections in Discrete Geometry", color="#000000").scale(1.1).move_to(ORIGIN).shift(DOWN * 0.9)
        authors_text = Text("Keenan Crane, Mathieu Desbrun, Peter Schröder", color="#3F3F3F").scale(0.6).next_to(paper_title_text, DOWN)
        presented_by_text = Text("Presented by Tim Huisman", color=GREY).scale(0.6).next_to(authors_text, DOWN).shift(DOWN * 0.4)

        intro_bunny_image = self.load_image("intro_bunny").shift(UP * 1.5)

        self.add(paper_title_text, authors_text, presented_by_text, intro_bunny_image)

        self.pause()

    def animate_slide_problem_description(self):
        self.next_slide()
        self.set_title("Problem")
        self.pause()

        self.add_bullet_point("- Create vector fields on the surface of a 3D shape.", t2w={"vector fields": BOLD, "surface": BOLD, "3D shape": BOLD})
        from_bunny_to_field_image = self.load_image("from_bunny_to_field")
        from_bunny_to_field_image.scale(0.75).to_corner(DOWN + RIGHT)
        self.add(from_bunny_to_field_image)
        self.pause()

        self.add_bullet_point("- Smooth everywhere, except on marked singularity vertices.", t2w={"Smooth": BOLD, "singularity vertices": BOLD})
        self.pause()

    def animate_slide_relevance(self):
        self.next_slide()
        self.set_title("Useful for what?")
        from_bunny_to_field_image = self.load_image("from_bunny_to_field")
        from_bunny_to_field_image.scale(0.6).to_corner(DOWN + LEFT)
        self.add(from_bunny_to_field_image)
        self.pause()

        hair_rendering_image = self.load_image("hair_rendering").scale(0.45)
        hair_rendering_image.to_corner(UP + RIGHT).shift(LEFT * 3.5)
        self.add_bullet_point("- Hair rendering")
        self.add(hair_rendering_image)
        self.pause()

        surface_parameterization_image = self.load_image("surface_parameterization").scale(0.8)
        surface_parameterization_image.to_corner(UP + RIGHT)
        self.add_bullet_point("- Surface parameterization")
        self.add(surface_parameterization_image)
        self.pause()

        art_image = self.load_image("art").scale(1.2)
        art_image.to_corner(DOWN + RIGHT)
        self.add_bullet_point("- Art!")
        self.add(art_image)
        self.pause()

        self.add_bullet_point("- ...").shift(DOWN * 0.1)
        self.pause()

    def animate_slide_example_on_flat_surface(self):
        self.next_slide()
        self.set_title("TODO: Example on flat surface")
        self.pause()

    def animate_slide_problem_with_curved_surface(self):
        self.next_slide()
        self.set_title("TODO: Issue on a curved surface...")
        self.pause()

        curved_surface_problem_left_image = self.load_image("curved_surface_problem_left").scale(1.2)
        curved_surface_problem_left_image.shift(LEFT * 3)
        self.add(curved_surface_problem_left_image)
        self.pause()

        transition_arrow = Arrow(max_tip_length_to_length_ratio=0.12).set_color(BLACK).put_start_and_end_on(LEFT * 0.5, RIGHT * 0.5)
        curved_surface_problem_right_image = self.load_image("curved_surface_problem_right").scale(1.2)
        curved_surface_problem_right_image.shift(RIGHT * 3)

        self.add(transition_arrow)
        self.add(curved_surface_problem_right_image)
        self.pause()

    def animate_slide_goal_is_zero_holonomy(self):
        self.next_slide()
        self.set_title("TODO: Goal is zero defect (on all cycles)")
        self.pause()

    def animate_slide_adjustment_angles(self):
        self.next_slide()
        self.set_title("How to control directions?")

        self.pause()

        icosphere_image = self.load_image("icosphere_two_triangles")
        icosphere_image.scale(1.8).shift(LEFT * 3)

        transition_arrow = Arrow(max_tip_length_to_length_ratio=0.12).set_color(BLACK).put_start_and_end_on(LEFT * 0.5, RIGHT * 0.5)

        v, e, f = self.generate_triangle_mesh([
            [0],
            [0, 1],
            [1],
        ], spacing=2)
        for edge in e.values():
            edge.set_stroke(RED)
        mesh_group = Group(*f.values(), *e.values(), *v.values())
        mesh_group.rotate(-0.5 * np.pi).move_to(3 * RIGHT)

        self.add(icosphere_image)
        self.pause()

        self.add(transition_arrow)
        self.add(mesh_group)
        self.pause()

        self.play(
            FadeOut(self.title, shift=UP),
            FadeOut(icosphere_image, shift=LEFT),
            FadeOut(transition_arrow, shift=LEFT),
            Group(*e.values()).animate.scale(2).move_to(ORIGIN).set_color(LIGHT_GREY),
            Group(*v.values(), *f.values()).animate.scale(2).move_to(ORIGIN),
            run_time=0.6
        )
        self.pause()

        displacement = np.array([0.6, 0.45, 0])
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

        face_i_text = Tex("$i$", color=GREY).scale(0.8).next_to(e[frozenset({(0, 0), (0, 1)})], DOWN).shift(DOWN * 0.3)
        face_j_text = Tex("$j$", color=GREY).scale(0.8).next_to(e[frozenset({(0, 1), (1, 2)})], DOWN).shift(DOWN * 0.3)
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
        adjustment_angle_arc = Arc(0.5, displacement_angle, adjustment_angle_value).set_color(BLUE)
        adjustment_angle_arc.shift(pos_j)
        self.play(
            Create(adjustment_angle_arc),
            Rotate(tangent_vector_i, adjustment_angle_value, about_point=pos_j),
            run_time=0.8
        )
        self.wait(0.3)

        adjustment_angle_indicator = edge_circle_text.copy()
        self.add(adjustment_angle_indicator)
        self.play(
            adjustment_angle_indicator.animate.scale(0.6).move_to(adjustment_angle_arc).shift((0.2, 0.2, 0)),
            run_time=0.8
        )
        self.pause()

        adjustment_angle_text = Text("\"Adjustment Angle\"", color=BLUE).to_edge(UP).shift(DOWN * 0.2)
        self.play(
            FadeIn(adjustment_angle_text, shift=UP * 0.5),
            run_time=0.5
        )
        self.pause()

        tangent_vector_j = tangent_vector_i.copy()
        self.add(tangent_vector_j)
        self.play(
            tangent_vector_j.animate.shift(pos_i - pos_j),
            run_time=0.8
        )
        self.wait(0.2)

        opposite_adjustment_angle_formula_text = Tex("$x_{j \\to i}$", "$ = $", "$-$", "$x_{i \\to j}$", color=BLACK)
        opposite_adjustment_angle_formula_text.set_color_by_tex("x", BLUE)
        opposite_adjustment_angle_formula_text.set_color_by_tex("-", RED)
        opposite_adjustment_angle_formula_text.scale(1.5).to_edge(DOWN).shift(UP * 0.2)
        self.play(
            FadeIn(opposite_adjustment_angle_formula_text, shift=DOWN * 0.5),
            run_time=0.5
        )
        self.pause()

        tangent_vector_j_ghost = tangent_vector_j.copy()
        tangent_vector_j_ghost.set_opacity(0.35)
        self.add(tangent_vector_j_ghost)
        adjustment_angle_arc_negative = Arc(0.5, displacement_angle + adjustment_angle_value, -adjustment_angle_value).set_color(BLUE)
        adjustment_angle_arc_negative.shift(pos_i)
        adjustment_angle_indicator_negative = Tex("$-x_{i \\to j}$").set_color(BLUE).scale(0.8 * 0.6)
        adjustment_angle_indicator_negative.move_to(adjustment_angle_arc_negative).shift((0.2, 0.2, 0))
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
        self.add_bullet_point("- Goal: Zero defect on a cycle", t2w={"Zero defect": BOLD})
        self.pause()

        v, e, f = self.generate_triangle_mesh([
            [0, 1],
            [0, 1, 2],
            [1, 2],
        ], spacing=2)
        mesh_group = Group(*f.values(), *e.values(), *v.values())
        mesh_group.move_to(ORIGIN).shift(3 * RIGHT)

        self.add(mesh_group)
        self.pause()

        path_face_keys = [
            frozenset({(0, 0), (1, 0), (1, 1)}),
            frozenset({(1, 0), (1, 1), (2, 1)}),
            frozenset({(1, 1), (2, 1), (2, 2)}),
            frozenset({(1, 1), (1, 2), (2, 2)}),
            frozenset({(0, 1), (1, 1), (1, 2)}),
            frozenset({(0, 0), (0, 1), (1, 1)}),
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

        tangent_vectors = []
        angle = -np.pi / 2
        angle_delta = -0.04 * np.pi
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

        path_arrows = []
        for i in range(len(path_face_keys)):
            fa, fb = f[path_face_keys[i]], f[path_face_keys[(i + 1) % len(path_face_keys)]]
            arrow = Arrow(max_tip_length_to_length_ratio=0.12).set_color(BLUE).set_opacity(0.4).put_start_and_end_on(fa.get_center(), fb.get_center())
            path_arrows.append(arrow)
            self.play(
                self.create_arrow(arrow),
                run_time=0.25
            )
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
        self.pause()

        animations = []
        for i in range(len(tangent_vectors)):
            vector = tangent_vectors[i]
            start, end = vector.get_start_and_end()
            if i % 6 == 0:
                animations.append(vector.animate.put_start_and_end_on(start, start + (end - start) * 2))
            else:
                animations.append(vector.animate.put_start_and_end_on(start, start + (end - start) * 0.5).set_opacity(0.4))
        self.play(
            *animations,
            run_time=0.8
        )
        self.wait(0.2)

        defect_angle = len(path_face_keys) * angle_delta
        defect_arc = Arc(1.6, -0.5 * np.pi + defect_angle, -defect_angle).set_stroke(RED, width=5)
        defect_arc.shift(f[path_face_keys[0]].get_center())
        defect_arc_text = Tex("$\\delta$", color=RED).move_to(defect_arc).shift((-0.2, -0.4, 0))
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

        self.add_bullet_point("- Idea: cancel out defect", t2w={"cancel out": BOLD})
        self.add_bullet_point("  using adjustment angles").shift(UP * 0.12)
        self.pause()

        x = [
             0.08 * np.pi,
             0.05 * np.pi,
            -0.09 * np.pi,
             0.10 * np.pi,
             0.13 * np.pi,
            -0.03 * np.pi
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

        linear_formula_tex = Tex("$x_1$", "$ + $", "$x_2$", "$ + $", "$x_3$", "$ + $", "$x_4$", "$ + $", "$x_5$", "$ + $", "$x_6$", "$~=~$", "$-\\delta$", color=BLACK)
        linear_formula_tex.set_color_by_tex("x", BLUE)
        linear_formula_tex.set_color_by_tex("\\delta", RED)
        linear_formula_tex.move_to(self.next_bullet_point_pos, LEFT + UP).shift((0.3, -0.8, 0))

        self.play(
            Write(linear_formula_tex),
            run_time=0.8
        )
        self.pause()

    def animate_slide_basis_cycle_with_singularities(self):
        self.next_slide()
        self.set_title("Supporting singularities")

        intro_bunny_image = self.load_image("intro_bunny")
        intro_bunny_image.scale(1.4).shift(3 * RIGHT)

        self.add(intro_bunny_image)
        self.pause()

        self.add_bullet_point("- Why even allow singularities?", t2s={"allow": ITALIC})
        self.pause()

        self.next_slide()
        theorem_text = Text("Hairy Ball Theorem", color=BLACK).scale(1.2).shift(2.5 * UP)
        hairy_ball_image = self.load_image("hairy_ball").scale(2)
        self.add(theorem_text)
        self.add(hairy_ball_image)
        self.pause()

        coconut_text = Text("\"You can't comb the hair on a coconut.\"", color=DARK_GREY, slant=ITALIC).shift(2.5 * DOWN)
        self.add(coconut_text)
        self.pause()

        self.next_slide()
        self.set_title("Supporting singularities")
        self.add_bullet_point("- Define value k for each vertex", t2c={"k": GREEN}, t2s={"k": ITALIC})
        intro_bunny_image.scale(0.5).to_corner(DOWN + LEFT)
        hairy_ball_image.scale(0.75).next_to(intro_bunny_image, RIGHT).align_to(intro_bunny_image, DOWN)
        self.add(intro_bunny_image)
        self.add(hairy_ball_image)
        self.pause()

        middle_vertex = Circle(0.24).set_stroke(opacity=0).set_fill(GREEN, opacity=1)
        middle_vertex.move_to(ORIGIN).shift(3 * RIGHT)
        k_text = Tex("$k$", color=WHITE).scale(0.8).move_to(middle_vertex)
        outline_rectangle = Rectangle(WHITE, 4, 4).set_stroke(LIGHT_GREY, width=3).set_fill(opacity=0)
        outline_rectangle.move_to(middle_vertex)
        k_value_text_1 = Tex("$k =~$", "$0$", color=GREEN).next_to(outline_rectangle, UP)
        k_value_text_2 = Tex("$k =~$", "$1$", color=GREEN).next_to(outline_rectangle, UP)
        k_value_text_3 = Tex("$k =~$", "$-1$", color=GREEN).next_to(outline_rectangle, UP)

        tangent_vectors = []
        interpolation_steps = 24
        angle_delta = 2 * np.pi / interpolation_steps
        for i in range(interpolation_steps):
            pos_angle = -0.25 * np.pi + 2 * np.pi * (i / interpolation_steps)
            pos = middle_vertex.get_center() + 1.2 * np.array([np.cos(pos_angle), np.sin(pos_angle), 0])
            tangent_vector = Arrow(max_tip_length_to_length_ratio=0.12).set_color(RED).put_start_and_end_on(pos, pos + 0.35 * (DOWN + RIGHT))
            tangent_vector.rotate((np.random.random() - 0.5) * 0.2, about_point = tangent_vector.get_start())
            tangent_vectors.append(tangent_vector)

        self.add(outline_rectangle)
        self.add(middle_vertex)
        self.add(k_text)
        self.add(k_value_text_1)
        self.pause()

        self.play(
            AnimationGroup(
                *[self.create_arrow(j) for j in tangent_vectors],
                run_time=1.2,
                lag_ratio=0.02
            ),
        )
        self.add_foreground_mobjects(*tangent_vectors)
        self.pause()

        self.add_foreground_mobjects(middle_vertex, k_text)

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

        # TODO: add equation

        self.remove_foreground_mobjects(middle_vertex, k_text)

    def animate_slide_adding_basis_cycles(self):
        self.next_slide()
        self.set_title("What about bigger cycles?")
        self.add_bullet_point("- Goal: Zero defect on all cycles", t2w={"all": BOLD})
        self.pause()

        v, e, f = self.generate_triangle_mesh([
            [0, 1, 2],
            [0, 1, 2, 3],
            [1, 2, 3],
        ], spacing=2)
        mesh_group = Group(*f.values(), *e.values(), *v.values())
        mesh_group.move_to(DOWN)
        self.add(mesh_group)
        self.pause()

        path_1 = [
            f[frozenset({(0, 0), (1, 0), (1, 1)})],
            f[frozenset({(1, 0), (1, 1), (2, 1)})],
            f[frozenset({(1, 1), (2, 1), (2, 2)})],
            f[frozenset({(1, 1), (1, 2), (2, 2)})],
            f[frozenset({(0, 1), (1, 1), (1, 2)})],
            f[frozenset({(0, 0), (0, 1), (1, 1)})],
        ]
        path_1_arrows = []
        for i in range(len(path_1)):
            pos_i, pos_j = path_1[i - 1].get_center(), path_1[i].get_center()
            pos_i, pos_j = pos_i + 0.05 * (pos_j - pos_i), pos_j + 0.05 * (pos_i - pos_j)
            arrow = Arrow(max_tip_length_to_length_ratio=0.12).set_color(BLUE).put_start_and_end_on(pos_i, pos_j)
            path_1_arrows.append(arrow)

        self.play(
            FadeIn(Group(*path_1_arrows), scale=0.5),
            run_time=0.6
        )
        self.pause()

        path_2 = [
            f[frozenset({(1, 0), (2, 0), (2, 1)})],
            f[frozenset({(2, 0), (2, 1), (3, 1)})],
            f[frozenset({(2, 1), (3, 1), (3, 2)})],
            f[frozenset({(2, 1), (2, 2), (3, 2)})],
            f[frozenset({(1, 1), (2, 1), (2, 2)})],
            f[frozenset({(1, 0), (1, 1), (2, 1)})],
        ]
        path_2_arrows = []
        for i in range(len(path_2)):
            pos_i, pos_j = path_2[i - 1].get_center(), path_2[i].get_center()
            pos_i, pos_j = pos_i + 0.05 * (pos_j - pos_i), pos_j + 0.05 * (pos_i - pos_j)
            arrow = Arrow(max_tip_length_to_length_ratio=0.12).set_color(GREEN).put_start_and_end_on(pos_i, pos_j)
            path_2_arrows.append(arrow)

        left_arrow, right_arrow = path_1_arrows[2], path_2_arrows[5]
        right_arrow.shift(RIGHT * 0.1)
        self.play(
            left_arrow.animate.shift(LEFT * 0.1),
            FadeIn(Group(*path_2_arrows), scale=0.5),
            run_time=0.6
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
        self.pause()

        # TODO: add equations

    ###################################
    #                                 #
    #            STRUCTURE            #
    #                                 #
    ###################################

    def animate(self):
        # self.animate_slide_intro_outro()
        # self.animate_slide_problem_description()
        # self.animate_slide_relevance()

        # self.animate_slide_example_on_flat_surface()
        # self.animate_slide_problem_with_curved_surface()

        # self.animate_slide_goal_is_zero_holonomy()

        # self.animate_slide_adjustment_angles()
        # self.animate_slide_equation_for_basis_cycle()
        # self.animate_slide_basis_cycle_with_singularities()
        # self.animate_slide_recap_basis_cycle()
        self.animate_slide_adding_basis_cycles()
        
        self.animate_slide_intro_outro()

if __name__ == "__main__":
    render_slides(HIGH_QUALITY)

    import run

# TODO: explain what a "trivial connection" is