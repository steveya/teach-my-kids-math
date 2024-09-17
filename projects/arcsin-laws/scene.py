from manim import *
from manim_physics import *
from manim.camera.camera import Camera
import numpy as np
import random


class BasketballNetScene(Scene):
    def construct_basketball(self):
        basketball = Circle(radius=0.4, color=ORANGE, fill_opacity=1)

        # Add typical basketball pattern lines
        # Vertical line
        vertical_line = Line(UP * 0.4, DOWN * 0.4).set_color(BLACK)
        # Horizontal line
        horizontal_line = Line(LEFT * 0.4, RIGHT * 0.4).set_color(BLACK)
        # Curved lines to mimic the basketball's pattern
        curve_point = 2 * np.sqrt(2) * 0.1
        curve1 = ArcBetweenPoints(
            LEFT * curve_point + UP * curve_point,
            RIGHT * curve_point + UP * curve_point,
            radius=1.8,
        ).set_color(BLACK)
        curve2 = ArcBetweenPoints(
            LEFT * curve_point + DOWN * curve_point,
            RIGHT * curve_point + DOWN * curve_point,
            radius=-1.8,
        ).set_color(BLACK)

        # Group the basketball and the lines to make one object
        basketball_group = VGroup(
            basketball, vertical_line, horizontal_line, curve1, curve2
        )
        return basketball_group

    def construct_net(self):
        # Define the net, placed at the left of the scene
        a = [-0.3, -0.5, 0]
        b = [-0.5, 0.5, 0]
        c = [0.5, 0.5, 0]
        d = [0.3, -0.5, 0]
        net_shape = ArcPolygon(a, b, c, d, radius=2)
        net_shape.set_stroke(WHITE, opacity=0.5, width=3)
        # net_shape.set_color(WHITE)

        # Add lines to simulate the netting
        net_lines = VGroup()
        num_lines = 5
        for i in range(num_lines):
            line = Line(
                a + np.array([0, i * 1.0 / num_lines, 0]),
                d + np.array([0, i * 1.0 / num_lines, 0]),
            )
            net_lines.add(line)

        net_lines.set_stroke(WHITE, opacity=0.5, width=2)

        # Grouping the shape and lines
        net = VGroup(net_shape, net_lines)
        # net = VGroup(net_lines)
        net.set_color(WHITE)

        return net

    def construct_basketball_path(self, v0: float, angle: float, t_end: float = 25):
        # Define the path of the basketball
        # Initial velocity components
        v_x0 = v0 * np.cos(angle)
        v_y0 = v0 * np.sin(angle)

        gravity = 0.03

        # Define the trajectory for the basketball (a parabola)
        def trajectory(t):
            return np.array(
                [
                    -3 + v_x0 * t,
                    -1 + v_y0 * t - 0.5 * gravity * t**2,
                    0,  # z = 0, because it's a 2D scene
                ]
            )

        path = ParametricFunction(trajectory, t_range=np.array([0, t_end]), color=WHITE)
        return path

    def build_score_board(self):
        self.alice_score = Text("0", font_size=DEFAULT_FONT_SIZE)
        self.bob_score = Text("0", font_size=DEFAULT_FONT_SIZE)
        self.score_table = (
            MobjectTable(
                [
                    [Text("Alice"), Text("Bob")],
                    [self.alice_score, self.bob_score],
                ]
            )
            .scale(0.5)
            .to_corner(UR)
        )
        self.score_table.to_corner(UR)
        self.add(self.score_table)
        return

    def demonstrate_basketball_path(self):
        self.net = ImageMobject("net.png")
        self.net.scale(0.4)
        # self.net = self.construct_net()
        self.net.move_to(2 * RIGHT + 1.3 * UP + 0.55 * RIGHT)

        # Define the basketball, starting from the middle of the scene
        self.basketball = self.construct_basketball()
        self.basketball.add_updater(
            lambda m, dt: m.rotate(-PI * dt, about_point=self.basketball.get_center())
        )
        self.basketball.move_to(ORIGIN + 3 * LEFT + DOWN)

        self.add(self.net, self.basketball)
        # Add net and basketball to the scene
        # self.add(self.net, self.basketball)
        self.build_score_board()

        alice = ImageMobject("alice.png")
        bob = ImageMobject("bob.png")
        players = [alice, bob]
        for p in players:
            p.scale(0.2)
            p.to_edge(LEFT).shift(3 * LEFT + DOWN)
            self.add(p)

        player_starting_location = alice.get_center()
        player_target_location = self.basketball.get_left() + LEFT * 0.5

        self.add(alice, bob)

        scores = {alice: 0, bob: 0}
        for round in range(2):
            player = round % 2 == 0 and alice or bob
            score = round % 2 == 0 and self.alice_score or self.bob_score
            move_in_animation = ApplyMethod(player.move_to, player_target_location)
            move_out_animation = ApplyMethod(player.move_to, player_starting_location)

            win_path = self.construct_basketball_path(0.5, np.pi / 2.85, 24)
            loss_path = self.construct_basketball_path(0.5, np.pi / 2.5, 28)

            win_loss = np.random.choice(["win", "loss"], p=[0.8, 0.2])
            if win_loss == "win":
                path = win_path
                scores[player] += 1
            else:
                path = loss_path

            new_score = Text(f"{scores[player]}", font_size=DEFAULT_FONT_SIZE)
            new_score.move_to(score)
            if player == alice:
                self.alice_score = new_score
            else:
                self.bob_score = new_score

            self.play(
                move_in_animation,
            )
            self.add(self.net)
            self.play(
                MoveAlongPath(self.basketball, path, run_time=0.6, rate_func=linear),
                ReplacementTransform(score, new_score),
            )
            self.play(
                move_out_animation,
            )

        # self.wait()

    def construct(self):
        self.demonstrate_basketball_path()


class CoinFlipMultipleSimulations(Scene):
    def construct(self):
        axes = Axes(
            x_range=[0, 100, 10],
            y_range=[-50, 50, 10],
            x_length=9,
            y_length=5,
            axis_config={"color": BLUE},
        )
        axes_labels = axes.get_axis_labels(x_label="Flips", y_label="Score")

        # Prepare the table
        table = (
            Table(
                [["Simulation", "Above 0"]],
                col_labels=[Text("Sim #"), Text("% Time Above 0")],
                include_outer_lines=True,
            )
            .scale(0.5)
            .to_corner(UR)
        )

        self.add(axes, axes_labels, table)

        simulations_to_run = 5  # Number of simulations
        for simulation_number in range(1, simulations_to_run + 1):
            score = 0
            times_above_0 = 0
            line = VMobject(color=RED)
            # line.set_points_as_corners([axes.c2p(0, score)])
            line.start_new_path(
                axes.c2p(0, score)
            )  # Start the line at the initial score

            for flip in range(1, 101):
                flip_result = random.choice([1, -1])
                score += flip_result
                if score > 0:
                    times_above_0 += 1

                new_point = axes.c2p(flip, score)
                line.add_points_as_corners([new_point])
                if flip == 100:  # Update at the end of each simulation
                    self.play(
                        Create(line),
                        run_time=2,
                        rate_func=linear,
                    )
                    # Update table
                    # table.add_row(
                    #    [f"{simulation_number}", f"{times_above_0}%"],
                    #    cell_style={"font_size": 24},
                    # )
                    # self.play(Write(table))
                    # if simulation_number > 1:
                    # self.play(line.animate.set_opacity(0.2))
                    self.play(FadeOut(line))

        self.wait()


class TestTex(Scene):
    def construct(self):

        text3 = MathTex(
            r"\begin{bmatrix} f(\epsilon_1) |\ f(\epsilon_2) \end",
            color=BLUE,
            font_size=120,
        )
        self.play(Write(text3), runtime=5)
        self.wait(5)
        self.play(FadeOut(text3))


class CoinFlipSimulationWithHistogram(Scene):
    def initiate(self):
        self.num_simulations = 200
        self.histogram_count = [0] * 10
        self.simulation_axes, self.zero_line = self.construct_time_series_axes()
        self.histogram_axes, self.hist_x_axis_labels = self.construct_histogram_axes()
        self.proportion_text = Text(
            "% time  spent  in  the  positive  region: ", font_size=22
        ).next_to(self.simulation_axes, UP, buff=0.5)
        self.proportion = Integer(0, font_size=26).next_to(
            self.proportion_text, RIGHT, buff=0.5
        )
        self.proportion_unit = Text("/ 100", font_size=22).next_to(
            self.proportion, RIGHT, buff=0.3
        )
        self.path = VMobject(color=RED)

    def construct_time_series_axes(self):
        axes = Axes(
            x_range=[0, 110, 20],
            y_range=[-30, 30, 5],
            x_length=6,
            y_length=4,
            axis_config={"color": BLUE},
            tips=False,
            x_axis_config={"include_numbers": True, "font_size": 26},
            y_axis_config={"include_numbers": True, "font_size": 26},
        ).to_edge(LEFT, buff=0.5)

        flip_label = Text("# Coin Flips", font_size=20).next_to(axes, DOWN, buff=0.5)
        score_label = (
            Text("Score", font_size=20)
            .next_to(axes.y_axis, LEFT, buff=0.5)
            .rotate(90 * DEGREES)
        )

        shift_amount = axes.y_length / 2  # Shift down by half the height of the axes

        # Apply the shift to the axes
        axes.x_axis.shift(DOWN * shift_amount)

        zero_line = Line(
            start=axes.c2p(0, 0), end=axes.c2p(100, 0), color=WHITE, stroke_width=2
        )
        axes.add(flip_label, score_label)

        # Example of adding a label for the y-axis at a specific position
        return axes, zero_line

    def construct_histogram_axes(self):
        axes = Axes(
            x_range=[0, 1, 0.1],
            y_range=[0, 12, 1],
            x_length=6,
            y_length=4,
            axis_config={"color": BLUE},
            tips=False,
        ).to_edge(RIGHT, buff=0.5)

        x_axis_nums = VGroup()
        for i in range(1, 11):
            num = (
                MathTex("\\frac{%3d}{10}" % i)
                .scale(0.6)
                .next_to(axes.x_axis.n2p((i - 1) / 10 + 0.05), DOWN, buff=0.1)
            )
            x_axis_nums.add(num)

        proportion_label = Text("# Positive / 100", font_size=20).next_to(
            x_axis_nums, DOWN, buff=0.1
        )
        count_label = (
            Text("Count", font_size=20)
            .next_to(axes.y_axis, LEFT, buff=0.1)
            .rotate(90 * DEGREES)
        )

        axes.add(proportion_label, count_label)
        return axes, x_axis_nums

    def construct(self):
        self.initiate()
        self.play(
            LaggedStart(
                Create(self.simulation_axes),
                FadeIn(self.zero_line),
                Create(self.histogram_axes),
                *[FadeIn(num) for num in self.hist_x_axis_labels],
                Create(self.proportion_text),
                Create(self.proportion_unit),
                lag_ratio=0.5,
                run_time=2,
            )
        )

        self.run_simulations()

    def run_simulations(self):
        for i in range(self.num_simulations):
            # Simulate coin flips and display on the simulation axes
            self.simulate_path(i)
            if i < 5:
                self.wait(0.1)  # Wait between updates for clarity
            self.path.clear_points()

        self.wait(5)

    def simulate_path(self, curr_iter):
        if curr_iter < 5:
            runtime = 1
        else:
            runtime = 0.1

        score = 0
        positive_count = 0  # Number of flips where score is positive
        # proportion_text = Text("% time  spent  in  the  positive  region: ", font_size=20).next_to(simulation_axes, UP, buff=0.5)
        # proportion = DecimalNumber(0, num_decimal_places=2, font_size=20).next_to(proportion_text, RIGHT, buff=0.5)
        # path = VMobject(color=RED)

        self.path.start_new_path(self.simulation_axes.c2p(0, 0))
        for flip in range(1, 101):
            result = random.choice([-1, 1])
            score += result
            if score > 0:
                positive_count += 1

            new_point = self.simulation_axes.c2p(flip, score)
            self.path.add_points_as_corners([new_point])

        # Fill in the regrion betwen the path and the Axes
        # fill only the positive region
        # polygons, pos, neg = self.fill_path(self.path)
        polygons = self.highlight_positive_segments(self.simulation_axes, self.path)

        self.proportion.set_value(positive_count)
        # porportion_box = SurroundingRectangle(proportion.copy()).move_to(histogram_axes, UP)

        self.play(Create(VGroup(self.path, polygons)), run_time=runtime)
        # self.play(porportion_box.animate.move_to(histogram_axes, UP))

        self.play(
            Transform(polygons, self.proportion),
            # FadeIn(self.proportion),
            run_time=runtime,
        )

        # moved_proportion = self.proportion.copy()
        proportion_histogram_box = SurroundingRectangle(
            # moved_proportion,
            VGroup(self.proportion, self.proportion_unit),
            stroke_color=WHITE,
            stroke_width=0.2,
            fill_color=BLUE,
            fill_opacity=0.5,
            buff=0.1,
        )

        histogram_box_group = VGroup(proportion_histogram_box)
        self.play(DrawBorderThenFill(proportion_histogram_box), run_time=runtime)

        num_index = int(np.floor(positive_count / 10))
        if num_index == 10:
            num_index = 9

        histogram_box_width = 0.60
        histogram_box_height = 0.1
        self.histogram_count[num_index] += 1

        moved_box = (
            Rectangle(
                width=histogram_box_width,
                height=histogram_box_height,
                fill_color=BLUE,
                fill_opacity=0.5,
                stroke_width=0,
            )
            .next_to(self.hist_x_axis_labels[num_index], UP, buff=0)
            .shift(self.histogram_count[num_index] * histogram_box_height * UP)
        )
        self.play(
            Transform(histogram_box_group, moved_box),
            Create(moved_box),
            FadeOut(self.path),
            FadeOut(polygons),
            FadeOut(self.proportion),
            # FadeOut(self.moved_proportion),
            run_time=runtime,
        )

    def highlight_positive_segments(self, axes, path):
        points = path.get_points()
        was_positive = False
        start_positive = None

        highlight_lines = []
        for i, point in enumerate(points):
            x, y = axes.p2c(point)[:2]
            is_positive = y > 0

            # Check if the path crosses the x-axis
            if is_positive and not was_positive:
                start_positive = x  # Mark the start of a positive segment
            elif was_positive and not is_positive and start_positive is not None:
                # Path was positive and now crosses back below the x-axis
                hline = self.draw_highlight_line(axes, start_positive, x)
                start_positive = None  # Reset for the next positive segment
                highlight_lines.append(hline)

            was_positive = is_positive

        # If the path ends while still positive, draw highlight to the end
        if was_positive and start_positive is not None:
            hline = self.draw_highlight_line(axes, start_positive, x)
            highlight_lines.append(hline)

        return VGroup(*highlight_lines)

    def draw_highlight_line(self, axes, start_x, end_x):
        start_point = axes.c2p(start_x, 0)
        end_point = axes.c2p(end_x, 0)
        line = Line(start_point, end_point, color=YELLOW, stroke_width=8)
        return line

    def fill_path(self, path):
        # Get the points from the path
        points = path.get_points()
        poligons = []
        positive_polygons = []
        negative_polygons = []
        # Iterate through points to create filled areas
        for i in range(len(points) - 1):
            start_point = points[i]
            end_point = points[i + 1]

            # Determine points on the x-axis directly below start and end points
            start_point_on_axis = np.array([start_point[0], 0, 0], dtype=float)
            end_point_on_axis = np.array([end_point[0], 0, 0], dtype=float)

            # Create a polygon to fill between the path and the x-axis
            if start_point[1] > 0 and end_point[1] > 0:  # Both points above x-axis
                polygon = Polygon(
                    start_point,
                    end_point,
                    end_point_on_axis,
                    start_point_on_axis,
                    color=RED,
                )
                polygon.set_fill(RED, opacity=0.3)
                poligons.append(polygon)
                positive_polygons.append(polygon)
            elif start_point[1] < 0 and end_point[1] < 0:  # Both points below x-axis
                polygon = Polygon(
                    start_point,
                    end_point,
                    end_point_on_axis,
                    start_point_on_axis,
                    color=GREEN,
                )
                polygon.set_fill(GREEN, opacity=0.3)
                poligons.append(polygon)
                negative_polygons.append(polygon)

        return VGroup(*poligons), VGroup(*positive_polygons), VGroup(*negative_polygons)
