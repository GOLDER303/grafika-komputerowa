#!/usr/bin/env python3
import random
import sys
from math import cos, pi, sin
from typing import Any

from glfw.GLFW import (
    glfwCreateWindow,
    glfwGetTime,
    glfwInit,
    glfwMakeContextCurrent,
    glfwPollEvents,
    glfwSetFramebufferSizeCallback,
    glfwSwapBuffers,
    glfwSwapInterval,
    glfwTerminate,
    glfwWindowShouldClose,
)
from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_FLAT,
    GL_LINES,
    GL_MODELVIEW,
    GL_POINTS,
    GL_PROJECTION,
    GL_SMOOTH,
    GL_TRIANGLE_STRIP,
    GL_TRIANGLES,
    glBegin,
    glClear,
    glClearColor,
    glColor3f,
    glEnable,
    glEnd,
    glFlush,
    glLoadIdentity,
    glMatrixMode,
    glOrtho,
    glRotatef,
    glShadeModel,
    glVertex,
    glVertex3f,
    glViewport,
)

Vertex = tuple[float, float, float]
Color = tuple[float, float, float]


N = 25
tab: list[list[list[float]]] = [[[0] * 3 for _ in range(N)] for _ in range(N)]
colors: list[list[Color]] = [
    [(random.random(), random.random(), random.random()) for _ in range(N)]
    for _ in range(N)
]


def startup():
    update_viewport(None, 400, 400)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH) 

    buildMountain()

    for i in range(N):
        for j in range(N):
            u = i / (N - 1)
            v = j / (N - 1)

            x, y, z = eggFunction(u, v)

            tab[i][j] = [x, y, z]


def shutdown():
    pass


def axes():
    glBegin(GL_LINES)

    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-5.0, 0.0, 0.0)
    glVertex3f(5.0, 0.0, 0.0)

    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, -5.0, 0.0)
    glVertex3f(0.0, 5.0, 0.0)

    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, -5.0)
    glVertex3f(0.0, 0.0, 5.0)

    glEnd()


def spin(angle: float):
    glRotatef(angle, 1.0, 0.0, 0.0)
    glRotatef(angle, 0.0, 1.0, 0.0)
    glRotatef(angle, 0.0, 0.0, 1.0)


def update_viewport(window: Any, width: float, height: float):
    if width == 0:
        width = 1
    if height == 0:
        height = 1
    aspect_ratio = width / height

    glMatrixMode(GL_PROJECTION)
    glViewport(0, 0, width, height)
    glLoadIdentity()

    if width <= height:
        glOrtho(-7.5, 7.5, -7.5 / aspect_ratio, 7.5 / aspect_ratio, 7.5, -7.5)
    else:
        glOrtho(-7.5 * aspect_ratio, 7.5 * aspect_ratio, -7.5, 7.5, 7.5, -7.5)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def eggFunction(u: float, v: float) -> Vertex:
    return (
        (-90 * u**5 + 225 * u**4 - 270 * u**3 + 180 * u**2 - 45 * u) * cos(pi * v),
        160 * u**4 - 320 * u**3 + 160 * u**2 - 5,
        (-90 * u**5 + 225 * u**4 - 270 * u**3 + 180 * u**2 - 45 * u) * sin(pi * v),
    )


MOUNTAIN_SIZE: float = 10.0
MOUNTAIN_HEIGHT_SCALE: float = 25.0
MOUNTAIN_GRID: int = 80
WEIERSTRASS_EXPONENT: int = 2
WEIERSTRASS_TERMS: int = 20

mountainPoints: list[list[Vertex]] = []
mountainColors: list[list[Vertex]] = []


def weierstrass(position: float, exponent: int, terms: int) -> float:
    total = 0.0
    for k in range(1, terms + 1):
        frequency = k**exponent
        total += sin(pi * frequency * position) / (pi * frequency)
    return total


def buildMountain() -> None:
    mountainPoints.clear()
    mountainColors.clear()

    heights: list[list[float]] = []

    for row in range(MOUNTAIN_GRID):
        heightsRow: list[float] = []

        for column in range(MOUNTAIN_GRID):
            u = row / (MOUNTAIN_GRID - 1)
            v = column / (MOUNTAIN_GRID - 1)

            height = weierstrass(
                u, WEIERSTRASS_EXPONENT, WEIERSTRASS_TERMS
            ) * weierstrass(v, WEIERSTRASS_EXPONENT, WEIERSTRASS_TERMS)

            heightsRow.append(height)

        heights.append(heightsRow)

    maxHeight = max(max(heightsRow) for heightsRow in heights)

    for row in range(MOUNTAIN_GRID):
        pointsRow: list[Vertex] = []
        colorsRow: list[Vertex] = []

        for column in range(MOUNTAIN_GRID):
            x = (row / (MOUNTAIN_GRID - 1) - 0.5) * MOUNTAIN_SIZE
            z = (column / (MOUNTAIN_GRID - 1) - 0.5) * MOUNTAIN_SIZE

            height = heights[row][column]
            pointsRow.append((x, height * MOUNTAIN_HEIGHT_SCALE, z))

            brightness = height / maxHeight
            colorsRow.append((brightness, 0.3 + 0.6 * brightness, 0.3 * brightness))

        mountainPoints.append(pointsRow)
        mountainColors.append(colorsRow)


def drawMountain() -> None:
    for row in range(MOUNTAIN_GRID - 1):
        glBegin(GL_TRIANGLE_STRIP)

        for column in range(MOUNTAIN_GRID):
            glColor3f(*mountainColors[row][column])
            glVertex3f(*mountainPoints[row][column])

            glColor3f(*mountainColors[row + 1][column])
            glVertex3f(*mountainPoints[row + 1][column])

        glEnd()


def drawEggPoints() -> None:
    glBegin(GL_POINTS)

    for i in range(N):
        for j in range(N):
            glVertex3f(*tab[i][j])

    glEnd()


def drawEggLines() -> None:
    glBegin(GL_LINES)

    for i in range(N - 1):
        for j in range(N - 1):
            glVertex3f(*tab[i][j])
            glVertex3f(*tab[i + 1][j])

            glVertex3f(*tab[i][j])
            glVertex3f(*tab[i][j + 1])

    glEnd()


def drawEggTriangles() -> None:
    glBegin(GL_TRIANGLES)

    for i in range(N - 1):
        for j in range(N - 1):
            glColor3f(*colors[i][j])
            glVertex3f(*tab[i][j])
            glColor3f(*colors[i + 1][j])
            glVertex3f(*tab[i + 1][j])
            glColor3f(*colors[i][j + 1])
            glVertex3f(*tab[i][j + 1])

            glColor3f(*colors[i + 1][j + 1])
            glVertex3f(*tab[i + 1][j + 1])
            glColor3f(*colors[i + 1][j])
            glVertex3f(*tab[i + 1][j])
            glColor3f(*colors[i][j + 1])
            glVertex3f(*tab[i][j + 1])

    glEnd()


def drawEggStrip() -> None:
    for i in range(N - 1):
        glBegin(GL_TRIANGLE_STRIP)
        for j in range(N):
            glColor3f(*colors[i][j])
            glVertex3f(*tab[i][j])

            glColor3f(*colors[i + 1][j])
            glVertex3f(*tab[i + 1][j])

        glEnd()


def render(time: float):
    glClear(
        GL_COLOR_BUFFER_BIT
        | GL_DEPTH_BUFFER_BIT  # pyright: ignore[reportOperatorIssue]
    )
    glLoadIdentity()

    spin(time * 180 / 3.1415)

    axes()

    # drawEggPoints()
    # drawEggLines()
    # drawEggTriangles()
    # drawEggStrip()

    drawMountain()

    glFlush()


def main():
    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(400, 400, __file__, None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    glfwMakeContextCurrent(window)
    _ = glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSwapInterval(1)

    startup()
    while not glfwWindowShouldClose(window):
        render(glfwGetTime())
        glfwSwapBuffers(window)
        glfwPollEvents()
    shutdown()

    glfwTerminate()


if __name__ == "__main__":
    main()
